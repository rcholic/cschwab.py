# (Unofficial) Charles Schwab Stock and Option Trade API Client

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

This is a Python client library for accessing the Charles Schwab stock and option trade API. It provides a convenient way to interact with the Charles Schwab trading platform programmatically.

## Features

- Authenticate with your Charles Schwab account
- Get account information
- Place stock and option trades
- Retrieve trade history
- Monitor real-time market data

## Installation

To install the Charles Schwab API client, you can use pip:
```
pip install CSchwabPy
```

## Usage Example

* Authentication & Get Access Token & Refresh Token

```python

# save these lines in a file named like cschwab.py
from cschwabpy.SchwabAsyncClient import SchwabAsyncClient

app_client_key = "---your-app-client-key-here-"
app_secret = "app-secret"

schwab_client = SchwabAsyncClient(app_client_id=app_client_key, app_secret=app_secret)
schwab_client.get_tokens_manually()

# run in your Terminal, follow the prompt to complete authentication:
> python cschwab.py


# now you should have access token & refresh token downloaded to your device

#----------------
# download SPX option chains
from_date = 2024-07-01
to_date = 2024-07-01
ticker = '$SPX'
asyncio.run(schwab_client.download_option_chain(ticker, from_date, to_date))

```
