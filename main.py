import requests
import pandas as pd
import time
from discord import Webhook, RequestsWebhookAdapter
from env import DISCORD_WEBHOOK_URL, DISCORD_LOG_WEBHOOK_URL

PRODUCTS_JSON_URL = 'https://finalmouse.com/products.json'
START_URL = 'https://finalmouse.com/collections/museum/products/'
has_found_new_product = False


def main():
    notify_discord_main("Starting up THE FINAL CRAWL!")
    product_handles = pd.read_csv('product-handles.csv')['handle']

    while True:
        start_time = time.time()
        df_products = init()

        if not has_found_new_product:
            df_products.apply(lambda p: check_if_new_product(product_handles, p), axis=1)

        df_products.apply(lambda p: check_stock(p), axis=1)
        end_time = time.time() - start_time
        notify_discord_log(
            "Check completed in {}ms".format(int(round(end_time, 3) * 1_000)))
        time.sleep(5)


def init():
    r = requests.get(PRODUCTS_JSON_URL)
    df_products = pd.json_normalize(r.json()['products'])
    df_products['variants'] = df_products['variants'].apply(lambda v: pd.json_normalize(v[0]))
    return df_products


def check_stock(product):
    if product['variants']['available'].bool():
        notify_discord_main("{} is IN STOCK at {}{}".format(product['title'], START_URL, product['handle']))


def check_if_new_product(product_handles, product):
    if not product_handles.str.contains(product['handle']).any():
        global has_found_new_product
        has_found_new_product = True
        notify_discord_main(
            "Discovered a new product called {} at {}{}".format(product['title'], START_URL, product['handle']))


def notify_discord_main(message):
    formatted_message = "[{}] {}".format(time.strftime("%H:%M:%S"), message)
    Webhook \
        .from_url(DISCORD_WEBHOOK_URL, adapter=RequestsWebhookAdapter()) \
        .send(formatted_message)
    notify_discord_log(message)


def notify_discord_log(message):
    formatted_message = "[{}] {}".format(time.strftime("%H:%M:%S"), message)
    print(formatted_message)
    Webhook \
        .from_url(DISCORD_LOG_WEBHOOK_URL, adapter=RequestsWebhookAdapter()) \
        .send(formatted_message)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        notify_discord_main("EXCEPTION: {}".format(e))
    finally:
        notify_discord_main("Shutting down THE FINAL CRAWL!")
