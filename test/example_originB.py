#!/usr/bin/env python

import time

import json
import web3 # Web3, HTTPProvider

class Example:

    def __init__(self):
        # after the transaction has been send we wait this time for it to be mined
        self.MAX_RETRIES = 10
        self.SECONDS_BETWEEN_RETRIES = 1

        client_url = "http://localhost:8545"

        # npm start:
        # info: Asset Contract Deployed: 0x6389D7786F7B2cd7e951d417CAD7e5e04295ae48
        contract_address = "0x6389D7786F7B2cd7e951d417CAD7e5e04295ae48"

        with open('AssetContractLookupInterface.json') as contract_json:
            contract = json.load(contract_json)

        self.w3 = web3.Web3(web3.HTTPProvider(client_url))

        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract_address))

        assetProducingRegistryLogic = contract_instance.functions.assetProducingRegistry().call()
        print(assetProducingRegistryLogic) # 0xA82E267dDb7417B1Ef2f88378bAE35dA5fF33647

        # TODO: get assetProducingDB address from assetProducingRegistryLogic

        assetProducingDB = "0x4F804aE27A225e1052BCEa4ecded8b37E8b08218"

        with open('AssetProducingDB.json') as contract_json:
            contract = json.load(contract_json)

        self.contract = contract

        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(assetProducingDB))


        producing_asset_address = "0x343854a430653571b4de6bf2b8c475f828036c30" # from repo ptt-ew-utils-demo config/demo-config.json:75
        producing_asset_pk      =  "12c5c7473dbdb92a524a93baa14ded529fe29acef8d269a3901c14a15e2b0f98"

        owner_address           = "0x71c31ff1faa17b1cb5189fd845e0cca650d215d3" # demo-config.json:77
        owner_pk                = "bfb423a193614c6712efd02951289192c20d70b3fc8a8b7cdee73603fcead486"

        wallet_add = producing_asset_address # select producing assset
        wallet_pwd = producing_asset_pk

        private_key = bytearray.fromhex(wallet_pwd)
        nonce = self.w3.eth.getTransactionCount(account=self.w3.toChecksumAddress(wallet_add))
        transaction = {
            'from': self.w3.toChecksumAddress(wallet_add),
            'gas': 400000,
            'gasPrice': self.w3.toWei('0', 'gwei'),
            'nonce': nonce,
        }

        tx = contract_instance.functions.setLastSmartMeterReadWh(0, 18060000 + 7320000).buildTransaction(transaction)

        print(tx)

        signed_txn = self.w3.eth.account.signTransaction(tx, private_key=private_key)

        tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction) # Error: msg.sender is not owner


def main():
    e = Example()
    #print(e.tx_receipt)

if __name__=="__main__":
    main()