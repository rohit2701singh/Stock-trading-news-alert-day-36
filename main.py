import requests
import os
from twilio.rest import Client

account_sid = os.environ.get("ACCOUNT_SID_TWILIO")
auth_token = os.environ.get("AUTH_TOKEN_TWILIO")

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "country": "in",
    "apikey": "S62TWALLKGLIZXV7",
}

stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()
# print(stock_data)

data_last_refresh = stock_data["Meta Data"]["3. Last Refreshed"]  # format: "2023-10-06"
closing_data = stock_data["Time Series (Daily)"]

data_list = [value for (key, value) in closing_data.items()]
yesterday_closing_price = float(data_list[0]["4. close"])
day_before_closing_price = float(data_list[1]["4. close"])
print(f"yesterday closing: {yesterday_closing_price}, day before yesterday closing: {day_before_closing_price}")

closing_price_gap = (yesterday_closing_price - day_before_closing_price) / yesterday_closing_price
price_percent_change = round(closing_price_gap * 100, 4)
print(f"price gap: {closing_price_gap}, percentage change: {price_percent_change}")

if abs(price_percent_change) < 5:   # abs returns absolute value of a number
    news_parameters = {
        "q": COMPANY_NAME,
        "apiKey": "11xxxxxxxxxxxxxxxxxxxx9cdc",
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()["articles"][0:3]  # select top three news articles from list
    # print(news_data)

    for article in news_data:
        news_source = article["source"]["name"]
        news_title = article["title"]
        news_description = article["description"]
        # print(f"{news_title},\n{news_description} -->{news_source}")

        up_down = None
        if price_percent_change < 0:
            up_down = "🔻"
        else:
            up_down = "🔺"

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"{STOCK}: {up_down}{abs(price_percent_change)}%\nHeadlines: {news_title}\nBrief: {news_description} -{news_source}",
            from_='+125xxxxxxxx6',
            to='+9x8xxxxxxxxxx09',
        )
        print(message.status)
