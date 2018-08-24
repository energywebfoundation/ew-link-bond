# Bond: An energy data interface for blockchain smart contracts

[![](https://img.shields.io/pypi/v/ew-link-bond.svg)](https://warehouse.python.org/project/ew-link-bond/) 
[![](https://img.shields.io/pypi/l/ew-link-bond.svg)](https://warehouse.python.org/project/ew-link-bond/) 

## Summary

Library designed to support the creation of interfaces for reading, parsing and writing energy industry related data to and from the blockchain.

The main component of the `bond` code is the [core](https://github.com/energywebfoundation/ewf-link-bond/tree/master/core) library, organized into `abstract`, `input` and `output`. Abstract defines all classes and interfaces to be inherited and implemented by input and output classes. As the names imply the software consists of loading and reading one or many input modules and write formatted data to output modules.

Further development and contribution enhancing generalization of the tool is much welcome, please contribute with issues and pull requests. :)

### Suported Energy Assets

#### Available
- [Verbund Eumel v1.0](https://www.verbund.com/de-at/privatkunden/themenwelten/wiki/smart-meter) - Smart meter still not available on the market.
- [Wattime CO2 Emission API v1.0](https://api.watttime.org/docs/)
- [Wattime CO2 Emission API v2.0](https://api.watttime.org/docs/)

#### Future
- [Gridx Gridbox](https://gridx.de/produkt/gridbox/)
- [Loxone Miniserver](https://www.loxone.com/enen/products/miniserver-extensions/)

## Core Library

### Classes

The core library comes with an object-oriented structure to standardize and support the extension of the input and output modules, thus extending the system functionalities and ability to communicate with other Energy Assets.

![Core Library Class Diagram](https://github.com/energywebfoundation/ewf-link-bond/blob/master/docs/media/core-class-diagram.png)

### Data Access Object

Object to abstract data persistence, allowing connection to databases and disk storage using the same interfaces. 

### Configuration

Descriptor loader to speed up the development of a bond based app.

This library can be used to load a `json` file that describes the modules to load for production and comsumption of energy, as well as to which blockchain clients and persistence modules to store the data collected. 

Designed with reflection in mind, the configuration file needs to have a list of `consumption`, `production` and a `client`. These keywords are objects describing python-like `module` path, case-sensitive `class_name` and a dictionary of `class_parameters` that are required in the chosen class constructor.

**local-prosumer.json**
```json
{
  "consumption": [
    {
      "energy": {
        "module": "origin.input.simulator",
        "class_name": "EnergyMeter",
        "class_parameters": {
        }
      },
      "origin": {
        "module": "origin.config_parser",
        "class_name": "OriginCredentials",
        "class_parameters": {
          "asset_id": 1,
          "contract_address": "0xc73628651f491682ab12a2a82ca700e06940b9b4",
          "wallet_add": "0x0074AD67550a8B0690EeE3E0CA99f406bEab678c",
          "wallet_pwd": "574e43825f7217cb2de43d6a3d34d3d1a5e77d28aac36ee191282fc0a14c34e4"
        }
      },
      "name": "consumer_site_0"
    }
  ],
  "production": [
    {
      "energy": {
        "module": "core.input.simulator",
        "class_name": "EnergyMeter",
        "class_parameters": {
        }
      },
      "carbonemission": {
        "module": "core.input.carbonemission",
        "class_name": "Wattime",
        "class_parameters": {
          "usr": "your_user_here",
          "pwd": "password_of_your_user",
          "ba": "FR",
          "hours_from_now": 24
        }
      },
      "origin": {
        "module": "core.abstract.bond",
        "class_name": "OriginCredentials",
        "class_parameters": {
          "asset_id": 1,
          "contract_address": "0xc73628651f491682ab12a2a82ca700e06940b9b4",
          "wallet_add": "0x0074AD67550a8B0690EeE3E0CA99f406bEab678c",
          "wallet_pwd": "574e43825f7217cb2de43d6a3d34d3d1a5e77d28aac36ee191282fc0a14c34e4"
        }
      },
      "name": "producer_site_0"
    }
  ],
  "client": {
    "module": "core.output.energyweb",
    "class_name": "RemoteClientOriginProducer",
    "class_parameters": {
      "url": "http://localhost:8545"
    }
  }
}
```
