import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from .const import DEFAULT_HEADERS, ENDPOINT, INVOICEHISTORY_ENDDATE_PARAM, INVOICEHISTORY_PATH, \
    INVOICEHISTORY_STARTDATE_PARAM, INVOICEHISTORY_SUBSCRIPTION_PARAM, JSON_CONTENT, LASTDOC_PATH, \
    LOGIN_PATH, PWD_PARAM, SUBSCRIPTIONS_PATH, USER_PARAM, LASTCONSUMPTION_PATH, \
    LASTCONSUMPTION_SUBSCRIPTION_PARAM
from .models import Consumption, Invoice, Subscription

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class AguasGaia:

    def __init__(self, websession, username, password, subscription_id=None):
        self._last_invoice = None
        self._last_consumption = None
        self._invoice_history = None
        self._selected_subscription_id = subscription_id
        self._subscriptions = None
        self._session_cookies = None
        self._token = None
        self._websession = websession
        self._username = username
        self._password = password

    async def __api_request(self, url: str, method="get", data=None, return_cookies=False, params=None):
        async with getattr(self._websession, method)(url, headers=self.__get_auth_headers(), json=data,
                                                     params=params) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    json_response = await response.json()
                    if return_cookies:
                        return {
                            "response": json_response,
                            "cookies": response.cookies
                        }
                    return json_response
                else:
                    raise Exception(f"HTTP Request Error: %s", str(response.status) + " " + str(response.content_type))
            except Exception as err:
                _LOGGER.error(f"API request error: %s", err)
                return None

    def __get_auth_headers(self):
        _LOGGER.debug("AguasGaia API AuthHeaders")
        headers = {**DEFAULT_HEADERS}
        if self._token is not None:
            headers["X-Auth-Token"] = self._token
        if self._session_cookies is not None:
            headers["Cookie"] = self._session_cookies
        return headers

    def get_selected_subscription(self):
        return str(self._selected_subscription_id)

    def set_selected_subscription(self, sub: Subscription):
        self._selected_subscription_id = sub.subscription_id

    async def login(self):
        _LOGGER.debug("AguasGaia API Login")
        url = ENDPOINT + LOGIN_PATH

        data = {
            USER_PARAM: self._username,
            PWD_PARAM: self._password
        }

        res = await self.__api_request(url, method="post", data=data, return_cookies=True)
        if res is not None:
            self._token = res.get("response", {}).get("token", {}).get("token", None)
            cookies = res.get("cookies", [])
            self._session_cookies = "".join([cookies[x].key + "=" + cookies[x].value + ";" for x in cookies])
            if self._token is None or self._session_cookies is None:
                return False

        if self._selected_subscription_id is None:
            subscriptions = await self.get_subscriptions()
            if subscriptions is None or len(subscriptions) == 0:
                return False
            self.set_selected_subscription(subscriptions.pop())
        return True

    async def get_subscriptions(self) -> list[Subscription]:
        _LOGGER.debug("AguasGaia API Subscriptions")

        url = ENDPOINT + SUBSCRIPTIONS_PATH
        subscription_payload = await self.__api_request(url)
        self._subscriptions = [Subscription(sub) for sub in await self.__api_request(url)]
        return self._subscriptions

    async def get_last_invoice(self, subscription_id=None) -> Invoice:
        _LOGGER.debug("AguasGaia API LastDocData")

        subscription_id = subscription_id or self._selected_subscription_id

        url = ENDPOINT + LASTDOC_PATH

        invoice_payload = await self.__api_request(url, params={LASTCONSUMPTION_SUBSCRIPTION_PARAM: subscription_id})

        self._last_invoice = Invoice(invoice_payload)
        return self._last_invoice

    async def get_invoice_history(self, subscription_id=None):
        _LOGGER.debug("AguasGaia API Invoice History")

        subscription_id = subscription_id or self._selected_subscription_id

        today = datetime.now()
        year_ago = today - relativedelta(years=1)
        url = ENDPOINT + INVOICEHISTORY_PATH

        self._invoice_history = await self.__api_request(
            url,
            params={
                INVOICEHISTORY_ENDDATE_PARAM: "{year}-{month}-{day}".format(
                    year=today.year,
                    month=today.month,
                    day=today.day
                ),
                INVOICEHISTORY_STARTDATE_PARAM: "{year}-{month}-{day}".format(
                    year=year_ago.year,
                    month=year_ago.month,
                    day=year_ago.day
                ),
                INVOICEHISTORY_SUBSCRIPTION_PARAM: subscription_id
            }
        )
        return self._invoice_history

    async def get_last_consumption(self, subscription_id=None) -> Consumption:
        _LOGGER.debug("AguasGaia API Last Consumption")

        subscription_id = subscription_id or self._selected_subscription_id

        url = ENDPOINT + LASTCONSUMPTION_PATH

        last_consumption_payload = await self.__api_request(
            url,
            params={LASTCONSUMPTION_SUBSCRIPTION_PARAM: subscription_id})

        self._last_consumption = Consumption(last_consumption_payload)

        if self._last_consumption.consumption_value == 0 and self._last_consumption.consumption_attributes == {}:
            raise Exception("No consumption data found")

        return self._last_consumption
