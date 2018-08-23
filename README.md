# Bond: An energy data interface for blockchain smart contracts

Service designed to be a general interface for reading, parsing and writing energy industry related data to and from the blockchain.

The main component of the `bond` code is the [core](https://github.com/energywebfoundation/ewf-link-bond/tree/master/core) library, organized into `abstract`, `input` and `output`. Abstract defines all classes and interfaces to be inherited and implemented by input and output classes. As the names imply the software consists of loading and reading one or many input modules and write formatted data to output modules.

Further development and contribution enhancing generalization of the tool is much welcome, please contribute with issues and pull requests. :)

### Configuration
Bond needs a `json` file to know which modules to load and read the modules configuration. Designed with reflection in mind, the configuration file needs to have a list of `consumption` or `production` and a `client`. These keywords are objects describing python-like `module` path, case-sensitive `class_name` and a dictionary of `class_parameters` that are required in the chosen class constructor.

### Core Classes
![Core Library Class Diagram](https://github.com/energywebfoundation/ewf-link-bond/blob/master/docs/media/core-class-diagram.png)
