import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .const import DEFAULT_HEADERS, ENDPOINT, INVOICEHISTORY_ENDDATE_PARAM, INVOICEHISTORY_PATH, \
    INVOICEHISTORY_STARTDATE_PARAM, INVOICEHISTORY_SUBSCRIPTION_PARAM, JSON_CONTENT, LASTDOC_PATH, \
    LASTDOC_SUBSCRIPTION_PARAM, LOGIN_PATH, PWD_PARAM, SUBSCRIPTIONS_PATH, USER_PARAM, LASTCONSUMPTION_PATH, \
    LASTCONSUMPTION_SUBSCRIPTION_PARAM
from .models import Consumption, Invoice

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class AguasGaia:

    def __init__(self, websession, username, password, subscription_id):
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

    async def __api_request(self, url: str, method="get", data=None, return_cookies=False):
        async with getattr(self._websession, method)(url, headers=self.__get_auth_headers(), json=data) as response:
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
                    raise Exception("HTTP Request Error: %s", str(response.status)+" "+str(response.content_type))
            except Exception as err:
                _LOGGER.error("API request error: %s", err)
                return None

    def __get_auth_headers(self):
        _LOGGER.debug("AguasGaia API AuthHeaders")
        headers = {**DEFAULT_HEADERS}
        if self._token is not None:
            headers["X-Auth-Token"] = self._token
        if self._session_cookies is not None:
            headers["Cookie"] = self._session_cookies
        return headers

    def get_subscription(self):
        return self._selected_subscription_id

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
            if self._token is not None and self._session_cookies is not None:
                return True
        return False

    async def get_subscriptions(self):
        _LOGGER.debug("AguasGaia API Subscriptions")

        url = ENDPOINT + SUBSCRIPTIONS_PATH

        self._subscriptions = await self.__api_request(url)
        return self._subscriptions

    async def get_last_invoice(self, subscription_id=None) -> Invoice:
        _LOGGER.debug("AguasGaia API LastDocData")

        subscription_id = subscription_id or self._selected_subscription_id

        url = ENDPOINT + LASTDOC_PATH + "?" + LASTDOC_SUBSCRIPTION_PARAM + "=" + subscription_id

        invoice = await self.__api_request(url)

        self._last_invoice = Invoice(
            invoice_value=invoice[0]["dadosPagamento"]["valor"],
            invoice_attributes=invoice[0]
        )
        return self._last_invoice

    async def get_invoice_history(self, subscription_id=None):
        _LOGGER.debug("AguasGaia API Invoice History")

        subscription_id = subscription_id or self._selected_subscription_id

        today = datetime.now()
        year_ago = today - relativedelta(years=1)
        url = "{url}?{param1}={param1_value}&{param2}={param2_value}&{param3}={param3_value}".format(
            url=ENDPOINT + INVOICEHISTORY_PATH,
            param1=INVOICEHISTORY_ENDDATE_PARAM,
            param1_value="{year}-{month}-{day}".format(
                year=today.year,
                month=today.month,
                day=today.day
            ),
            param2=INVOICEHISTORY_STARTDATE_PARAM,
            param2_value="{year}-{month}-{day}".format(
                year=year_ago.year,
                month=year_ago.month,
                day=year_ago.day
            ),
            param3=INVOICEHISTORY_SUBSCRIPTION_PARAM,
            param3_value=subscription_id
        )

        self._invoice_history = await self.__api_request(url)
        return self._invoice_history

    async def get_last_consumption(self, subscription_id=None) -> Consumption:
        _LOGGER.debug("AguasGaia API Last Consumption")

        subscription_id = subscription_id or self._selected_subscription_id

        url = ENDPOINT + LASTCONSUMPTION_PATH + "?" + LASTCONSUMPTION_SUBSCRIPTION_PARAM + "=" + subscription_id

        self._last_consumption = await self.__api_request(url)

        if len(self._last_consumption[0]["funcoesContador"]) != 0:
            return Consumption(
                consumption_value=self._last_consumption[0]["funcoesContador"][0]["ultimaLeitura"],
                consumption_attributes=self._last_consumption[0]
            )
        else:
            raise Exception("No consumption data found")


