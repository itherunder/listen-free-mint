## config
add a config.yml at root dir, example here:
```yaml
mail:
  from: "xxx"
  to: "xxx" # email u want to send to when mint event happened
  pswd: "xxx" # your mail_from's password
api_key:
  etherscan: "xxx"
  polygonscan: "xxx"
  opensea: "xxx" # opensea api key
# 0x2953399124f0cbb46d2cbacd8a89cf0599974963 is opensea nft
# 0x495f947276749Ce646f68AC8c248420045cb7b5e is opensea nft
black_list: "contract_address1#contract_address2#..." # did not listen these contract's mint event
mint_minimum: "0.01" # the minimum mint value of the mint event
params:
  # query_limit: 100 # deprecated
  event_type: "transfer" # event u want to listen
  account_address: "0x0000000000000000000000000000000000000000"
  # collection_slug: "xxx"
```

## usage
```bash
$ pip3 install -r requirements.txt
$ python3 listen.py
```
