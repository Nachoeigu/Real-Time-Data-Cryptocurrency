from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
from dotenv import load_dotenv
import os
import gspread
from gspread_dataframe import set_with_dataframe

class Coins:

    def __init__(self):
        #Loading the secret variables
        load_dotenv()

        #URL which we will request the information
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        
        #With this parameter, we retrieve the first 5000 coins
        self.parameters =  {
            'start': '1',
            'limit': '5000',
            'convert':'USD'
            }

        #With the headers, we request the information in json format
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': f'{os.getenv("API_KEY_COINMARKETCAP")}',
            }

        #We build a session in order to scrape the data
        self.session = Session()
        self.session.headers.update(self.headers)

        #Making the request
        try:
            response = self.session.get(self.url, params=self.parameters)
            self.data = json.loads(response.text)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

    # With this function, we retrieve the current price of the best ranked and first 50000 coins from Coinmarketcap
    def extraction(self):
        coin_name = []
        coin_price = []
        
        #Measuring the amount of coins we see in the response
        length = len(self.data["data"])

        #With this loop, we get the price and name of each coin
        for n_coin in range(0,length):
            price = float(self.data["data"][n_coin]["quote"]["USD"]["price"])

            #For readibility, we round in case the price is higher than 50 USD
            if price > 50:
                price = round(price, 0)

            #For readibility, we keep the first two decimals in case the price is lower than 50 USD but higher than 10 USD
            elif (price <= 50) & (price >= 10):
                price = round(price, 2)

            #For readibility, we keep all the decimals in case the price is lower than 10 USD
            else:
                price = round(price, 10)

            name = (self.data["data"][n_coin]["symbol"]).lower()

            coin_price.append(price)
            coin_name.append(name)

        #We create the dataframe with the ouput of the for loop
        self.crypto_prices = pd.DataFrame(list(zip(coin_name, coin_price)), columns = ['coin_name', 'coin_price'])
        

    #This function stores the dataframe in Google Spreadsheet so then we can manage our portfolio easily
    def upload(self):
        #Credentials for accessing to Google API
        id_keys = 'credentials.json'
        gc = gspread.service_account(filename = id_keys)

        # We access in the spreadsheet where we want to store the values        
        sh = gc.open_by_key(f'{os.getenv("SPREADSHEET_ID")}')
        worksheet = sh.get_worksheet(1) # 0 is the first sheet, 1 is the second sheet, etc.  

        # With this line, we send the data each time we execute the function
        set_with_dataframe(worksheet, self.crypto_prices)
        


        
