from enum import Enum
from typing import Any
from typing import Literal
from typing import NotRequired
from typing import TypedDict


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
