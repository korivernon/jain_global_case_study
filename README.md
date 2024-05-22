# jain_global_case_study
Objective: Develop a REST API that fetches, processes, and serves data relevant to an investment shop.

# Temporarily Deployed: http://jainglobal.korivernon.com:8002/

# Deliverables
1. Approach and Methodology
   2. My approach and initial methodology was to complete the overall tasks with the endpoints. As I have worked with yfinance before, I knew it would be difficult to get all of the tickers that the API supports. Knowing this, I decided to save this task for last as I thought that would take the most time.
   3. I tackled the returns first, as I knew that correlaiton and correlation matrix would be dependent on a base returns function. I created a function to fetch the returns by finding the difference between the open and close each day. I then converted the date to a human readable format so we can easily see what the price was on a given day. 
   4. Afterwards, I took a look at the correlation function and built out what would be required in order to find the pearson correlation coefficient for two provided tickers. I knew that this could be used as the baseline to find the correlation matrix, which was the next task. 
   5. When working on the correlation matrix functionality, I thought of a slight edge case-- there could be newly listed stocks that have different historical lenghts. If this was the case, I opted to immediately fail. The reason I opted to immediately fail is just personal preference. There could be a method of tackling this issue where if they have differing lengths of history, that we only calculate the correlation where all dates are the same.
   6. Lastly, I returned to the initial endpoint: tickers. After doing some research, I found a website that provides me the data that I'm looking for. While these symbols are not directly tested against yfinance, I could create a function to check each of the individual symbols. 

2. Assumptions Made
   1. There were a few assumptions made: first, I assumed that the start_date, and end_date would be passed into correlation matrix POST. This is because we need a time period in order to calculate the correlation for a given time series. 
   2. The next assumption I made was that we should expect the historical time periods to be the same across stocks. For example, we wouldn't be able to compare CAVA to Chipotle before CAVA's listing date because it doesn't have historical data. 

3. Challenges Faced
   1. Trying to find all available tickers for yfinance.

4. Potential Improvements
   1. Find the correlation between tickers and volatility so we can get a picture of what stocks may be correlated with one another. This could also grow to include the correlation across different sectors as well. Potentially being able to forecast and predict that a move would occur by finding stocks with similar volatility in T-1 days.
      1. For example, if Ticker 1 is highly correlated with Ticker 2 on T-1, but T-0 the volatility is not correlated at all, it could forecast a potential move in Ticker 2 (however, this does not imply direction).
   2. User interface

## Endpoints
-  GET /tickers
-  GET /returns/
-  GET /correlation
-  POST /correlation_matrix/

### GET /tickers
This endpoint returns a list of all of the tickers that the API supports. Note that this ticker data was pulled from an external yfinance source: https://ftp.nasdaqtrader.com/Trader.aspx?id=symbollookup

**Request**
There is no request body for this endpoint.

**Response**
The response is a JSON array of options symbols with positive dte.

``` [
    "AACG",
    "AACI",
    "AACIU",
    "AACIW",
      ...,
    "ZXIET"
]
```
### GET /returns
Returns a time series of the daily returns for the specified ticker and time horizon.

**Request**
There is no request body for this endpoint.

**Response**
The response is a JSON array of daily returns formatted as a float.

```commandline
[
    {
        "Date": "2024-04-04",
        "Returns": -1.4699859619140625
    },
    {
        "Date": "2024-04-05",
        "Returns": -0.0099945068359375
    },
    ...,
    {
        "Date": "2024-05-21",
        "Returns": 1.260009765625
    }
]
```
### GET /correlation
Returns the Pearson correlation coefficient between the daily return time series for the two provided tickers.

**Request**
There is no request body for this endpoint.

**Response**
The response is a JSON response with correlation_coefficient, which denotes the correlation coefficient, as well as the two tickers that were used. ticker_1 denotes ticker 1 and ticker_2 denotes ticker 2.

``` {
    "correlation_coefficient": 0.2582843917821114,
    "ticker_1": "aapl",
    "ticker_2": "tsla"
}
```
### POST /correlation_matrix
Get the latest volatility analysis for a given symbol. If no symbol is specified, the latest volatility analysis will be provided.

**Request**
```commandline
{
    "start_date": "2024-04-04",
    "end_date": "2024-05-22",
    "tickers": [
        "TSLA",
        "AAPL",
        "RIVN"
    ]
}
```
**Response**
The response is a JSON response with the correlation matrix.
```commandline
{
    "correlation_matrix": {
        "AAPL": {
            "AAPL": 1.0,
            "RIVN": -0.11900436280611904,
            "TSLA": 0.2582843917821113
        },
        "RIVN": {
            "AAPL": -0.11900436280611904,
            "RIVN": 1.0,
            "TSLA": 0.3365588296531417
        },
        "TSLA": {
            "AAPL": 0.2582843917821113,
            "RIVN": 0.3365588296531417,
            "TSLA": 1.0
        }
    },
    "tickers": [
        "TSLA",
        "AAPL",
        "RIVN"
    ]
}
```