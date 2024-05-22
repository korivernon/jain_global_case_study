import pandas as pd
from flask import Flask, render_template, request
import yfinance as yf
from datetime import datetime
import traceback
import pprint

##### LOGGER SETUP ######
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

##### CONSTANTS ######
DATE_FORMAT = "%Y-%m-%d"
NASDAQ_LISTED = 'nasdaq_listed.psv'
OTHER_LISTED = 'other_listed.psv'

##### INIT FLASK APP #####
app = Flask(__name__)

##### HELPER FUNCTIONS #####
def fetch_symbols(file):
    """
    Fetch a list of all of the US Symbols - note this was downloaded from:
    https://ftp.nasdaqtrader.com/Trader.aspx?id=symbollookup
    :return: [str]
    """
    with open(file, 'r') as f:
        lines = f.readlines()
    # tickers = [",".split(line) for line in lines]
    tickers = []
    for line in lines[1:-1]: #cut off timestamp of file
        line = line.strip('\n').split('|')
        tickers.append(line[0])
    return tickers
NASDAQ_LISTED_SYMBOLS = fetch_symbols(NASDAQ_LISTED)
OTHER_LISTED_SYMBOLS = fetch_symbols(OTHER_LISTED)
us_symbols = []
us_symbols.extend(NASDAQ_LISTED_SYMBOLS)
us_symbols.extend(OTHER_LISTED_SYMBOLS)

def ticker_returns_matrix(
        ticker: str,
        start_date: str,
        end_date: str
    ):
    """
    Return a dataframe that contains the date and the returns
    :param ticker: valid ticker
    :param start_date: start date that is less than the end date
    :param end_date: end date that is greater than the start date
    :return: pd.Dataframe()
    """
    try:
        yf.Ticker(ticker)
    except Exception as e:
        msg = f'Unable to fetch ticker: {ticker}\n{traceback.format_exc()}'
        logger.error(msg)
        raise Exception(msg)
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Returns'] = data['Close'] - data['Open']
    data.index = data.index.strftime('%Y-%m-%d')
    data = data.reset_index()
    print(data)
    return data[['Date','Returns']]

def validate_dates(start_date, end_date):
    try:
        start = datetime.strptime(start_date, DATE_FORMAT)
        end = datetime.strptime(end_date, DATE_FORMAT)
        if end < start:
            raise Exception(f'Start date: {start_date} is greater than end date: {end}')
    except ValueError as e:
        raise e
    return True

def return_error(url: str,exception: Exception, msg: str=''):
    return {
        'url': url,
        'message': msg
    }


@app.errorhandler(404)
def page_not_found(error):
  return render_template('404.html'), 404

##### HOME PAGE #####
@app.route("/")
def index():
    return render_template('index.html')

##### ENDPOINTS #####
@app.route("/tickers", methods = ['GET'])
def tickers():
    """
    Return list of valid Tickers that the API supports
    :return:
    """
    return us_symbols

@app.route("/returns/<ticker>/<start_date>/<end_date>", methods = ['GET'])
def returns(ticker, start_date, end_date):
    """
    Returns a time series of the daily returns for the specified ticker and time horizon
    :return:
    """
    url = f'/returns/{ticker}/{start_date}/{end_date}'
    try:
        # first we want to validate the dates
        validate_dates(start_date, end_date)
        # after we validate dates we want to get the returns
        returns_df = ticker_returns_matrix(ticker, start_date, end_date)
    except Exception as e:
        msg = f'Error getting data from: {url}\n{traceback.format_exc()}'
        return return_error(url=url, exception=e, msg=msg)
    logger.info(f'Returns DF\n{returns_df}')
    return returns_df.to_dict(orient='records')

@app.route("/correlation/<ticker1>/<ticker2>/<start_date>/<end_date>", methods =['GET'])
def correlation(ticker1, ticker2, start_date, end_date):
    """
    Returns Pearson correlation coefficient between the daily return time series for the two
    provided tickers
    :return:
    """
    url = f'/correlation/{ticker1}/{ticker2}/{start_date}/{end_date}'
    try:
        validate_dates(start_date, end_date)
        # first we want to validate the dates
        # after we validate dates we want to get the returns
        returns_ticker_1 = ticker_returns_matrix(ticker1, start_date, end_date)
        returns_ticker_2 = ticker_returns_matrix(ticker2, start_date, end_date)
        if returns_ticker_2.shape[0] != returns_ticker_1.shape[0]:
            raise Exception('Please enter in tickers that have the same amount of historical data.')
        correlation = returns_ticker_1['Returns'].corr(returns_ticker_2['Returns'], method='pearson')
        correlation_coefficient_json = {
            'correlation_coefficient': correlation,
            'ticker_1': ticker1,
            'ticker_2': ticker2
        }
    except Exception as e:
        msg = f'Error getting data from: {url}\n{traceback.format_exc()}'
        return return_error(url=url, exception=e, msg=msg)
    logger.info(f'Correlation Coefficient JSON:\n{correlation_coefficient_json}')
    return correlation_coefficient_json

@app.route("/correlation_matrix/", methods = ['POST'])
def correlation_matrix():
    """
    Returns Pearson correlation coefficient matrix between the daily return time series for all
    of the provided tickers
    :return:
    """
    url = f'/correlation_matrix/'
    try:
        start_date = request.json['start_date']
        end_date = request.json['end_date']
        # first we want to validate the dates
        validate_dates(start_date, end_date)
        tickers = request.json['tickers']
        returns_df = pd.DataFrame()
        data_size = 0
        for i, ticker in enumerate(tickers):
            ticker_returns = ticker_returns_matrix(ticker, start_date, end_date)
            if i == 0:
                data_size = ticker_returns.shape[0]
            elif i > 0 and ticker_returns.shape[0] != data_size:
                raise Exception('Please enter in tickers that have the same amount of historical data.')
            returns_df[ticker] = ticker_returns['Returns']
        logger.info(returns_df)
        # after we validate dates we want to get the returns
        correlation_matrix = returns_df.corr(method='pearson')
        logger.info(f'Correlation Matrix:\n{correlation_matrix}')
        correlation_json = {
            'tickers': tickers,
            'correlation_matrix': correlation_matrix.to_dict(),
            }
        logger.info(correlation_json)
    except Exception as e:
        msg = f'Error getting data from: {url}\nWith JSON Request:{request.json}\n{traceback.format_exc()}'
        return return_error(url=url, exception=e, msg=msg)
    return correlation_json

def start():
    app.run(host='0.0.0.0', port=8002)

if __name__ == "__main__":
    start()