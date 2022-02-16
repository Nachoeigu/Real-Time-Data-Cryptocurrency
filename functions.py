from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
import requests
import pandas as pd
from dotenv import load_dotenv
import os
import datetime


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

def request_coingreko():
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.87 Safari/537.36'}
    coin = []
    current_price = []

    #We request for the current price of the first 32 pages in Coingreko
    for number in range(1,32):
        time.sleep(3)
        data = requests.get(f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={number}&sparkline=false', headers = headers)
        data = json.loads(data.content)
        for item in data:
            symbol = item['symbol'].lower()
            current_prices = item['current_price']
            
            #If we don´t know the price of that token, add to it 0
            if current_prices == None:
                current_price.append(0)
                coin.append(symbol)
            
            else:
                current_prices = float(current_prices)

                #For readibility, we round in case the price is higher than 50 USD
                if current_prices > 50:
                    current_prices = round(current_prices, 0)

                #For readibility, we keep the first two decimals in case the price is lower than 50 USD but higher than 10 USD
                elif (current_prices <= 50) & (current_prices >= 10):
                    current_prices = round(current_prices, 2)

                #For readibility, we keep all the decimals in case the price is lower than 10 USD
                else:
                    current_prices = round(current_prices, 10)

                coin.append(symbol)
                current_price.append(current_prices)
    
    #We create the dataframe with the ouput of the for loop
    print("Creating the dataframe with the data from Coingecko")
    crypto_prices = pd.DataFrame({'coin_name':coin,
                'coin_price':current_price})

    #We add the information about the time we made the last update
    crypto_prices['last_update'] = datetime.datetime.today().strftime("%d-%b-%Y (%H:%M)")

    return crypto_prices
