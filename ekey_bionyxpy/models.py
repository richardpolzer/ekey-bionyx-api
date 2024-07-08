"""Module for interacting with the objects returned by the API."""

from ._typing import SystemResponse
from ._typing import WebhookData
from ._typing import WebhookResponse
from .auth import AbstractAuth


class Webhook:
    def __init__(self, raw_data: WebhookResponse, system_id: str, auth: AbstractAuth) -> None:
        self._system_id = system_id
        self._auth = auth
        self._update_values(raw_data)
        print(str(self.__dict__))

    def _update_values(self, data: WebhookResponse) -> None:
        self._webhook_id = data["functionWebhookId"]
        self._webhook_function_name = data["functionName"]
        self._webhook_location_name = data["locationName"]
        self._expires_at = data["expiresAt"]
        self._modification_state = data["modificationState"]

    async def get_update(self) -> None:
        resp = await self._auth.request("get", f"systems/{self._system_id}/function-webhooks/{self._webhook_id}")
        resp.raise_for_status()
        json_data = await resp.json()
        self._update_values(json_data)
        print(str(self.__dict__))

    async def delete(self) -> None:
        resp = await self._auth.request("delete", f"systems/{self._system_id}/function-webhooks/{self._webhook_id}")
        resp.raise_for_status()
        self._modification_state = "DeleteRequested"

    async def update(self, webhook_data: WebhookData) -> None:
        resp = await self._auth.request("put", f"systems/{self._system_id}/function-webhooks", json=webhook_data)
        resp.raise_for_status()
        self._modification_state = "UpdateRequested"


class System:
    def __init__(self, raw_data: SystemResponse, auth: AbstractAuth):
        self._system_id = raw_data["systemId"]
        self._system_name = raw_data["systemName"]
        self._own_system = raw_data["ownSystem"]
        self._auth = auth

    @property
    def system_id(self) -> str:
        return self._system_id

    @property
    def system_name(self) -> str:
        return self._system_name

    @property
    def own_system(self) -> bool:
        return self._own_system

    async def get_webhooks(self) -> list[Webhook]:
        resp = await self._auth.request("get", f"systems/{self._system_id}/function-webhooks")
        resp.raise_for_status()
        return [Webhook(wh_data, self._system_id, self._auth) for wh_data in await resp.json()]

    async def get_webhook(self, webhook_id: str) -> Webhook:
        resp = await self._auth.request("get", f"systems/{self._system_id}/function-webhooks/{webhook_id}")
        resp.raise_for_status()
        return Webhook(await resp.json(), self._system_id, self._auth)

    async def add_webhook(self, webhook_data: WebhookData) -> Webhook:
        resp = await self._auth.request("post", f"systems/{self._system_id}/function-webhooks", json=webhook_data)
        resp.raise_for_status()
        return Webhook(await resp.json(), self._system_id, self._auth)


class BionyxAPI:
    """Base class for interacting with the API and get all systems attached to the user."""

    def __init__(self, auth: AbstractAuth) -> None:
        """Initialize the API with an Auth object.

        Args:
            auth (AbstractAuth): Auth object that provides the base URL
        """
        self._auth = auth

    async def get_systems(self) -> list[System]:
        """Gets all the Systems attached to the currently logged in user.

        Returns:
            list[System]: List of Systems the user has access to
        """
        resp = await self._auth.request("get", "systems")
        resp.raise_for_status()
        return [System(system_data, self._auth) for system_data in await resp.json()]
