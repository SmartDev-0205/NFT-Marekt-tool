# Project: NFT Metadata changer
# by: Brent Jeremy 	<https://github.com/Brent-Jeremy>
# Date : 7/18 2022
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from spl.token.instructions import transfer_checked, TransferCheckedParams, create_associated_token_account
from solana.rpc.commitment import Confirmed
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
import base58
import re
import datetime
import asyncio
from asyncstdlib import enumerate
from solana.rpc.websocket_api import connect

from solana.rpc.request_builder import (
    LogsSubscribeFilter,
)
import threading

WSS_ENDPORINT_RPC = "wss://nameless-hidden-lake.solana-mainnet.quiknode.pro/8f1131ad8d22d311c9b061736167c976a5b08ea0/"
ENDPORINT_RPC = "https://nameless-hidden-lake.solana-mainnet.quiknode.pro/8f1131ad8d22d311c9b061736167c976a5b08ea0/"

TOKEN_ID = TOKEN_PROGRAM_ID.__bytes__()
OWNER_ADDRESS = "HdR9AMf31MetLVjmJKmhbUzgmwZJFAowMJUbzQTH224H"
CONTRACT_ADDRESS = "4bnFSnkQCBgFjDd5ThEMKfB8yjRLDngHwAPimpPPWCf3"
TOKEN_ADDRESS = "Bdx9ATvoc2xnieDPRyeCcxpxNsk9fFUUwixhN4rmH6Lo"
PRIVATE_KEY = "3CqcaNk1sdHXXBjHgG6u8nW6xBbHn4Q2QkbcnT62YEUWQtCRjhzJbN39EugGbuvGuTfBrefxyaDw9Z6w3dSnN5QD"
OWNER_IDS = ["810297386211475477"]
AMOUNT = 1000000000
CHANNELID = 981918369852850197
intents = discord.Intents.default()
intents.members = True
connected_contract_wallet = []


