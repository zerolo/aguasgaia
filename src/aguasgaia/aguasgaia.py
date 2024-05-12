import logging
import aiohttp
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

    def __init__(self, websession, username, password):
        self.last_invoice = None
        self.last_consumption = None
        self.invoice_history = None
        self._last_invoice = None
        self.selected_subscription_id = None
        self.subscriptions = None
        self.session_cookies = None
        self.token = None
        self.websession = websession
        self.username = username
        self.password = password

    async def login(self):
        _LOGGER.debug("AguasGaia API Login")
        url = ENDPOINT + LOGIN_PATH

        data = {
            USER_PARAM: self.username,
            PWD_PARAM: self.password
        }

        async with self.websession.post(url, headers=DEFAULT_HEADERS, json=data) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    res = await response.json()
                    self.token = res["token"]["token"]
                    self.session_cookies = "".join([x.key + "=" + x.value + ";" for x in self.websession.cookie_jar])
                    return res
                raise Exception("Can't login in the API")
            except aiohttp.ClientError as err:
                _LOGGER.error("Login error: %s", err)
                return

    def get_auth_headers(self):
        _LOGGER.debug("AguasGaia API AuthHeaders")
        return {
            **DEFAULT_HEADERS,
            "X-Auth-Token": self.token,
            "Cookie": self.session_cookies
        }

    async def get_subscriptions(self):
        _LOGGER.debug("AguasGaia API Subscriptions")
        url = ENDPOINT + SUBSCRIPTIONS_PATH
        headers = self.get_auth_headers()
        async with self.websession.get(url, headers=headers) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    res = await response.json()
                    self.subscriptions = res
                    self.selected_subscription_id = str(res[0]["subscriptionId"])
                    return res
                raise Exception("Can't retrieve subscriptions")
            except aiohttp.ClientError as err:
                _LOGGER.error("Subscriptions Error: %s", err)

    async def get_last_invoice(self, subscription_id=None) -> Invoice:
        _LOGGER.debug("AguasGaia API LastDocData")


        if subscription_id is None:
            if self.selected_subscription_id is not None:
                subscription_id = self.selected_subscription_id
            else:
                raise Exception("No subscriptionID found")

        url = ENDPOINT + LASTDOC_PATH + "?" + LASTDOC_SUBSCRIPTION_PARAM + "=" + subscription_id
        headers = self.get_auth_headers()
        async with self.websession.get(url, headers=headers) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    self._last_invoice = await response.json()
                    if len(self._last_invoice) == 0:
                        raise Exception("Empty Response")
            except Exception as err:
                _LOGGER.error("last document data Error: %s", err)
            
            self.last_invoice = Invoice(
                invoice_value=self._last_invoice[0]["dadosPagamento"]["valor"],
                invoice_attributes=self._last_invoice[0]
            )
            return self.last_invoice

    async def get_invoice_history(self, subscription_id=None):
        _LOGGER.debug("AguasGaia API InvoiceHistory")

        if subscription_id is None:

            if self.selected_subscription_id is not None:
                subscription_id = self.selected_subscription_id
            else:
                raise Exception("No subscriptionID found")

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
        print(url)
        headers = self.get_auth_headers()
        async with self.websession.get(url, headers=headers) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    res = await response.json()
                    self.invoice_history = res
                    return res
                raise Exception("Can't retrieve invoice history data")
            except aiohttp.ClientError as err:
                _LOGGER.error("invoice history data Error: %s", err)
                return

    async def get_last_consumption(self, subscription_id=None) -> Consumption:
        _LOGGER.debug("AguasGaia API Last Consumption")

        if subscription_id is None:
            if self.selected_subscription_id is not None:
                subscription_id = self.selected_subscription_id
            else:
                raise Exception("No subscriptionID found")

        url = ENDPOINT + LASTCONSUMPTION_PATH + "?" + LASTCONSUMPTION_SUBSCRIPTION_PARAM + "=" + subscription_id
        headers = self.get_auth_headers()
        async with self.websession.get(url, headers=headers) as response:
            try:
                if response.status == 200 and response.content_type == JSON_CONTENT:
                    self.last_consumption = await response.json()
                    if len(self.last_consumption) == 0:
                        raise Exception("Empty Response")
            except Exception as err:
                _LOGGER.error("last consumption data Error: %s", err)

            if len(self.last_consumption[0]["funcoesContador"]) != 0:
                return Consumption(
                    consumption_value=self.last_consumption[0]["funcoesContador"][0]["ultimaLeitura"],
                    consumption_attributes=self.last_consumption[0]
                )
