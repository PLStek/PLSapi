import urllib.parse

import requests
from isodate import parse_duration

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"


def extract_video_id_from_url(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)

    if parsed_url.netloc == "youtu.be":
        return parsed_url.path[1:]

    if parsed_url.netloc in ("www.youtube.com", "youtube.com"):
        if parsed_url.path == "/watch":
            params = urllib.parse.parse_qs(parsed_url.query)
            return params.get("v", [None])[0]

        if parsed_url.path[:7] == "/embed/":
            return parsed_url.path.split("/")[2]

        if parsed_url.path[:3] == "/v/":
            return parsed_url.path.split("/")[2]

    return None


def get_youtube_video_duration(video_id: str, api_key: str) -> int:
    payload = {"part": "contentDetails", "id": video_id, "key": api_key}
    response = requests.get(
        YOUTUBE_API_URL,
        params=payload,
    )
    response.raise_for_status()
    raw_date = response.json()["items"][0]["contentDetails"]["duration"]
    return parse_duration(raw_date).total_seconds()
