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
        wallet_add = "0x68F89f072A37c9571733E899EFF7219a03d51bb0"
        wallet_pwd = "f97120b63afc4a6c622a4131687ac6d3ef068590beec04276a3d13bc4148c12b"

        # npm run start-test-backend:
        # GET - ProducingAsset 0 (contract 0xa82e267ddb7417b1ef2f88378bae35da5ff33647)
        # PUT - OriginContractLookupMarketLookupMapping 0xe377ae7241f76ac5cdb89f5debc0dbe82f9c2c03

        # npm start:
        # info: Asset Contract Deployed: 0x6389D7786F7B2cd7e951d417CAD7e5e04295ae48
        contract_address = "0x6389D7786F7B2cd7e951d417CAD7e5e04295ae48"

        with open('AssetProducingDB.json') as contract_json:
            contract = json.load(contract_json)

        #print(contract['abi'])

        self.w3 = web3.Web3(web3.HTTPProvider(client_url))

        contract_instance = self.w3.eth.contract(
            abi=contract['abi'],
            address=self.w3.toChecksumAddress(contract_address))
            #bytecode=contract['bytecode'])

        method_name = "getLastSmartMeterReadWh"
        asset_id = 0
        args = [asset_id]
        
        #smartMeterRead = getattr(contract_instance.functions, method_name)(*args).call()
        smartMeterRead = contract_instance.functions.getLastSmartMeterReadWh(0).call()

        # with correct method name -> Error: VM Exception while processing transaction: revert ganache-core.node.cli.js:10

        # with incorrect method name -> Error: The function 'getAssetLocation' was not found in this contract's abi. ", 'Are you sure you provided the correct contract abi?

def main():
    e = Example()
    #print(e.tx_receipt)

if __name__=="__main__":
    main()