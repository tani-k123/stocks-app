import csv  #csv writes list of dictionaries
import os

from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

import json
import pdb   #allows running of small sections of code to test
import requests
from IPython import embed
import datetime

def parse_response(response_text):
    # response_text can be either a raw JSON string or an already-converted dictionary
    # pdb.set_trace() #stops running script from further than the parse_reponse function
    if isinstance(response_text, str): # if response_text variable is string then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results #return list of dictionaries

def write_prices_to_file(prices=[], filename="db/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"], # change attribute name to match project requirements
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
        writer.writerow(row)

#load_dotenv() # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable

# see: https://www.alphavantage.co/support/#api-key
#api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

#symbol = "NFLX" #TODO: capture user input

# see: https://www.alphavantage.co/documentation/#daily
# TODO: assemble the request url to get daily data for the given stock symbol

# TODO: issue a "GET" request to the specified url, and store the response in a variable

# TODO: parse the JSON response

#latest_price_usd = "$100,000.00" # TODO: traverse the nested response data structure to find the latest closing price

#print(f"LATEST DAILY CLOSING PRICE FOR {symbol} IS: {latest_price_usd}")

# TODO: configure environment variables

if __name__ == '__main__': # only execute if file invoked from the command-line, not when imported into other files, like tests

    load_dotenv() # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable

    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."
    #print (api_key)

    # CAPTURE USER INPUTS (SYMBOL)
    symbol = "NFLX" # input("Please input a stock symbol (e.g. 'NFLX'): ")
    symbol = input ("Please input a stock symbol (e.g. 'NFLX'): ")

    #converted_symbol = float (symbol)
    #if isinstance (converted_symbol, float):
    #    print ("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR STOCK SYMBOL.")
    #    quit ("Stopping the program")

    # VALIDATE SYMBOL AND PREVENT UNECESSARY REQUESTS
    try:
        float (symbol)
        print ("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR STOCK SYMBOL.")
        quit ("Stopping the program")
    except ValueError as e: #Exception is used nonspecifcally for all types of errors
        pass

    # ASSEMBLE REQUEST URL
    # ... see: https://www.alphavantage.co/support/#api-key
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    # f"..." is string interpolation vs. string cancatnation

    # ISSUE "GET" REQUEST
    response = requests.get(request_url)    # url returns object as dictionary

    # VALIDATE RESPONSE AND HANDLE ERRORS
    # ... todo
    if "Error Message" in response.text:
        print ("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR STOCK SYMBOL.")
        quit ("Stopping the program")
        # else

    # PARSE RESPONSE (AS LONG AS THERE ARE NO ERRORS)
    daily_prices = parse_response(response.text)

    # WRITE TO CSV
    write_prices_to_file(prices=daily_prices, filename="db/prices.csv")

    response_body = json.loads(response.text)
    #response.text: turns response data into string
    # x.loads turns above string data into python friendly data and dictionary

    # traverse the nested response data structure to find the latest info
    metadata = response_body ["Meta Data"]
    data = response_body ["Time Series (Daily)"]
    dates = list (data) #convert dictionary into list of dates
    #print (dates)

    # PERFORM CALCULATIONS
    # ... todo (HINT: use the daily_prices variable, and don't worry about the CSV file anymore :-)

    # PRODUCE FINAL RECOMMENDATION
    # ... todo
    latest_daily_data = data[dates[1]]

    latest_price = latest_daily_data ["4. close"]
    latest_price = float (latest_price)
    latest_price_usd = "${0:,.2f}".format(latest_price)
    trade_date = dates [0]
    print (f"Latest Daily Closing Price For {symbol} Is: {latest_price_usd}")

    time_data = datetime.datetime.now()
    print ("Time of execution: " + time_data.strftime("%A, %B %d, %Y at %I:%M %p"))

    print ("Latest Data from: " + trade_date)

    avg_price = daily_prices[0:100]

    max_price = []
    for data in avg_price:
        max_price.append(float(data["high"]))
    avg_high_price = max (max_price)
    print ("Maximum of daily high averages: " + str(avg_high_price))

    min_price = []
    for data in avg_price:
        min_price.append(float(data["low"]))
    avg_low_price = min (min_price)
    print ("Minimum of daily low averages: " + str(avg_low_price))

    if latest_price >= avg_high_price:
        print ("Don't Buy because price too high and likely to autocorrect.")
    elif avg_high_price >= latest_price > avg_low_price:
        print ("Buy as price is likely to climb.")
    elif latest_price <= 0.7 * (float (avg_low_price)):
        print ("Don't Buy because historically low prices.")
    else:
        print ("Buy as price may climb given. Assess company prospectus")
