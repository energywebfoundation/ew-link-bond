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
        contract_address = "0xb19B5d529F8af11f5b91d4FC9B33106844F210a0"

        with open('AssetContractLookupInterface.json') as contract_json:
            contract = json.load(contract_json)

        self.w3 = web3.Web3(web3.HTTPProvider(client_url))

        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract_address))

        assetProducingRegistryLogic = contract_instance.functions.assetProducingRegistry().call()
        print(assetProducingRegistryLogic)
        # works: 0x944655d2D4C6C68dBb2B1576A89fAD5e36e714dA

        # TODO: get assetProducingDB address from assetProducingRegistryLogic

        assetProducingDB = "0xcab91029732e642067F9095dbb395937d67667F7"

        with open('AssetProducingDB.json') as contract_json:
            contract = json.load(contract_json)

        self.contract = contract

        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(assetProducingDB))


        wallet_add = "0x343854a430653571b4de6bf2b8c475f828036c30"
        wallet_pwd = "12c5c7473dbdb92a524a93baa14ded529fe29acef8d269a3901c14a15e2b0f98"
        private_key = bytearray.fromhex(wallet_pwd)
        nonce = self.w3.eth.getTransactionCount(account=self.w3.toChecksumAddress(wallet_add))
        transaction = {
            'from': self.w3.toChecksumAddress(wallet_add),
            'gas': 400000,
            'gasPrice': self.w3.toWei('0', 'gwei'),
            'nonce': nonce,
        }

        method_name = "setLastSmartMeterReadWh"

        tx = contract_instance.functions.setLastSmartMeterReadWh(0, 100000).buildTransaction(transaction)

        print(tx)

        signed_txn = self.w3.eth.account.signTransaction(tx, private_key=private_key)

        tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)


    def getContractMethod(self, method_name):
        for method in self.contract['abi']:
            try:
                if method['name'] == method_name:
                    return method
            except KeyError:
                continue

def main():
    e = Example()
    #print(e.tx_receipt)

if __name__=="__main__":
    main()