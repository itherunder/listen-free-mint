

__author__ = "Zhou.Liao"

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml, logging, smtplib, requests

config_file, config = "config.yml", {}
before_block_number = {"ethereum": 0, "polygon": 0}
block_number_url = {
    "ethereum": "https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey=%s" % config["etherscan_api_key"],
    "polygon": "https://api.polygon.io/v2/meta/blocks/latest?apiKey=%s" % config["polygonscan_api_key"]
}

def parse_config():
    global config
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    mail_to = config["mail_to"].split("#")
    config["mail_to"] = mail_to
    black_list = config["black_list"].split("#")
    config["black_list"] = black_list
    if config["etherscan_api_key"] == "":
        logging.error("Etherscan API key is empty")
    if config["polygonscan_api_key"] == "":
        logging.error("Polygonscan API key is empty")
    logging.info("Config loaded", config)

def send_mail(message, chain):
    if config["mail_from"] == "" or config["pswd"] == "" or config["mail_to"] == []:
        logging.error("mail_from or password or mail_to is empty")
        return
    title = "free mint on %s!" % (chain)
    content = message
    mail = MIMEMultipart()
    mail.attach(MIMEText(content, "plain", "utf-8"))
    mail["Subject"], mail["From"] = title, config["mail_from"]
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(config["mail_from"], config["pswd"])
    for _ in config["mail_to"]:
        s.sendmail(config["mail_from"], _, mail.as_string())

def get_cur_block_number(chain):
    global before_block_number
    res = requests.get(block_number_url if chain == 'eth' else bsc_block_number_url)
    if res.status_code != 200:
        log('[%s error] get block number error: wrong status code: %d' % (chain, res.status_code))
        return before_block_number if chain == 'eth' else bsc_before_block_number
    info = json.loads(res.text)
    if 'status' in info and info['status'] != '1':
        log('[%s error] get block number error: wrong block number: %d detail: %s' % (chain, before_block_number if chain == 'eth' else bsc_before_block_number, info))
        return before_block_number if chain == 'eth' else bsc_before_block_number

    cur_block_number = int(info['result'], 16)
    return cur_block_number

if __name__ == "__main__":
    parse_config()
    send_mail("hello world", "ethereum")

def listen_ethereum():
    pass

def listen_polygon():
    pass

block_number_url = "https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey=" + config["etherscan_api_key"]
get_log_url = "https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock=%d&toBlock=latest&topic0=%s&apikey=" + config["etherscan_api_key"]

transfer_id = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
swap_id = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
