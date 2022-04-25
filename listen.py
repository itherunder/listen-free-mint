

__author__ = "Zhou.Liao"

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, requests, json, yaml
from log import *

config_file, config = "config.yml", {}
meta = json.load(open("./meta.json", "r"))

event_types = {
    "transfer": True,
    "created": True,
    "successful": True,
    "cancelled": True,
    "bid_entered": True,
    "bid_withdrawn": True,
    "offer_entered": True,
    "approve": True,
}

query_transaction_url = {
    "ethereum": "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&apikey=%s&txhash=%s",
    "polygon": "https://api.polygon.io/v2/meta/blocks/latest?apiKey=%s"
}

def parse_config():
    global config
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    mail_to = config["mail"]["to"].split("#")
    config["mail"]["to"] = mail_to
    black_list = config["black_list"].split("#")
    config["black_list"] = {_.lower(): True for _ in black_list}
    # if config["etherscan_api_key"] == "":
    #     logger.error("Etherscan API key is empty")
    # if config["polygonscan_api_key"] == "":
    #     logger.error("Polygonscan API key is empty")
    if "api_key" not in config or "opensea" not in config["api_key"] or config["api_key"]["opensea"] == "":
        logger.error("Opensea API key is empty")
    if "params" not in config or "event_type" not in config["params"] or config["params"]["event_type"] not in event_types:
        logger.error("No parmas/event_type in config")
    if "mint_minimum" in config:
        config["mint_minimum"] = int(float(config["mint_minimum"]) * 10**18)
    else: config["mint_minimum"] = 0 # free mint

    logger.info("Config loaded %s", config)

def update_meta(last_event_id):
    meta["last_event_id"] = last_event_id
    with open("./meta.json", "w") as f:
        f.write(json.dumps(meta))

def send_mail(message, chain):
    if config["mail"]["from"] == "" or config["mail"]["pswd"] == "" or config["mail"]["to"] == []:
        logger.error("mail_from or password or mail_to is empty")
        return
    title = "free mint on %s!" % (chain)
    content = message
    logger.info("Sending mail %s, %s", title, content)
    # mail = MIMEMultipart()
    # mail.attach(MIMEText(content, "plain", "utf-8"))
    # mail["Subject"], mail["From"] = title, config["mail"]["from"]
    # s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    # s.login(config["mail"]["from"], config["mail"]["pswd"])
    # for _ in config["mail_to"]:
    #     s.sendmail(config["mail"]["from"], _, mail.as_string())

def listen_event():
    url = "https://api.opensea.io/api/v1/events"

    headers = {
        "Accept": "application/json",
        "X-API-KEY": config["api_key"]["opensea"]
    }

    response = requests.get(url, params=config["params"], headers=headers)
    if response.status_code != 200:
        logger.error("Request failed")
        return
    return json.loads(response.text)["asset_events"]

def handle_free_mint_event(event):
    permalink = event["asset"]["permalink"]
    contract = event["asset"]["asset_contract"]["address"].lower()
    chain = "ethereum"
    if "matic" in permalink:
        chain = "polygon"
    created_date = event["created_date"]
    logger.info("handle free mint event %s, %s, %s, %s, %s" % (event["id"], permalink, created_date, chain, contract))

    if "transaction" not in event or event["transaction"] is None:
        logger.error("No transaction in event")
        return
    transaction = event["transaction"]
    logger.debug("transaction %s", transaction)
    transaction_hash = transaction["transaction_hash"]
    response = requests.get(query_transaction_url[chain] % transaction_hash)
    if response.status_code != 200:
        logger.error("Request failed")
        return
    transaction = json.loads(response.text)["result"]
    if int(transaction["value"], 16) <= config["mint_minimum"]:
        send_mail("%s\n%s" % (permalink, created_date), chain)

def listen_free_mint():
    events = listen_event()
    events.sort(key=lambda x: x["id"])
    update_meta(events[-1]["id"])
    events = filter(lambda x: x["id"] > meta["last_event_id"], events)
    events = filter(lambda x: not x["is_private"] or x["is_private"] is None, events)
    events = filter(lambda x: x["asset"]["asset_contract"]["address"].lower() not in config["black_list"], events)
    events = list(events)
    for event in events:
        handle_free_mint_event(event)

def main():
    parse_config()
    listen_free_mint()

if __name__ == "__main__":
    main()
    # send_mail("hello world", "ethereum")