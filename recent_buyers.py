import sys
import time
import requests


def recent_buyers(collection):
    buyers = {}
    price_map = {}
    print(f"{collection}: Fetching current activities (this will take a minute)")

    url = "https://api-mainnet.magiceden.dev/v2/collections/" + collection + "/activities?offset=0&limit=500"
    response = requests.request("GET", url)
    activities = response.json()

    for act in activities:
        if act['type'] == 'buyNow':
            if act['buyer'] not in buyers.keys():
                buyers[act['buyer']] = [act['tokenMint']]
            else:
                buyers[act['buyer']].append(act['tokenMint'])
            price_map[act['tokenMint']] = act['price']

    return (buyers, price_map)


def recent_buyers_def(params):
    result_str = ""
    try:
        file_name = "recent_buyers.py"
        params.insert(0, file_name)
        sys.argv = params
        (rec_buyers, price_map) = recent_buyers(sys.argv[1])
        result_str += "=================================================================\n"
        result_str += f"Largest recent {sys.argv[1]} buyers on MagicEden\n"
        index = 0
        for k in sorted(rec_buyers, key=lambda k: len(rec_buyers[k]), reverse=True):
            index += 1
            if index > 10:
                break
            result_str = result_str + "(" + str(index) + ") https://solscan.io/account/" + k + "\n"
            for mint in rec_buyers[k]:
                result_str = result_str + f"    - ({str(price_map[mint])} SOL)\n"

        result_str += "================================================================="
    except:
        result_str = "Collection not found"
    print(result_str)
    return  result_str
