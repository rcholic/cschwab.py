# (Unofficial) Charles Schwab Stock and Option Trade API Client

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

This is a Python client library for accessing the Charles Schwab stock and option trade API. It provides a convenient way to interact with the Charles Schwab trading platform programmatically.

## Features

- [x] Authenticate with your Charles Schwab account
- [X] Automated refreshing of access token
- [x] Download option chain data
- [x] Get account information
- [x] Place stock and option trades
- Retrieve trade history [Work in Progress]
- Monitor real-time market data [TODO]

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
ticker = '$SPX'
# get option expirations:
expiration_list = await schwab_client.get_option_expirations_async(underlying_symbol = ticker)

# download SPX option chains
from_date = 2024-07-01
to_date = 2024-07-01

opt_chain_result = await schwab_client.download_option_chain_async(ticker, from_date, to_date)

# get call-put dataframe pairs by expiration
opt_df_pairs = opt_chain_result.to_dataframe_pairs_by_expiration()

for df in opt_df_pairs:
    print(df.expiration)
    print(f"call dataframe size: {df.call_df.shape}. expiration: {df.expiration}")
    print(f"put dataframe size: {df.put_df.shape}. expiration: {df.expiration}")
    print(df.call_df.head(5))
    print(df.put_df.head(5))

```
