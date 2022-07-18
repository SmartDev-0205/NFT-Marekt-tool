import sys
import time
import requests

delay = 0.5


def unique_sellers(collection):
    holders = {}
    price_map = {}
    print(f"{collection}: Fetching current listings (this will take a minute)")
    i = 0
    while True:
        url = "https://api-mainnet.magiceden.dev/v2/collections/" + collection + "/listings?offset=" + str(
            i * 20) + "&limit=20"
        response = requests.request("GET", url)
        listings = response.json()

        time.sleep(delay);
        if response.json() == []:
            break;

        for listing in listings:
            if listing['seller'] not in holders.keys():
                holders[listing['seller']] = [listing['tokenMint']]
            else:
                holders[listing['seller']].append(listing['tokenMint'])
            price_map[listing['tokenMint']] = listing['price']

        i += 1

    return (holders, price_map)


def unique_sellers_def(params):
    file_name = "unique_sellers.py"
    params.insert(0, file_name)
    sys.argv = params
    result_str = ""
    try:
        (un_sellers, price_map) = unique_sellers(sys.argv[1])

        result_str += "=================================================================\n"
        print("=================================================================\n")
        result_str += f"Largest {sys.argv[1]} sellers on MagicEden\n"

        index = 0
        for k in sorted(un_sellers, key=lambda k: len(un_sellers[k]), reverse=True):
            # result_str += "(" + str(len(un_sellers[k])) + ") https://solscan.io/account/" + k + "\n"
            index += 1
            if index > 10:
                break
            result_str += str(index) + ") https://solscan.io/account/" + k + "\n"
            subindex = 0
            for mint in un_sellers[k]:
                subindex += 1
                result_str += " (" + str(subindex) + ") https://solscan.io/account/" + k + "\n"
                result_str += f"    - ({str(price_map[mint])} SOL)\n"
        result_str += "=================================================================\n"
        print("=================================result================================\n")
    except:
        result_str = "Collection not found"
    return result_str
