import aiohttp
import pytest
from aioresponses import aioresponses

from ekey_bionyxpy import AbstractAuth
from ekey_bionyxpy import BionyxAPI
from ekey_bionyxpy import System
from ekey_bionyxpy import SystemResponse
from ekey_bionyxpy import Webhook
from ekey_bionyxpy import WebhookData
from ekey_bionyxpy import WebhookResponse


system_template: SystemResponse = {
    "systemName": "TESTSYSTEM",
    "systemId": "946da01f-9abd-4d9d-80c7-02af85c822a8",
    "ownSystem": True,
}
base_url = "http://test.example.com"

webhook_template: WebhookResponse = {
    "functionWebhookId": "946da01f-9abd-4d9d-80c7-02af85c822a8",
    "integrationName": "Third Party",
    "locationName": "A simple string containing 0 to 128 word, space and punctuation characters.",
    "functionName": "A simple string containing 0 to 50 word, space and punctuation characters.",
    "expiresAt": "2022-05-16T04:11:28.0000000+00:00",
    "modificationState": None,
}

webhook_data_template: WebhookData = {
    "integrationName": "Third Party",
    "locationName": "A simple string containing 0 to 128 word, space and punctuation characters.",
    "functionName": "A simple string containing 0 to 50 word, space and punctuation characters.",
    "definition": {
        "method": "Post",
        "url": "https://www.rfc-editor.org/rfc/rfc3986.html",
        "body": {"contentType": "application/json", "content": "string"},
        "securityLevel": "AllowHttp",
        "authentication": {
            "apiAuthenticationType": "None",
        },
    },
}


class Auth(AbstractAuth):
    def __init__(self, websession: aiohttp.ClientSession, host: str, token: str):
        super().__init__(websession, host)
        self.token = token

    async def async_get_access_token(self) -> str:
        return self.token


@pytest.mark.asyncio
async def test_get_systems():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    api = BionyxAPI(auth)
    with aioresponses() as m:
        m.get(f"{base_url}/systems", payload=[system_template])
        systems = await api.get_systems()
        comp_system = System(system_template, auth)
        assert comp_system.__dict__ == systems[0].__dict__
        m.assert_called_once()
    await session.close()


@pytest.mark.asyncio
async def test_unauthorized():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    api = BionyxAPI(auth)
    with aioresponses() as m:
        m.get(f"{base_url}/systems", status=401)
        with pytest.raises(aiohttp.ClientResponseError, match="401"):
            await api.get_systems()
        m.assert_called_once()
    await session.close()


@pytest.mark.asyncio
async def test_get_webhooks():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.get(f"{base_url}/systems/{system_template['systemId']}/function-webhooks", payload=[webhook_template])
        webhooks = await (System(system_template, auth)).get_webhooks()
        comp_webhook = Webhook(webhook_template, system_template["systemId"], auth)
        assert comp_webhook.__dict__ == webhooks[0].__dict__
        m.assert_called_once()
    await session.close()


@pytest.mark.asyncio
async def test_get_webhook():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.get(
            f"{base_url}/systems/{system_template['systemId']}/function-webhooks/{webhook_template["functionWebhookId"]}",
            payload=webhook_template,
        )
        webhook = await (System(system_template, auth)).get_webhook(webhook_template["functionWebhookId"])
        comp_webhook = Webhook(webhook_template, system_template["systemId"], auth)
        assert comp_webhook.__dict__ == webhook.__dict__
        m.assert_called_once()
    await session.close()


@pytest.mark.asyncio
async def test_add_webhook():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.post(
            f"{base_url}/systems/{system_template['systemId']}/function-webhooks",
            payload=webhook_template,
        )
        webhook = await (System(system_template, auth)).add_webhook(webhook_data_template)
        comp_webhook = Webhook(webhook_template, system_template["systemId"], auth)
        assert comp_webhook.__dict__ == webhook.__dict__
        m.assert_called_once_with(
            "http://test.example.com/systems/946da01f-9abd-4d9d-80c7-02af85c822a8/function-webhooks",
            method="post",
            json=webhook_data_template,
            headers={"authorization": "Bearer not needed"},
        )
    await session.close()
