## config
add a config.yml at root dir, example here:
```yaml
mail_from: "xxx"
mail_to: "xxx" # email u want to send to when mint event happened
pswd: "xxx" # your mail_from's password
etherscan_api_key: "xxx"
polygon_api_key: "xxx"
black_list: "contract_address1#contract_address2#..." # did not listen these contract's mint event
mint_minimum: "0.01" # the minimum mint value of the mint event
```

## usage
```bash
$ python3 listen.py
```