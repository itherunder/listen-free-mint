

__author__ = "Zhou.Liao"

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml, logging, smtplib, requests, asyncio, json

config_file, config = "config.yml", {}
meta = json.load(open("./meta.json", "r"))

def update_meta(last_event_id):
    meta["last_event_id"] = last_event_id
    with open("./meta.json", "w") as f:
        f.write(json.dumps(meta))

# before_block_number = {"ethereum": 0, "polygon": 0}
# block_number_url = {
#     "ethereum": "https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey=%s" % config["api_key.etherscan"],
#     "polygon": "https://api.polygon.io/v2/meta/blocks/latest?apiKey=%s" % config["api_key,polygonscan"]
# }

def parse_config():
    global config
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    mail_to = config["mail.to"].split("#")
    config["mail.to"] = mail_to
    black_list = config["black_list"].split("#")
    config["black_list"] = {_.lower(): True for _ in black_list}
    # if config["etherscan_api_key"] == "":
    #     logging.error("Etherscan API key is empty")
    # if config["polygonscan_api_key"] == "":
    #     logging.error("Polygonscan API key is empty")
    if config["api_key.opensea"] == "":
        logging.error("Opensea API key is empty")
    if "params.event_type" not in config:
        logging.error("No event_type in config")

    logging.info("Config loaded", config)

def send_mail(message, chain):
    if config["mail.from"] == "" or config["mail.pswd"] == "" or config["mail.to"] == []:
        logging.error("mail_from or password or mail_to is empty")
        return
    title = "free mint on %s!" % (chain)
    content = message
    mail = MIMEMultipart()
    mail.attach(MIMEText(content, "plain", "utf-8"))
    mail["Subject"], mail["From"] = title, config["mail_from"]
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(config["mail.from"], config["mail.pswd"])
    for _ in config["mail_to"]:
        s.sendmail(config["mail_from"], _, mail.as_string())

def listen_event():
    url = "https://api.opensea.io/api/v1/events"

    headers = {
        "Accept": "application/json",
        "X-API-KEY": config["opensea_api_key"]
    }

    response = requests.get(url, params=config["params"], headers=headers)
    if response.status_code != 200:
        logging.error("Request failed")
        return
    return json.loads(response.text)["asset_events"]

def listen_free_mint():
    events = listen_event()
    events.sort(key=lambda x: x["id"])
    events = filter(lambda x: x["id"] > meta["last_event_id"], events)
    events = filter(lambda x: not x["is_private"], events)
    events = filter(lambda x: x["asset"]["asset_contract"]["address"].lower() not in config["black_list"], events)
    update_meta(events[-1]["id"])

def main():
    parse_config()
    listen_event()

if __name__ == "__main__":
    main()
    # send_mail("hello world", "ethereum")