import aiohttp
import pytest
from aioresponses import aioresponses

from ekey_bionyxpy import AbstractAuth
from ekey_bionyxpy import BionyxAPI
from ekey_bionyxpy import System
from ekey_bionyxpy import SystemResponse
from ekey_bionyxpy import Webhook
from ekey_bionyxpy import WebhookData
from ekey_bionyxpy import WebhookRename
from ekey_bionyxpy import WebhookResponse


system_template: SystemResponse = {
    "systemName": "TESTSYSTEM",
    "systemId": "946da01f-9abd-4d9d-80c7-02af85c822a8",
    "ownSystem": True,
    "functionWebhookQuotas": {"free": 5, "used": 0},
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

webhook_patch_data: WebhookRename = {"functionName": "A simple string", "locationName": "0 to 50 word"}

system_id = system_template["systemId"]
webhook_id = webhook_template["functionWebhookId"]


class Auth(AbstractAuth):
    def __init__(self, websession: aiohttp.ClientSession, host: str, token: str):
        super().__init__(websession, host)
        self.token = token

    async def async_get_access_token(self) -> str:
        return self.token


@pytest.mark.asyncio
async def test_request_with_headers():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.get(f"{base_url}")
        resp = await auth.request("GET", "", headers={"test": "test"})
        resp.raise_for_status()
        m.assert_called_once_with(
            f"{base_url}",
            method="get",
            headers={"authorization": "Bearer not needed", "test": "test"},
        )
    await session.close()


@pytest.mark.asyncio
async def test_system():  # noqa: RUF029
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    system = System(system_template, auth)
    assert system.system_id == system_template["systemId"]
    assert system.system_name == system_template["systemName"]
    assert system.own_system == system_template["ownSystem"]
    assert system.function_webhook_quotas == system_template["functionWebhookQuotas"]


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
async def test_webhook():  # noqa: RUF029
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    webhook = Webhook(webhook_template, system_id, auth)
    assert webhook.webhook_id == webhook_template["functionWebhookId"]
    assert webhook.webhook_function_name == webhook_template["functionName"]
    assert webhook.webhook_location_name == webhook_template["locationName"]
    assert webhook.expires_at == webhook_template["expiresAt"]
    assert webhook.modification_state == webhook_template["modificationState"]


@pytest.mark.asyncio
async def test_get_webhooks():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.get(f"{base_url}/systems/{system_id}/function-webhooks", payload=[webhook_template])
        webhooks = await (System(system_template, auth)).get_webhooks()
        comp_webhook = Webhook(webhook_template, system_id, auth)
        assert comp_webhook.__dict__ == webhooks[0].__dict__
        m.assert_called_once()
    await session.close()


@pytest.mark.asyncio
async def test_get_webhook():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.get(
            f"{base_url}/systems/{system_id}/function-webhooks/{webhook_id}",
            payload=webhook_template,
        )
        webhook = await (System(system_template, auth)).get_webhook(webhook_id)
        comp_webhook = Webhook(webhook_template, system_id, auth)
        assert comp_webhook.__dict__ == webhook.__dict__
        m.assert_called_once()
    await session.close()


@pytest.mark.asyncio
async def test_add_webhook():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.post(
            f"{base_url}/systems/{system_id}/function-webhooks",
            payload=webhook_template,
        )
        webhook = await (System(system_template, auth)).add_webhook(webhook_data_template)
        comp_webhook = Webhook(webhook_template, system_id, auth)
        assert comp_webhook.__dict__ == webhook.__dict__
        m.assert_called_once_with(
            f"{base_url}/systems/{system_id}/function-webhooks",
            method="post",
            json=webhook_data_template,
            headers={"authorization": "Bearer not needed"},
        )
    await session.close()


@pytest.mark.asyncio
async def test_webhook_get_update():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.get(
            f"{base_url}/systems/{system_id}/function-webhooks/{webhook_id}",
            payload=webhook_template,
        )
        webhook = Webhook(webhook_template, system_id, auth)
        webhook._webhook_function_name = "Test"
        assert webhook._webhook_function_name == "Test"
        await webhook.get_update()
        comp_webhook = Webhook(webhook_template, system_id, auth)
        assert comp_webhook.__dict__ == webhook.__dict__
        m.assert_called_once()
    await session.close()


@pytest.mark.asyncio
async def test_webhook_delete():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")

    with aioresponses() as m:
        m.delete(f"{base_url}/systems/{system_id}/function-webhooks/{webhook_id}")
        webhook = Webhook(webhook_template, system_id, auth)
        await webhook.delete()
        assert webhook._modification_state == "DeleteRequested"
        m.assert_called_once_with(
            f"{base_url}/systems/{system_id}/function-webhooks/{webhook_id}",
            method="delete",
            headers={"authorization": "Bearer not needed"},
        )
    await session.close()


@pytest.mark.asyncio
async def test_webhook_update():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.put(f"{base_url}/systems/{system_id}/function-webhooks/{webhook_id}")
        webhook = Webhook(webhook_template, system_id, auth)
        await webhook.update(webhook_data_template)
        assert webhook._modification_state == "UpdateRequested"
        m.assert_called_once_with(
            f"{base_url}/systems/{system_id}/function-webhooks/{webhook_id}",
            method="put",
            json=webhook_data_template,
            headers={"authorization": "Bearer not needed"},
        )
    await session.close()


@pytest.mark.asyncio
async def test_webhook_patch():
    session = aiohttp.ClientSession()
    auth = Auth(session, base_url, "not needed")
    with aioresponses() as m:
        m.patch(f"{base_url}/systems/{system_id}/function-webhooks/{webhook_id}")
        webhook = Webhook(webhook_template, system_id, auth)
        await webhook.update_name(webhook_patch_data)
        m.assert_called_once_with(
            f"{base_url}/systems/{system_id}/function-webhooks/{webhook_id}",
            method="patch",
            json=webhook_patch_data,
            headers={"authorization": "Bearer not needed"},
        )
    await session.close()
