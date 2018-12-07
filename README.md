# Bond: An energy data interface for blockchain smart contracts

[![](https://img.shields.io/pypi/v/ew-link-bond.svg)](https://warehouse.python.org/project/ew-link-bond/) 
[![](https://img.shields.io/pypi/l/ew-link-bond.svg)](https://warehouse.python.org/project/ew-link-bond/) 

## Summary

Library designed to support the creation of interfaces for reading, parsing and writing energy industry related data to and from the blockchain.

Further development and contribution enhancing generalization of the tool is much welcome, please contribute with issues and pull requests. :)

### Usage

Simply install it as a dependency with `pip3 install ew-link-bond`, 

### Features
- Raw transactions signing
- Extension and reusability through OOP
- Asyncio thread pool control and event loop
- General application abstraction

#### Features Roadmap
- General Smart-Contract event listener
- Remote Logging with some tool (maybe Data Dog)
- Message Queue for off-line resilience
- Accept YAML to generate JSON for more human readable config
- Merkle tree proofs for collected data. Check [precise proofs](https://medium.com/centrifuge/introducing-precise-proofs-create-validate-field-level-merkle-proofs-a31af9220df0) and [typescript implementation](https://github.com/slockit/precise-proofs).
    - Fiel-level validation
    - Document integrity validation
    - Document structure enforcement
- ZK-SNARKS based token splitting
    - Split a token without revealing the total amount in the contract
    - Linear gas costs
- IPFS storage
    - UUID pre-calculation and validation
- Enforce TLS/SSL over http
- Artik710/710s support with:
    - Offloaded cryptography to hardware acceletors
    - Storage and access of the configuration file on secure enclave
    - Private key generation and siganture on secure enclave (Artik710s only)

### Suported Energy Assets

- [Verbund Eumel v1.0](https://www.verbund.com/de-at/privatkunden/themenwelten/wiki/smart-meter)
- [Verbund Eumel v2.1.1](https://www.verbund.com/de-at/privatkunden/themenwelten/wiki/smart-meter)
- [Wattime CO2 Emission API v1.0](https://api.watttime.org/docs/)
- [Wattime CO2 Emission API v2.0](https://api.watttime.org/docs/)

#### Energy Assets Roadmap
- [Gridx Gridbox](https://gridx.de/produkt/gridbox/)
- [Loxone Miniserver](https://www.loxone.com/enen/products/miniserver-extensions/)

### Suported Smart-Contracts

- [Energyweb's Certificate of Origin v1.0](https://github.com/energywebfoundation/ew-origin)

#### Smart-Contracts Roadmap
- Universal Sharing Network 
- Energyweb Asset Registry
- Energyweb Certificate of Origin v2.0
- Your project here - We are open for suggestions!

## Library Organization

The library is organized into `abstract`, `input` and `output`. Abstract defines all classes and interfaces to be inherited and implemented by input and output classes. As the names imply the software consists of loading and reading one or many input modules and write formatted data to output modules.

### Core Classes

The core library comes with an object-oriented structure to standardize and support the extension of the input and output modules, thus extending the system functionalities and ability to communicate with other Energy Assets.

![Core Library Class Diagram](https://github.com/energywebfoundation/ewf-link-bond/blob/master/docs/media/core-class-diagram.png)

Asyncio event loop abstraction:

![Event Loop](https://github.com/energywebfoundation/ewf-link-bond/blob/master/docs/media/threads.png)

### Data Access Object

Object to abstract data persistence, allowing connection to databases and disk storage using the same interfaces. 

### Configuration
            
Descriptor loader to speed up the development of a bond-based app.

This library can be used to load a `json` file that describes the modules to load for production and comsumption of energy, as well as to which blockchain clients and persistence modules to store the data collected. 

Designed with reflection in mind, the configuration file needs to have a list of `consumption`, and `production`. Consumers require the keywords `energy-meter`, and `smart-contract`. Producers require the keywords `energy-meter`, and `carbon-emission`, `smart-contract`.

These keywords are objects describing python-like `module` path, case-sensitive `class_name` and a dictionary of `class_parameters` that are required in the chosen class constructor.

**local-prosumer.json**
```json
{
  "consumers": [
    {
      "name": "my-home",
      "energy-meter": {
        "module": "input.simulator",
        "class_name": "EnergyMeter",
        "class_parameters": {
        }
      },
      "smart-contract": {
        "module": "output.origin_v1",
        "class_name": "OriginConsumer",
        "class_parameters": {
          "asset_id": 4,
          "client_url": "http://localhost:8143",
          "wallet_add": "0x0074AD67550a8B0690EeE3E0CA99f406bEab678c",
          "wallet_pwd": "574e43825f7217cb2de43d6a3d34d3d1a5e77d28aac36ee191282fc0a14c34e4"
        }
      }
    }
  ],
  "producers": [
    {
      "name": "my-solar-panels",
      "energy-meter": {
        "module": "input.simulator",
        "class_name": "EnergyMeter",
        "class_parameters": {
        }
      },
      "carbon-emission": {
        "module": "input.carbonemission",
        "class_name": "Wattime",
        "class_parameters": {
          "usr": "your_user_here",
          "pwd": "password_of_your_user",
          "ba": "FR",
          "hours_from_now": 24
        }
      },
      "smart-contract": {
        "module": "output.origin_v1",
        "class_name": "OriginProducer",
        "class_parameters": {
          "asset_id": 3,
          "client_url": "http://localhost:8143",
          "wallet_add": "0x0074AD67550a8B0690EeE3E0CA99f406bEab678c",
          "wallet_pwd": "574e43825f7217cb2de43d6a3d34d3d1a5e77d28aac36ee191282fc0a14c34e4"
        }
      }
    }
  ]
}
```
