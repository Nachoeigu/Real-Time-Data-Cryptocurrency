from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
import requests
import pandas as pd
from dotenv import load_dotenv
import os
import datetime
import gspread
from difflib import SequenceMatcher


def request_coinmarketcap():
        #Loading the secret variables 
        load_dotenv()

        #URL which we will request the information
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        
        #With this parameter, we retrieve the first 5000 coins
        parameters =  {
            'start': '1',
            'limit': '5000',
            'convert':'USD'
            }

        #With the headers, we request the information in json format
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': f'{os.getenv("API_KEY_COINMARKETCAP")}',
            }

        #We build a session in order to scrape the data
        session = Session()
        session.headers.update(headers)

        #Making the request: the output of this phase is a json file
        try:
            response = session.get(url, params=parameters)
            print("Making the request to the Coinmarketcap page")
            data = json.loads(response.text)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
        
        #The variables where we will hold the values
        coin_name = []
        coin_price = []
        
        #Measuring the amount of coins we see in the response
        length = len(data["data"])

        #With this loop, we get the price and name of each coin
        print("Extracting the price of each token in Coinmarketcap")
        for n_coin in range(0,length):
            price = float(data["data"][n_coin]["quote"]["USD"]["price"])

            #For readibility, we round in case the price is higher than 50 USD
            if price > 50:
                price = round(price, 0)

            #For readibility, we keep the first two decimals in case the price is lower than 50 USD but higher than 10 USD
            elif (price <= 50) & (price >= 10):
                price = round(price, 2)

            #For readibility, we keep all the decimals in case the price is lower than 10 USD
            else:
                price = round(price, 10)

            name = (data["data"][n_coin]["symbol"]).lower()

            coin_price.append(price)
            coin_name.append(name)

        #We create the dataframe with the ouput of the for loop
        print("Creating the dataframe with the data from Coinmarketcap")
        crypto_prices = pd.DataFrame(list(zip(coin_name, coin_price)), columns = ['coin_name', 'coin_price'])
        
        #We add the information about the time we made the last update
        crypto_prices['last_update'] = datetime.datetime.today().strftime("%d-%b-%Y (%H:%M)")

        return crypto_prices

def needed_coins_from_spreadsheets():
    #We need to retrieve the needed coins from Google Spreadsheets so we can find the current price of those specific coins

    load_dotenv()

    #We obtain a list with all the IDS
    spreadsheets_ids = [os.getenv('SPREADSHEET_ID')]
    
    # Conection with Google API
    gc = gspread.service_account(filename = 'credentials.json') 
    
    #We interact with each spreadsheet in order to know the unique coins
    needed_coins_symbols = []
    needed_coins_names = []
    
    print("Obtaining the needed coins from Google Spreadsheets")
    for spreadsheet in spreadsheets_ids:
        sh = gc.open_by_key(spreadsheet) 
        worksheet = sh.get_worksheet(0)
        #First we extract the symbols
        values_list = worksheet.col_values(3)
        coins = values_list[1:]

        for each_coin in coins:
            if each_coin in needed_coins_symbols:
                continue
            else:
                needed_coins_symbols.append(each_coin.lower())

        #We extract the name of those coins because there are cases with the same symbol (mng is one example of this)
        values_list = worksheet.col_values(4)
        coins = values_list[1:]

        for each_coin in coins:
            if each_coin in needed_coins_names:
                continue
            else:
                needed_coins_names.append(each_coin.lower())

    return needed_coins_symbols, needed_coins_names

def string_matching(first_string, second_string):
    if (SequenceMatcher(None, first_string, second_string).ratio()) > 0.6:
        return True
    else:
        return False

def request_coingreko():
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36'}

    #We obtain the coin names we should obtain its price from Google Spreadsheet
    needed_coins_in_symbols, needed_coins_names = needed_coins_from_spreadsheets()

    #We have the needed coins in symbol format, we need to have them in name format in order to obtain its price, so we create this variable with the symbols and names:
    print("Trying to find the name of each symbol we extract from Google Spreadsheets")
    data = requests.get('https://api.coingecko.com/api/v3/coins/list')
    data = json.loads(data.content)

    coin_names_from_coingeko = []
    for index in range(0,len(needed_coins_in_symbols)):
        for symbol in data:
            target_symbol = symbol['symbol'].lower()
            target_name = symbol['name'].lower().replace('-',' ')
            
            #We make a double validation: First by symbol, and second by name
            if (target_symbol == needed_coins_in_symbols[index]) & (string_matching(target_name, needed_coins_names[index])):
                coin_names_from_coingeko.append(symbol['name'].replace(' ','-').lower().strip())
                break
    
    coin = []
    price = []
    print("Obtaining the price of each coin")
    #We request for the current price of the needed coins
    for index in range(0,len(coin_names_from_coingeko)):
        time.sleep(2)
        data = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin_names_from_coingeko[index]}&vs_currencies=usd", headers = headers)
        data = json.loads(data.content)
        current_price = data[coin_names_from_coingeko[index]]['usd']
        try:
            current_price = float(current_price)
            #I NEED TO FIND A WAY TO CONVERT NOTATION SCIENTIFIC NUMBER TO FLOAT

        except:
            coin.append(needed_coins_in_symbols[index])
            price.append('')
            continue

        #For readibility, we round in case the price is higher than 50 USD
        if current_price > 50:
            current_price = round(current_price, 0)

        #For readibility, we keep the first two decimals in case the price is lower than 50 USD but higher than 10 USD
        elif (current_price <= 50) & (current_price >= 10):
            current_price = round(current_price, 2)

        #For readibility, we keep all the decimals in case the price is lower than 10 USD
        else:
            current_price = round(current_price, 10)
        coin.append(needed_coins_in_symbols[index])
        price.append(current_price)
    
    #We create the dataframe with the ouput of the for loop
    print("Creating the dataframe with the data from Coingecko")
    crypto_prices = pd.DataFrame({'coin_name':coin,
                'coin_price':price})
    print(crypto_prices)
    #We add the information about the time we made the last update
    crypto_prices['last_update'] = datetime.datetime.today().strftime("%d-%b-%Y (%H:%M)")

    return crypto_prices
