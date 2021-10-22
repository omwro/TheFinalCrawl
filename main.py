import requests
import pandas as pd
import time
from discord import Webhook, RequestsWebhookAdapter
from env import DISCORD_WEBHOOK_URL

PRODUCTS_JSON_URL = 'https://finalmouse.com/products.json'
START_URL = 'https://finalmouse.com/collections/museum/products/'


def main():
    notify_discord("Starting up THE FINAL CRAWL!")
    while True:
        df_products = init()
        df_products.apply(lambda p: check_stock(p), axis=1)
        time.sleep(5)


def init():
    r = requests.get(PRODUCTS_JSON_URL)
    df_products = pd.json_normalize(r.json()['products'])
    df_products['variants'] = df_products['variants'].apply(lambda v: pd.json_normalize(v[0]))
    return df_products


def check_stock(product):
    if product['variants']['available'].bool():
        notify_discord("{} is IN STOCK at {}{}".format(product['title'], START_URL, product['handle']))


def notify_discord(message):
    Webhook.from_url(DISCORD_WEBHOOK_URL, adapter=RequestsWebhookAdapter()).send(message)


if __name__ == "__main__":
    main()
