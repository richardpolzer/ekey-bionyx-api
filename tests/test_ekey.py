import aiohttp
import pytest
from aioresponses import aioresponses

from ekey_bionyxpy import AbstractAuth
from ekey_bionyxpy import BionyxAPI
from ekey_bionyxpy import System
from ekey_bionyxpy import SystemResponse
from ekey_bionyxpy import Webhook
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
        assert comp_system.system_id == systems[0].system_id
        assert comp_system.system_name == systems[0].system_name
        assert comp_system.own_system == systems[0].own_system
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
        assert comp_webhook._expires_at == webhooks[0]._expires_at
        assert comp_webhook._modification_state == webhooks[0]._modification_state
        assert comp_webhook._system_id == webhooks[0]._system_id
        assert comp_webhook._webhook_id == webhooks[0]._webhook_id
        assert comp_webhook._webhook_function_name == webhooks[0]._webhook_function_name
        assert comp_webhook._webhook_location_name == webhooks[0]._webhook_location_name
        m.assert_called_once()
    await session.close()
