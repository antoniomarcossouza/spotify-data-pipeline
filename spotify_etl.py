"""Module with functions used to extract data from the Spotify API."""

import base64
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
import requests

from exceptions import APIRequestException

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BASE64_ID_SECRET = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()


def get_yesterday_unix_timestamp() -> int:
    """Get yesterday's Unix timestamp in milliseconds."""

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    return int(yesterday.timestamp()) * 1000


def get_token() -> str:
    """Get Spotify API token."""

    url = "https://accounts.spotify.com/api/token"
    response = requests.post(
        url,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {BASE64_ID_SECRET}",
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": os.getenv("REFRESH_TOKEN"),
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise APIRequestException(url=url, response=response.json())

    return response.json()["access_token"]


def get_recently_played(token: str) -> dict:
    """Get recently played tracks."""

    url = "https://api.spotify.com/v1/me/player/recently-played"
    response = requests.get(
        url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        params={"limit": 50, "after": get_yesterday_unix_timestamp()},
        timeout=60,
    )

    if response.status_code != 200:
        raise APIRequestException(url=url, response=response.json())

    return response.json()


def get_artists_genres(artist_id: str, token: str) -> list:
    """Get artists genres"""

    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )

    if response.status_code != 200:
        raise APIRequestException(url=url, response=response.json())

    return response.json()["genres"]
