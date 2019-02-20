"""
Library containing the implementations of CO2 oracles integration classes
"""
import calendar
import datetime
import requests

from energyweb.interfaces import ExternalData, IntegrationPoint


class CarbonEmissionData(ExternalData):
    """
    Standard for collected carbon emission data, to be transformed into mintable data.
    """

    def __init__(self, access_epoch, raw, accumulated_co2, measurement_epoch):
        """
        Minimum set of data for power measurement logging.
        :param access_epoch: Time the external API was accessed
        :param raw: Raw data collected
        :param accumulated_co2: Registered in kg of carbon dioxide
        :param measurement_epoch: Time of measurement at the source
        """
        self.accumulated_co2 = accumulated_co2
        self.measurement_epoch = measurement_epoch
        ExternalData.__init__(self, access_epoch, raw)


class CarbonEmissionAPI(IntegrationPoint):
    """
    Carbon emission endpoint data interface
    """
    def read_state(self, *args, **kwargs) -> CarbonEmissionData:
        """
        Establishes a connection to the integration medium and returns the latest state
        :rtype: ExternalData
        """
        raise NotImplementedError

    def write_state(self, *args, **kwargs) -> ExternalData:
        """
        Establishes a connection to the integration medium and persists data
        :rtype: ExternalData
        """
        raise NotImplementedError


class WattimeV1(CarbonEmissionAPI):

    def __init__(self, usr: str, pwd: str, ba: str, hours_from_now: int = 2):
        """
        Wattime API credentials. http://watttime.org/
        :param usr: Username used for login
        :param pwd: Users password
        :param ba: Balancing Authority. https://api.watttime.org/tutorials/#ba
        :param hours_from_now: Hours from the current time to check for CO emission. If none provided, will \
        get current day.
        """
        self.credentials = {'username': usr, 'password': pwd}
        self.api_url = 'https://api.watttime.org/api/v1/'
        self.ba = ba
        self.hours_from_now = hours_from_now

    def read_state(self) -> CarbonEmissionData:
        """
        Reach wattime api, parse and convert to CarbonEmissionData.
        """
        auth_token = self.__get_auth_token()
        # 2. Fetch marginal data
        raw = self.__get_marginal(auth_token)
        # 3. Converts lb/MW to kg/W
        accumulated_co2 = raw['marginal_carbon']['value'] * 0.453592 * pow(10, -6)
        # 4. Converts time stamps to epoch
        now = datetime.datetime.now()
        access_epoch = calendar.timegm(now.timetuple())
        measurement_timestamp = datetime.datetime.strptime(raw['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return CarbonEmissionData(access_epoch, raw, accumulated_co2, measurement_epoch)

    def write_state(self, *args, **kwargs) -> ExternalData:
        raise NotImplementedError

    def __get_auth_token(self) -> str:
        """
        Exchange credentials for an access token.
        :return: Access token string suitable for passing as arg in other methods.
        """
        endpoint = self.api_url + 'obtain-token-auth/'
        r = requests.post(endpoint, data=self.credentials)
        if not r.status_code == 200:
            raise AttributeError('Failed getting a new token.')
        ans = r.json()
        if len(ans['token']) < 5:
            raise AttributeError('Failed getting a new token.')
        return ans['token']

    def __get_marginal(self, auth_token: str) -> dict:
        """
        Gets marginal carbon emission based on real time energy source mix of the grid.
        :param auth_token: authentication token
        :return: Measured data in lb/MW plus other relevant raw metadata.
        """
        base_time = datetime.datetime.now()
        if self.hours_from_now:
            start_time = base_time - datetime.timedelta(hours=self.hours_from_now)
            start_at = start_time.strftime("%Y-%m-%dT%H:00:00")
            end_at = base_time.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            start_at = base_time.strftime("%Y-%m-%dT00:00:00")
            end_at = base_time.strftime("%Y-%m-%dT23:59:59")

        marginal_query = {
            'ba': self.ba,
            'start_at': start_at,
            'end_at': end_at,
            'page_size': 1,
            'market': 'RTHR'
        }
        endpoint = self.api_url + 'marginal/'
        h = {'Authorization': 'Token ' + auth_token}
        r = requests.get(endpoint, headers=h, params=marginal_query)
        ans = r.json()
        if 'count' not in ans.keys() and 'detail' in ans.keys():
            raise AttributeError('Failed to login on api.')
        if ans['count'] < 1:
            raise AttributeError('Empty response from api.')
        return ans['results'][0]

    def get_ba(self, lon, lat, auth_token) -> str:
        """
        Fetch Balancing Authority data based on geo spatial coordinates.
        :param lon: longitude
        :param lat: latitude
        :param auth_token: authentication token
        :return: Abbreviated ba name suitable for marginal requests.
        """
        geo_query = {
            'type': 'Point',
            'coordinates': [lon, lat]
        }
        endpoint = self.api_url + 'balancing_authorities/'
        h = {'token': auth_token}
        r = requests.get(endpoint, headers=h, params=geo_query)
        ans = r.json()
        return ans['abbrev']


class WattimeV2(CarbonEmissionAPI):

    def __init__(self, usr: str, pwd: str, ba: str):
        """
        Wattime API credentials. http://watttime.org/
        :param usr: Username used for login
        :param pwd: Users password
        :param ba: Balancing Authority. https://api.watttime.org/tutorials/#ba
        """
        self.credentials = (usr, pwd)
        self.api_url = 'https://api2.watttime.org/v2test/'
        self.ba = ba

    def read_state(self) -> CarbonEmissionData:
        """
        Reach wattime api, parse and convert to CarbonEmissionData.
        """
        auth_token = self.__get_auth_token()
        # 2. Fetch marginal data
        raw = self.__get_marginal(auth_token)
        # 3. Converts lb/MW to kg/W
        accumulated_co2 = raw['avg'] * 0.453592 * pow(10, -6)
        # 4. Converts time stamps to epoch
        now = datetime.datetime.now()
        access_epoch = calendar.timegm(now.timetuple())
        measurement_timestamp = now
        measurement_epoch = calendar.timegm(measurement_timestamp.timetuple())
        return CarbonEmissionData(access_epoch, raw, accumulated_co2, measurement_epoch)

    def write_state(self, *args, **kwargs) -> ExternalData:
        raise NotImplementedError

    def __get_auth_token(self) -> str:
        """
        Exchange credentials for an access token.
        :return: Access token string suitable for passing as arg in other methods.
        """
        endpoint = self.api_url + 'login'
        r = requests.get(endpoint, auth=self.credentials)
        if not r.status_code == 200:
            raise AttributeError('Failed getting a new token.')
        ans = r.json()
        if len(ans['token']) < 5:
            raise AttributeError('Failed getting a new token.')
        return ans['token']

    def __get_marginal(self, auth_token: str) -> dict:
        """
        Gets marginal carbon emission based on real time energy source mix of the grid.
        :param auth_token: authentication token
        :return: Measured data in lb/MW plus other relevant raw metadata.
        """
        marginal_query = {
            'ba': self.ba
        }
        endpoint = self.api_url + 'insight/'
        h = {'Authorization': 'Bearer ' + auth_token}
        r = requests.get(endpoint, headers=h, params=marginal_query)
        if not r.status_code == 200:
            raise AttributeError('Failed to login on api.')
        return r.json()
