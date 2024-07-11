"""Module for interacting with the objects returned by the API."""

from ._typing import FunctionQuotas
from ._typing import SystemResponse
from ._typing import WebhookData
from ._typing import WebhookRename
from ._typing import WebhookResponse
from .auth import AbstractAuth


class Webhook:
    """Class for interacting with webhooks."""

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

    @property
    def webhook_id(self) -> str:
        return self._webhook_id

    @property
    def webhook_function_name(self) -> str:
        return self._webhook_function_name

    @property
    def webhook_location_name(self) -> str:
        return self._webhook_location_name

    @property
    def expires_at(self) -> str:
        return self._expires_at

    @property
    def modification_state(self) -> str:
        return self._modification_state

    async def get_update(self) -> None:
        """Gets the current version of the webhook as stored in the ekey system."""
        resp = await self._auth.request("GET", f"systems/{self._system_id}/function-webhooks/{self._webhook_id}")
        resp.raise_for_status()
        json_data = await resp.json()
        self._update_values(json_data)

    async def delete(self) -> None:
        """Requests deletion of the webhook. User needs to confirm."""
        resp = await self._auth.request("DELETE", f"systems/{self._system_id}/function-webhooks/{self._webhook_id}")
        resp.raise_for_status()
        self._modification_state = "DeleteRequested"

    async def update(self, webhook_data: WebhookData) -> None:
        """Updates the definition of the webhook. User needs to confirm.

        Args:
            webhook_data (WebhookData): The new data for the webhook.
        """
        resp = await self._auth.request(
            "PUT", f"systems/{self._system_id}/function-webhooks/{self._webhook_id}", json=webhook_data
        )
        resp.raise_for_status()
        self._modification_state = "UpdateRequested"

    async def update_name(self, webhook_data: WebhookRename) -> None:
        """Renames the webhook. User does not need to confirm.

        Args:
            webhook_data (WebhookRename): The new name and location
        """
        resp = await self._auth.request(
            "PATCH", f"systems/{self._system_id}/function-webhooks/{self._webhook_id}", json=webhook_data
        )
        resp.raise_for_status()


class System:
    """Class for interacting with a single system."""

    def __init__(self, raw_data: SystemResponse, auth: AbstractAuth):
        self._system_id = raw_data["systemId"]
        self._system_name = raw_data["systemName"]
        self._own_system = raw_data["ownSystem"]
        self._function_webhook_quotas = raw_data["functionWebhookQuotas"]
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

    @property
    def function_webhook_quotas(self) -> FunctionQuotas:
        return self._function_webhook_quotas

    async def get_webhooks(self) -> list[Webhook]:
        """Getting all the webhooks in the system that were set by this client_id.

        Returns:
            list[Webhook]: registered Webhooks
        """
        resp = await self._auth.request("GET", f"systems/{self._system_id}/function-webhooks")
        resp.raise_for_status()
        return [Webhook(wh_data, self._system_id, self._auth) for wh_data in await resp.json()]

    async def get_webhook(self, webhook_id: str) -> Webhook:
        """Gets the webhook with the provided id.

        Args:
            webhook_id (str): ID of the webhook

        Returns:
            Webhook: registerd Webhook

        Raises:
            aiohttp.ClientResponseError: If `Unauthorized - Authorization failed`
            or `Forbidden - Invalid or expired authentication token` or `Not Found`
        """
        resp = await self._auth.request("GET", f"systems/{self._system_id}/function-webhooks/{webhook_id}")
        resp.raise_for_status()
        return Webhook(await resp.json(), self._system_id, self._auth)

    async def add_webhook(self, webhook_data: WebhookData) -> Webhook:
        """Adds a new webhook with the provided data.

        Args:
            webhook_data (WebhookData): Data of the Webhook

        Returns:
            Webhook: registerd webhook
        """
        resp = await self._auth.request("POST", f"systems/{self._system_id}/function-webhooks", json=webhook_data)
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
        resp = await self._auth.request("GET", "systems")
        resp.raise_for_status()
        return [System(system_data, self._auth) for system_data in await resp.json()]
