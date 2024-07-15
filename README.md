# API for the ekey bionyx system - Python

[![Lint & Test](https://github.com/richardpolzer/ekey-bionyx-api/actions/workflows/lint_test.yml/badge.svg?branch=main)](https://github.com/richardpolzer/ekey-bionyx-api/actions/workflows/lint_test.yml)
[![codecov](https://codecov.io/github/richardpolzer/ekey-bionyx-api/branch/main/graph/badge.svg?token=MXJCFJZO5I)](https://codecov.io/github/richardpolzer/ekey-bionyx-api)

## Overview

The ekey_bionyxpy library can be used to interact with the API of the ekey bionyx biometric systems. All the current functions of the API are mapped. The library is written to completely take advantage of async code in Python.

---

## Features

- **Get all systems attached to the user**
- **Get all webhooks added by the integration**
- **Add new webhooks**
- **Update existing webhooks**

## Enabling the API

The system must be setup in the online mode. In your app please enable the API by following the picture
![Erklärung](https://github.com/user-attachments/assets/58602bed-af94-43a7-8bfa-aaeaa82e6cde)

After the API is enabled you can use the library by first implementing AbstractAuth with your custom token handling.

In the example a token manager is used. You can however use any mechanism you like to retieve an access token.

```python
from ekey_bionyxpy import AbstractAuth

class Auth(AbstractAuth):
    def __init__(self, websession: ClientSession, host: str, token_manager):
        """Initialize the auth."""
        super().__init__(websession, host)
        self.token_manager = token_manager

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        if self.token_manager.is_token_valid():
            return self.token_manager.access_token

        await self.token_manager.fetch_access_token()
        await self.token_manager.save_access_token()

        return self.token_manager.access_token
```

Once the Authentication is dealt with you can use the lib like so:

```python
async def main() -> None:
    async with aiohttp.ClientSession() as session:
        # Aquire token manager here
        auth = Auth(
            session,
            "https://api.bionyx.io/3rd-party/api",
            token_manager,
        )
        api = BionyxAPI(auth)
        systems = await api.get_systems()
        webhooks = await systems[0].get_webhooks()


asyncio.run(main())
```
