"""Module for interacting with the objects returned by the API."""

from enum import Enum
from typing import Any
from typing import Literal
from typing import NotRequired
from typing import TypedDict

from .auth import AbstractAuth


class Webhook:
    """Class for interacting with webhooks."""

    def __init__(self, raw_data: WebhookResponse, system_id: str, auth: AbstractAuth) -> None:
        self._system_id = system_id
        self._auth = auth
        self._update_values(raw_data)

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


class FunctionQuotas(TypedDict):
    free: int
    used: int


class SystemResponse(TypedDict):
    systemName: str
    systemId: str
    ownSystem: bool
    functionWebhookQuotas: FunctionQuotas


class WebhookResponse(TypedDict):
    functionWebhookId: str
    integrationName: str
    locationName: str
    functionName: str
    expiresAt: str
    modificationState: str | None


class WebhookDefinitionMethods(Enum):
    GET = "Get"
    POST = "Post"
    PUT = "Put"
    DELETE = "Delete"
    PATCH = "Patch"
    HEAD = "Head"


class WebhookDefinitionSecurityLevel(Enum):
    TLSWITHCACHECK = "TlsWithCACheck"
    TLSALLOWSELFFIGNED = "TlsAllowSelfSigned"
    ALLOWHTTP = "AllowHttp"
    TLSPINNEDCERTIFICATE = "TlsPinnedCertificate"


class WebhookDefinitionBody(TypedDict):
    contentType: NotRequired[str]
    content: str | dict


class WebhookDefinitionAuthenticationType(Enum):
    NONE = "None"
    OAUTH2ACCESSTOKEN = "OAuth2IssuedAccessToken"
    OAUTH2REFRESHTOKEN = "OAuth2IssuedRefreshToken"


class WebhookDefinitionAuthentication(TypedDict):
    apiAuthenticationType: (
        WebhookDefinitionAuthenticationType | Literal["None", "OAuth2IssuedAccessToken", "OAuth2IssuedRefreshToken"]
    )
    expiresIn: NotRequired[int]
    clientId: NotRequired[str]
    accessToken: NotRequired[str]
    refreshToken: NotRequired[str]
    tokenEndoint: NotRequired[str]
    scope: NotRequired[str]
    authorizationEndpoint: NotRequired[str]


class WebhookDefinition(TypedDict):
    method: WebhookDefinitionMethods | Literal["Get", "Post", "Put", "Delete", "Patch", "Head"]
    url: str
    body: NotRequired[WebhookDefinitionBody]
    securityLevel: (
        WebhookDefinitionSecurityLevel
        | Literal["AllowHttp", "TlsWithCACheck", "TlsAllowSelfSigned", "TlsPinnedCertificate"]
    )
    pinnedCertificate: NotRequired[str]
    timeout: NotRequired[int]
    additionalHttpHeaders: NotRequired[Any]
    authentication: WebhookDefinitionAuthentication


class WebhookData(TypedDict):
    functionWebhookId: NotRequired[str]
    integrationName: str
    locationName: NotRequired[str]
    functionName: NotRequired[str]
    expiresAt: NotRequired[str]
    modificationState: NotRequired[str]
    definition: WebhookDefinition


class WebhookRename(TypedDict):
    locationName: NotRequired[str]
    functionName: NotRequired[str]