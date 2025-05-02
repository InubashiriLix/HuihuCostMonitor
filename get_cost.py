import requests
from datetime import datetime
from dotenv import load_dotenv
import os
from typing import Optional

from get_info import get_new_token, get_room_id

load_dotenv()

# 从环境变量中加载配置
url = os.getenv("API_URL")
user_agent = os.getenv("USER_AGENT")
content_type = os.getenv("CONTENT_TYPE")
accept = os.getenv("ACCEPT")

camp = os.getenv("CAMPUS_TITLE")
room = os.getenv("ROOM_MATCH")

if camp is None:
    raise EnvironmentError("camp or room parse failed")

if room is None:
    raise EnvironmentError("room match parse failed")

if url is None:
    raise EnvironmentError("url parse failed")


def get_rest_cost() -> Optional[float]:
    satoken_ = get_new_token()
    satoken = satoken_[1]

    if camp is None:
        raise EnvironmentError("camp or room parse failed")

    room_id = get_room_id(*satoken_, campus_title=camp, room_match=room)
    print(room_id)

    params = {"roomId": room_id}
    headers = {
        "User-Agent": user_agent,
        "satoken": satoken,
        "Accept": accept,
        "Content-Type": content_type,
    }
    try:
        if url is None:
            raise Exception("env: dotnev url is None")

        print(f"Requesting URL: {url}")
        print(f"Parameters: {params}")

        response = requests.get(
            url, params=params, headers=headers, timeout=10
        )  # timeout added for safety

        # debug
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"rest_cost: {data['result']}")
            return data["result"]
        else:
            print("request failed, return code:", response.status_code)
            return None

    except KeyboardInterrupt:
        print("\ninterrupted，exiting")
    except requests.exceptions.RequestException as e:
        print(f"error while requesting: {e}")
        return None


if __name__ == "__main__":
    get_rest_cost()
