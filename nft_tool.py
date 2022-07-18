from deal_scanner import *
from recent_buyers import *
from attribute_count_floors import *
from attribute_count_listings import *
from wallet_evaluation import *
from unique_sellers import *
import discord

DISCORD_TOKEN = "OTMyMTU4NDEwNDcwODY2OTY0.YeO6SA.dwocN-3VIYVLCxcqqKTa9KSXER4"
CHANNELID = 981918369852850197
intents = discord.Intents.default()
intents.members = True


def make_parameters_from_str(str):
    parameters = str.split()
    return parameters


def make_list_from_parameter_without_filename(list):
    parameter_str = ""
    try:
        list.pop(0)
        for word in list:
            parameter_str += "{} ".format(word)
    except:
        pass
    return parameter_str


def deal_scanner_call(str):
    parameters = make_parameters_from_str(str)
    if "-a" in parameters:
        print("Fetching deals per collection...")
    else:
        print("Fetching current listings (this will take a minute)...")
    result_str = deal_scanner_def(parameters)
    return result_str


def recent_buyers_call(str):
    print("Fetching current activities (this will take a minute)....")
    parameters = make_parameters_from_str(str)
    result_str = recent_buyers_def(parameters)
    return result_str


def attribute_count_floors_call(str):
    parameters = make_parameters_from_str(str)
    result_str = attribute_count_floors_def(parameters)
    return result_str


def attribute_count_floors_listing_call(str):
    parameters = make_parameters_from_str(str)
    result_str = attribte_count_listings_def(parameters)
    return result_str


def wallet_evaluation_call(str):
    parameters = make_parameters_from_str(str)
    result_str = wallet_evaluation_def(parameters)
    return result_str


def unique_sellers_call(str):
    parameters = make_parameters_from_str(str)
    result_str = unique_sellers_def(parameters)
    print(result_str)
    return result_str


# if __name__ == '__main__':
    # deal_scanner_call("-a 100 0.5 2.5")
    # deal_scanner_call("gooney_toons gooneytoons 15")
    # recent_buyers_call("gooney_toons")
    # attribute_count_floors_call("solgods solgods")
    # attribute_count_floors_listi ng_call("solgods solgods 3")
    # wallet_evaluation_call("8vU6RfyFDk9WriVgaJohBxqtE86TLtjAR8cPWjdU6zEN gooney_toons")
    # unique_sellers_call("solgods")

class ClaimBot(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.channel.id == CHANNELID:
            channel = message.channel
            messages = await  channel.history(limit=1).flatten()
            message_content = messages[0].content
            try:
                if "/deals" in message_content:
                    if "-a" in make_parameters_from_str(message_content):
                        await message.channel.send("Fetching deals per collection...")
                    else:
                        await message.channel.send("Fetching current listings (this will take a minute)...")
                    argments_str = make_list_from_parameter_without_filename(make_parameters_from_str(message_content))
                    result_str = deal_scanner_call(argments_str)
                    lines = result_str.split("\n")
                    for line in lines:
                        await message.channel.send(line)

                elif "/sellers" in message_content:
                    await message.channel.send(f"Fetching current listings (this will take a minute)...")
                    argments_str = make_list_from_parameter_without_filename(make_parameters_from_str(message_content))
                    result_str = unique_sellers_call(argments_str)
                    lines = result_str.split("\n")
                    for line in lines:
                        await message.channel.send(line)
                elif "/buyers" in message_content:
                    await message.channel.send("Fetching current activities (this will take a minute)...")
                    argments_str = make_list_from_parameter_without_filename(make_parameters_from_str(message_content))
                    result_str = recent_buyers_call(argments_str)
                    lines = result_str.split("\n")
                    for line in lines:
                        await message.channel.send(line)
                elif "/attribute_count_floors" in message_content:
                    await message.channel.send("Fetching token attributes...")
                    argments_str = make_list_from_parameter_without_filename(make_parameters_from_str(message_content))
                    result_str = attribute_count_floors_call(argments_str)
                    lines = result_str.split("\n")
                    for line in lines:
                        await message.channel.send(line)
                elif "/attribute_count_listings" in message_content:
                    await message.channel.send("Fetching token attributes...")
                    argments_str = make_list_from_parameter_without_filename(make_parameters_from_str(message_content))
                    result_str = attribute_count_floors_listing_call(argments_str)
                    lines = result_str.split("\n")
                    for line in lines:
                        await message.channel.send(line)
                elif "/scan" in message_content:
                    await message.channel.send("Fetching ME NFTs in wallet...")
                    argments_str = make_list_from_parameter_without_filename(make_parameters_from_str(message_content))
                    result_str = wallet_evaluation_call(argments_str)
                    lines = result_str.split("\n")
                    for line in lines:
                        await message.channel.send(line)
            except Exception as error:
                print(error)


if __name__ == "__main__":
    client = ClaimBot(intents=intents)
    client.run(DISCORD_TOKEN, bot=False)
