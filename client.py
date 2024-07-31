"""
    QuantJourney API client library

    Key features:
    - Asynchronous API requests
    - Authentication
    - Fetch historical OHLCV data

    author: QuantJourney
    date: 2024-07-30
"""
import pandas as pd
import aiohttp
import asyncio
from typing import Optional


# QuantJourney class ---------------------------------------------------
class QuantJourney:
    def __init__(self, user_token: Optional[str] = None, admin_token: Optional[str] = None):
        self.base_url = "https://api.quantjourney.pro"  # Predefined URL
        self.user_token = user_token
        self.admin_token = admin_token

    async def async_authenticate(self, username: str, password: str):
        url = f"{self.base_url}/token"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={"username": username, "password": password}) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_token = data["access_token"]
                else:
                    raise Exception(f"Authentication failed: {await response.text()}")

    def authenticate(self, username: str, password: str):
        return asyncio.run(self.async_authenticate(username, password))

    async def async_get_ohlcv(self, ticker: str, exchange: str, period_start: str, period_end: str,
                              source: str = "yf", granularity: str = "1d",
                              read_db: bool = False, write_db: bool = False):
        url = f"{self.base_url}/ohlcv/{ticker}"
        params = {
            "exchange": exchange,
            "period_start": period_start,
            "period_end": period_end,
            "source": source,
            "granularity": granularity,
            "read_db": str(read_db).lower(),
            "write_db": str(write_db).lower()
        }
        headers = {}
        if self.admin_token:
            params["admin_token"] = self.admin_token
        elif self.user_token:
            headers["Authorization"] = f"Bearer {self.user_token}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        df = pd.DataFrame(data['data'])
                        df['datetime'] = pd.to_datetime(df['datetime'])
                        df.set_index('datetime', inplace=True)
                        return df
                    else:
                        raise Exception(f"API request failed with status {response.status}: {await response.text()}")
        except aiohttp.ClientError as e:
            raise Exception(f"Network error occurred: {str(e)}")

    def get_ohlcv(self, ticker: str, exchange: str, period_start: str, period_end: str,
                  source: str = "yf", granularity: str = "1d",
                  read_db: bool = False, write_db: bool = False):
        return asyncio.run(self.async_get_ohlcv(ticker, exchange, period_start, period_end,
                                                source, granularity, read_db, write_db))

