from functions import request_coinmarketcap, request_coingreko
import os
import gspread
from gspread_dataframe import set_with_dataframe
from dotenv import load_dotenv

class Coins:

    def __init__(self, mode = True):
        #Adding the mode defines if we extract data from Coinmarketcap(false) or Coingeko(true). 
        # Default = Coingeko
        #Loading the secret variables 
        load_dotenv()

        self.mode = mode

    # With this function, we retrieve the current price of the best ranked and first 50000 coins from Coinmarketcap
    def extraction(self):

        if self.mode == False:
            #The output is a dataframe with two columns
            self.crypto_prices = request_coinmarketcap()


        if self.mode == True:
            #The output is a dataframe with two columns coin_name and price_name
            self.crypto_prices = request_coingreko()



    #This function stores the dataframe in Google Spreadsheet so then we can manage our portfolio easily
    def upload(self):
        print("Updating everything in Google Spreadsheet")
        #Credentials for accessing to Google API
        id_keys = 'credentials.json'
        gc = gspread.service_account(filename = id_keys)

        # We access in the spreadsheet where we want to store the values        
        sh = gc.open_by_key(f'{os.getenv("SPREADSHEET_ID")}')
        worksheet = sh.get_worksheet(1) # 0 is the first sheet, 1 is the second sheet, etc.  

        # With this line, we send the data each time we execute the function
        set_with_dataframe(worksheet, self.crypto_prices)
        print("The End!")


        
