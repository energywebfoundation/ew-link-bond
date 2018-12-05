"""
USN RentingSupport Smart-Contract interface
"""
contract = {
    "address": "0x85Ec283a3Ed4b66dF4da23656d4BF8A507383bca",
    "abi": [
        {
            "constant": True,
            "inputs": [
                {
                    "name": "id",
                    "type": "bytes32"
                },
                {
                    "name": "index",
                    "type": "uint256"
                }
            ],
            "name": "getState",
            "outputs": [
                {
                    "name": "controller",
                    "type": "address"
                },
                {
                    "name": "rentedFrom",
                    "type": "uint64"
                },
                {
                    "name": "rentedUntil",
                    "type": "uint64"
                },
                {
                    "name": "properties",
                    "type": "uint128"
                }
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {
                    "name": "id",
                    "type": "bytes32"
                }
            ],
            "name": "getStateCount",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {
                    "name": "id",
                    "type": "bytes32"
                },
                {
                    "name": "secondsToRent",
                    "type": "uint32"
                },
                {
                    "name": "token",
                    "type": "address"
                }
            ],
            "name": "rent",
            "outputs": [],
            "payable": True,
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {
                    "name": "id",
                    "type": "bytes32"
                },
                {
                    "name": "user",
                    "type": "address"
                }
            ],
            "name": "getRentingState",
            "outputs": [
                {
                    "name": "rentable",
                    "type": "bool"
                },
                {
                    "name": "free",
                    "type": "bool"
                },
                {
                    "name": "open",
                    "type": "bool"
                },
                {
                    "name": "controller",
                    "type": "address"
                },
                {
                    "name": "rentedUntil",
                    "type": "uint64"
                },
                {
                    "name": "rentedFrom",
                    "type": "uint64"
                },
                {
                    "name": "props",
                    "type": "uint128"
                }
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {
                    "name": "id",
                    "type": "bytes32"
                }
            ],
            "name": "returnObject",
            "outputs": [],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {
                    "name": "id",
                    "type": "bytes32"
                }
            ],
            "name": "supportedTokens",
            "outputs": [
                {
                    "name": "addresses",
                    "type": "address[]"
                }
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {
                    "name": "id",
                    "type": "bytes32"
                },
                {
                    "name": "token",
                    "type": "address"
                }
            ],
            "name": "tokenReceiver",
            "outputs": [
                {
                    "name": "",
                    "type": "bytes32"
                }
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {
                    "name": "id",
                    "type": "bytes32"
                },
                {
                    "name": "user",
                    "type": "address"
                },
                {
                    "name": "secondsToRent",
                    "type": "uint32"
                },
                {
                    "name": "token",
                    "type": "address"
                }
            ],
            "name": "price",
            "outputs": [
                {
                    "name": "",
                    "type": "uint128"
                }
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "name": "fixFilter",
                    "type": "bytes32"
                },
                {
                    "indexed": True,
                    "name": "id",
                    "type": "bytes32"
                },
                {
                    "indexed": False,
                    "name": "controller",
                    "type": "address"
                },
                {
                    "indexed": False,
                    "name": "rentedFrom",
                    "type": "uint64"
                },
                {
                    "indexed": False,
                    "name": "rentedUntil",
                    "type": "uint64"
                },
                {
                    "indexed": False,
                    "name": "noReturn",
                    "type": "bool"
                },
                {
                    "indexed": False,
                    "name": "amount",
                    "type": "uint128"
                },
                {
                    "indexed": False,
                    "name": "token",
                    "type": "address"
                },
                {
                    "indexed": False,
                    "name": "properties",
                    "type": "uint128"
                }
            ],
            "name": "LogRented",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "name": "fixFilter",
                    "type": "bytes32"
                },
                {
                    "indexed": True,
                    "name": "id",
                    "type": "bytes32"
                },
                {
                    "indexed": False,
                    "name": "controller",
                    "type": "address"
                },
                {
                    "indexed": False,
                    "name": "rentedFrom",
                    "type": "uint64"
                },
                {
                    "indexed": False,
                    "name": "rentedUntil",
                    "type": "uint64"
                },
                {
                    "indexed": False,
                    "name": "paidBack",
                    "type": "uint128"
                }
            ],
            "name": "LogReturned",
            "type": "event"
        }
    ],
    "bytecode": '0x'
}