class ClaimBot(discord.Client):
    def init(self):
        self.source_address = self.get_associated_address(OWNER_ADDRESS)
        self.connection = Client(endpoint=ENDPORINT_RPC, commitment=Confirmed)
        private_key = PRIVATE_KEY
        byte_array = base58.b58decode(private_key)
        self.owner = Keypair.from_secret_key(byte_array)
        self.wallet_time_dics = {}
        # self.get_wallets_from_transaction("4iDvhWYbTo8kKTYUhJrQMHEnbCydELcTqDUoBNNF9BrqvSpAjYD7ybfiK65cE45YQvDAvhViXmVr2xT3vEsBs2RC")
        if len(connected_contract_wallet) == 0:
            print("Catching wallets that are connected to smart contract....")
            self.get_candidate_wallets()
        print(connected_contract_wallet)
        print("Waiting message")
        threading.Thread(target=self.subscribe_thread, daemon=True).start()

    async def subscribe_logs(self):
        async with connect(WSS_ENDPORINT_RPC) as websocket:
            await websocket.logs_subscribe(
                LogsSubscribeFilter.mentions(PublicKey("HdR9AMf31MetLVjmJKmhbUzgmwZJFAowMJUbzQTH224H")))
            first_resp = await websocket.recv()
            subscription_id = first_resp.result
            async for idx, msg in enumerate(websocket):
                try:
                    transaction = msg.result.value.signature
                    print("New transaction", transaction)
                    wallet = self.get_wallets_from_transaction(transaction)
                    if not wallet in connected_contract_wallet:
                        connected_contract_wallet.append(wallet)
                        print("Finished ")
                except Exception as error:
                    print(error)
            await websocket.logs_unsubscribe(subscription_id)

    def subscribe_thread(self):
        asyncio.run(self.subscribe_logs())

    def get_candidate_wallets(self):
        txes = self.get_signature_transactions()
        for tx in txes:
            try:
                wallet = self.get_wallets_from_transaction(tx)
                if not wallet in connected_contract_wallet:
                    connected_contract_wallet.append(wallet)
            except:
                pass

    async def on_ready(self):
        print('Logged on as', self.user)
        self.init()

    async def on_message(self, message):
        # don't respond to ourselves
        if message.channel.id == CHANNELID:
            global connected_contract_wallet
            channel = message.channel
            messages = await  channel.history(limit=1).flatten()
            message_content = messages[0].content
            try:
                if "/addwallet" in message_content:
                    try:
                        address = re.sub(r"(/addwallet[\s]*)([A-Za-z0-9]{44})", r'\2', message_content)
                        if message.author.id in OWNER_IDS:
                            connected_contract_wallet.append(address)
                            await message.channel.send(
                                "New wallet address is added to whitelist. -> {}".format(CONTRACT_ADDRESS))
                            print(connected_contract_wallet)
                    except Exception as error:
                        print(error)
                    # if not address in self.connected_contract_wallet:
                elif "/removewallet" in message_content:
                    try:
                        address = re.sub(r"(/removewallet[\s]*)([A-Za-z0-9]{44})", r'\2', message_content)
                        if message.author.id in OWNER_IDS and address in connected_contract_wallet:
                            connected_contract_wallet.remove(address)
                            await message.channel.send(
                                "Wallet address is removed from whitelist. -> {}".format(CONTRACT_ADDRESS))
                    except Exception as error:
                        print(error)
                    # if not address in self.connected_contract_wallet:
                elif "/address" in message_content:
                    address = re.sub(r"(/address[\s]*)([A-Za-z0-9]{44})", r'\2', message_content)
                    await message.channel.send(
                        "Checking if your address is connected to this contract. -> {}".format(CONTRACT_ADDRESS))
                    if not address in connected_contract_wallet:
                        await message.channel.send(
                            "This address is not connected to this contract. -> {}".format(CONTRACT_ADDRESS))
                        return
                    await message.channel.send(
                        "Your address is connected to this contract. -> {}".format(CONTRACT_ADDRESS))
                    current_time = datetime.datetime.now()
                    try:
                        old_wallet_time = self.wallet_time_dics[address]
                        differnet_time = current_time - old_wallet_time
                        if differnet_time.seconds > 21600:
                            await message.channel.send("Sending spl token to {}...".format(address))
                            self.transfer_slp(address)
                            await message.channel.send("Sent spl token to {}.".format(address))
                        else:
                            await message.channel.send("Try after {} seconds.".format(21600 - differnet_time.seconds))
                    except:
                        await message.channel.send("Sending spl token to {}...".format(address))
                        self.transfer_slp(address)
                        await message.channel.send("Sent spl token to {}.".format(address))
            except Exception as error:
                print(error)

    def get_signature_transactions(self):
        result = self.connection.get_signatures_for_address(CONTRACT_ADDRESS)
        txes = []
        if 'result' in result:
            result = result['result']
            for tx in result:
                txes.append(tx["signature"])
        return txes

    def get_wallets_from_transaction(self, tx):
        tranaction_struct = self.connection.get_confirmed_transaction(tx)
        try:
            api_keys = tranaction_struct["result"]["transaction"]["message"]["accountKeys"]
            # get only from and to
            return api_keys[0]
        except:
            pass

    def get_associated_address(self, owner):
        mint_address = PublicKey(TOKEN_ADDRESS).__bytes__()
        owner_address = PublicKey(owner).__bytes__()
        return PublicKey.find_program_address(
            seeds=[owner_address, TOKEN_ID, mint_address],
            program_id=ASSOCIATED_TOKEN_PROGRAM_ID
        )[0]

    def create_associated_address(self, owner, mint):
        mint_address = PublicKey(mint).__bytes__()
        owner_address = PublicKey(owner).__bytes__()
        return PublicKey.create_program_address(
            seeds=[owner_address, TOKEN_ID, mint_address],
            program_id=ASSOCIATED_TOKEN_PROGRAM_ID
        )

    def transfer_slp(self, address):
        print("Sending Token : {}".format(address))
        dest_address = self.get_associated_address(address)
        transaction = Transaction()
        transaction.add(
            transfer_checked(
                TransferCheckedParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=self.source_address,
                    mint=PublicKey(TOKEN_ADDRESS),
                    dest=dest_address,
                    owner=PublicKey(OWNER_ADDRESS),
                    amount=AMOUNT,
                    decimals=9,
                    signers=[]
                )
            )
        )
        dest_info = self.connection.get_account_info(dest_address)['result']['value']
        if not dest_info:
            try:
                create_transaction = create_associated_token_account(PublicKey(OWNER_ADDRESS), PublicKey(address),
                                                                     PublicKey(TOKEN_ADDRESS))
                associate_transaction = Transaction()
                associate_transaction.add(create_transaction)
                result = self.connection.send_transaction(
                    associate_transaction, self.owner,
                    opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed))
                print(result)
            except:
                pass
        try:
            result = self.connection.send_transaction(
                transaction, self.owner, opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed))
            print(result)
            current_time = datetime.datetime.now()
            self.wallet_time_dics[address] = current_time
        except:
            pass


if __name__ == "__main__":
    client = ClaimBot(intents=intents)
    client.run(DISCORD_TOKEN, bot=False)

