"""
 _
| |                  |
| |   __   _  _    __|
|/ \_/  \_/ |/ |  /  |
 \_/ \__/   |  |_/\_/|_/

Bond - Your favorite library for logging energy data on the blockchain
"""

from energyweb.dispatcher import EventLoop, Task, LifeCycle
from energyweb.eds import EnergyUnit, EnergyData, EnergyDataSource
from energyweb.carbonemission import CarbonEmissionData
from energyweb.interfaces import App

__name__ = 'energyweb'
__author__ = 'Paul Depraz <github.com/cerealkill>'
__repository__ = 'github.com/energywebfoundation/ew-link-bond'
__status__ = "pre-alpha"
__version__ = "0.3.7"
__date__ = "14 December 2018"

modules = {'Eumelv1': {'energyweb.eds', 'Eumelv1'}}
