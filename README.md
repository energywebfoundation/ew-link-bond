# Energyweb

[![](https://img.shields.io/pypi/v/ew-link-bond.svg)](https://warehouse.python.org/project/ew-link-bond/) 
[![](https://img.shields.io/pypi/l/ew-link-bond.svg)](https://warehouse.python.org/project/ew-link-bond/) 

## Summary

Energyweb if an Application framework designed to empower energy prosumers and utilities to leverage Blockchain and other cutting edge-cryptographic solutions. Just install it as a dependency with `pip3 install energyweb`. Create a python script and create your own **App** and **Tasks** importing classes from `energyweb.dispatcher` module.

Further development and contribution is much welcome, please contribute with issues and pull requests. :)

## Features
- Raw transactions signing
- Extension and reusability through OOP
- Event-loop logic with asynchronous I/O thread pool control
- General application abstraction
- General Ethereum VM based network client abstraction
    - Tested on [_Parity_](https://www.parity.io/ethereum/) and [_Geth_](https://github.com/ethereum/go-ethereum/wiki/geth)
- [EWF's Origin](https://github.com/energywebfoundation/ew-origin) release A smart-contract support for energy consumption and production registry for [REC](https://en.wikipedia.org/wiki/Renewable_Energy_Certificate_(United_States)) generation

#### Suported Energy Data Sources

- [Verbund Eumel v1.0](https://www.verbund.com/de-at/privatkunden/themenwelten/wiki/smart-meter)
- [Verbund Eumel v2.1.1](https://www.verbund.com/de-at/privatkunden/themenwelten/wiki/smart-meter)
- [EWF's Energy API](https://github.com/energywebfoundation/ew-link-bond/blob/master/docs/api_contract.yaml)
- [Wattime CO2 Emission API v1.0](https://api.watttime.org/docs/)
- [Wattime CO2 Emission API v2.0](https://api.watttime.org/docs/)

### Roadmap
- General EVM Smart-Contracts Event listener task trigger
- Remote logging in cloud platform. Check a list [here](https://www.capterra.com/sem-compare/log-management-software).
- Message Queue for off-line resilience
- Merkle-tree proofs for collected data. Check [precise proofs](https://medium.com/centrifuge/introducing-precise-proofs-create-validate-field-level-merkle-proofs-a31af9220df0) and [typescript implementation](https://github.com/slockit/precise-proofs).
    - Field-level validation
    - Document integrity validation
    - Document structure enforcement
- IPFS storage
    - UUID pre-calculation and validation for smart-contract integration
- Enforce TLS/SSL over http
- ARM TEE support:
    - Offloaded cryptography to hardware accelerators
    - Storage and access of the configuration file in secure enclave
    - Private key generation and signature in CryptoCell

#### Energy Assets Roadmap
- [Gridx Gridbox](https://gridx.de/produkt/gridbox/)
- [Loxone Miniserver](https://www.loxone.com/enen/products/miniserver-extensions/)

#### Smart-Contracts Roadmap
- [EWF's Origin](https://github.com/energywebfoundation/ew-origin) release B
- Universal Sharing Network
- EWF's User and Assets Registry
- Your project here - We are open for suggestions!

## Framework Architecture

The application consists of dynamically loading modules from the configuration file. After loading the modules, the main thread will spawn task threads when a trigger event occurs. In case the main thread dies or become a zombie, it must be restarted from an external command. It is the system administrator task to maintain services health, therefore no mitigation technique is applied.
 
A __task__ can be of any nature, although it is a best practice that it's execution is finite and it's resource usage is predictable. This will avoid _concurrence_ between tasks and possible _deadlocks_.

### Modules

A list of short explanations about the modules and libraries that compose the framework.

__EDS__ **E**nergy **D**ata **S**ources library has modules for supported smart-meter _APIs_ including _energyweb's_ specification written in [Swagger](https://editor.swagger.io), with this any utility or solar/wind farm could bundle many smart-meters and provide a simple [_Restful_](https://en.wikipedia.org/wiki/Representational_state_transfer) API using community provided code in many programming languages. Or even abstract legacy protocols instead of being forced to write a python module.

__Energyweb__ module contains all abstract classes and interfaces to be inherited and implemented by concrete classes. It is the framework skeleton. 

__Smart_Contract__ library bundles all integration modules and assets to persist and query data on [_EVM_](https://en.wikipedia.org/wiki/Ethereum#Virtual_Machine) based _Blockchains_. Most common assets are *json* files describing _smart-contract_ [_ABI_](https://en.wikipedia.org/wiki/Application_binary_interface) s.

__Base58__ module is a helper for parsing [Bitcoin](https://github.com/bitcoin/bitcoin) addresses [IPFS](https://github.com/ipfs/ipfs) file hashes.

__Config__ module has _json_ and _yaml_ formatted application configuration files parsers. App configuration files add better deployment, management, credentials safety and extension capabilities. This module also performs dynamic python module loading, allowing any registered class to be instantiated and parametrized by demand. This feature combined with OOP allows for the same device to be able to change smart-meters and smart-contracts seamlessly.

__Log__ writes a stream of characters to `stdout` and to files. 

__Storage__ supports EWF's Origin release A log storage, designed to record a sequence of _off-chain_ files by updating the previous file contents SHA hash with the next. It is particularly useful to enforce data integrity, by comparing the sequence of raw smart-meter readings with the sequence registered _on-chain_.

__Dispatcher__ module is helper for handling asynchronous non I/O blocking threads of event triggered tasks. Also know as or [event loop](https://en.wikipedia.org/wiki/Event_loop) it is the framework's main loop skeleton.

Event loop abstraction:

![Event Loop](https://github.com/energywebfoundation/ew-link-bond/blob/master/docs/media/threads.jpg)

## Example App
```python
import energyweb
import datetime

class MyTask(energyweb.Task):
    """
    Example Task
    """

    def coroutine(self):
        print('Task {}: {}\n'.format(self.interval, datetime.datetime.now()))


class MyApp(energyweb.App):
    """
    Example Application
    """

    def prepare(self):
        print('{} Prepared'.format(self.__class__.__name__))

    def configure(self):
        t1 = MyTask(interval=energyweb.LifeCycle.FIVE_SECONDS)
        t2 = MyTask(interval=energyweb.LifeCycle.ONE_MINUTE, is_eager=False)
        [self.add_task(t) for t in [t2, t1]]

    def finish(self):
        print('{} Finished'.format(self.__class__.__name__))


app = MyApp()

"""
Test loop
"""
if __name__ == '__main__':
    app.run()
```