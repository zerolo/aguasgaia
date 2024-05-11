ENDPOINT = "https://uportal.livre.cgi.com/uPortal2/gaia"
LOGIN_PATH = "/login"
SUBSCRIPTIONS_PATH = "/Subscription/listSubscriptions"
LASTDOC_PATH = "/Billing/getDadosUltimoDocumento"
INVOICEHISTORY_PATH = "/Billing/getFaturasContractoByIntervalo"
LASTCONSUMPTION_PATH = "/leituras/getContadores"

LASTDOC_SUBSCRIPTION_PARAM = "subscriptionId"
INVOICEHISTORY_SUBSCRIPTION_PARAM = "subscriptionId"
LASTCONSUMPTION_SUBSCRIPTION_PARAM = "subscriptionId"
INVOICEHISTORY_ENDDATE_PARAM = "dataFinal"
INVOICEHISTORY_STARTDATE_PARAM = "dataInicial"

JSON_CONTENT = "application/json"

DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=utf-8"
}

USER_PARAM = "username"
PWD_PARAM = "password"
