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

#### Planned Features
- Further support of Energy Assets
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

#### Planned
- [Gridx Gridbox](https://gridx.de/produkt/gridbox/)
- [Loxone Miniserver](https://www.loxone.com/enen/products/miniserver-extensions/)

### Suported Smart-Contracts

- [Energyweb's Certificate of Origin v1.0](https://github.com/energywebfoundation/ew-origin)

#### Planned
- Energyweb's Asset Registry
- Energyweb's Certificate of Origin v2.0
- Your project here - We are open for suggestions!

## Core Library

The main component of the `bond` code is the [core](https://github.com/energywebfoundation/ewf-link-bond/tree/master/core) library, organized into `abstract`, `input` and `output`. Abstract defines all classes and interfaces to be inherited and implemented by input and output classes. As the names imply the software consists of loading and reading one or many input modules and write formatted data to output modules.

### Core Classes

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

```
