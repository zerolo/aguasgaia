import pytest
import aiohttp
from unittest.mock import MagicMock
from http.cookies import SimpleCookie

from aguasgaia import AguasGaia


def create_mock(status_code, get_json_response, post_json_response, cookies):
    mock = aiohttp.ClientSession()
    mock.post = MagicMock()
    mock.post.return_value.__aenter__.return_value.status = status_code
    mock.post.return_value.__aenter__.return_value.content_type = "application/json"
    mock.post.return_value.__aenter__.return_value.cookies = cookies
    mock.post.return_value.__aenter__.return_value.json.return_value = post_json_response

    mock.get = MagicMock()
    mock.get.return_value.__aenter__.return_value.status = status_code
    mock.get.return_value.__aenter__.return_value.content_type = "application/json"
    mock.get.return_value.__aenter__.return_value.cookies = cookies
    mock.get.return_value.__aenter__.return_value.json.return_value = get_json_response

    return mock


@pytest.fixture
def setup_mocks():
    token_response = {
        "token": {
            "token": "my_token"
        }
    }
    token_no_response = {
        "no_token": {
            "no_token": "my_token"
        }
    }
    subscriptions_response = {
        "subscriptions": ["SUB1", "SUB2"]
    }
    invoice_response = [
        {
            "dadosPagamento": {
                "valor": "999"
            }
        }
    ]
    consumption_response = [
        {
            "funcoesContador": [
                {
                    "ultimaLeitura": "9999"
                }
            ]
        }
    ]

    cookies = SimpleCookie()
    cookies.__setitem__("COOKIE1", "A")
    cookies.__setitem__("COOKIE2", "B")

    mock_post_get_subscriptions = create_mock(200, subscriptions_response, token_response, cookies)
    mock_post_get_last_invoice = create_mock(200, invoice_response, token_response, cookies)
    mock_post_get_last_consumption = create_mock(200, consumption_response, token_response, cookies)
    mock_post_failure = create_mock(200, subscriptions_response, token_no_response, cookies)

    '''
    mock_post_success = aiohttp.ClientSession()
    mock_post_success.post = MagicMock()
    mock_post_success.post.return_value.__aenter__.return_value.status = 200
    mock_post_success.post.return_value.__aenter__.return_value.content_type = "application/json"
    mock_post_success.post.return_value.__aenter__.return_value.json.return_value = {
        "token": {
            "token": "my_token"
        }
    }
    
    
    mock_post_failure = aiohttp.ClientSession()
    mock_post_failure.post = MagicMock()
    mock_post_failure.post.return_value.__aenter__.return_value.status = 200
    mock_post_failure.post.return_value.__aenter__.return_value.content_type = "application/json"
    mock_post_failure.post.return_value.__aenter__.return_value.json.return_value = {
        "no_token": {
            "no_token": "my_token"
        }
    }
    '''

    yield {
        "post_get_success": mock_post_get_subscriptions,
        "mock_post_get_last_invoice": mock_post_get_last_invoice,
        "mock_post_get_last_consumption": mock_post_get_last_consumption,
        "post_failure": mock_post_failure
    }


@pytest.mark.asyncio
async def test_login_success(setup_mocks):
    mock = setup_mocks.get("post_get_success")

    aguas = AguasGaia(mock, "", "", "123")
    response = await aguas.login()

    assert response

    await mock.close()


@pytest.mark.asyncio
async def test_login_failed(setup_mocks):
    mock = setup_mocks.get("post_failure")

    aguas = AguasGaia(mock, "", "", "")
    response = await aguas.login()

    assert not response

    await mock.close()


@pytest.mark.asyncio
async def test_get_subscriptions_success(setup_mocks):
    mock_post_get_success = setup_mocks.get("post_get_success")

    aguas = AguasGaia(mock_post_get_success, "", "", "")

    response = await aguas.login()
    assert response

    subscriptions = await aguas.get_subscriptions()
    assert subscriptions.get("subscriptions", None) == ["SUB1", "SUB2"]

    await mock_post_get_success.close()


@pytest.mark.asyncio
async def test_get_last_invoice_success(setup_mocks):
    mock_post_get_last_invoice = setup_mocks.get("mock_post_get_last_invoice")

    aguas = AguasGaia(mock_post_get_last_invoice, "", "", "")

    response = await aguas.login()
    assert response

    invoice = await aguas.get_last_invoice()

    assert invoice is not None
    assert invoice.invoice_value == "999"

    await mock_post_get_last_invoice.close()


@pytest.mark.asyncio
async def test_get_invoice_history_success(setup_mocks):
    mock_post_get_last_invoice = setup_mocks.get("mock_post_get_last_invoice")

    aguas = AguasGaia(mock_post_get_last_invoice, "", "", "")

    response = await aguas.login()
    assert response

    invoices = await aguas.get_invoice_history()

    assert invoices is not None

    await mock_post_get_last_invoice.close()


@pytest.mark.asyncio
async def test_get_last_consumption_success(setup_mocks):
    mock_post_get_last_consumption = setup_mocks.get("mock_post_get_last_consumption")

    aguas = AguasGaia(mock_post_get_last_consumption, "", "", "")

    response = await aguas.login()
    assert response

    consumption = await aguas.get_last_consumption()

    assert consumption is not None

    await mock_post_get_last_consumption.close()
