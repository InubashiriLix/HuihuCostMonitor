from json import load
from typing import Optional
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# TODO: put in the .env

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781 "
    "(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF "
    "WindowsWechat(0x63090c33)XWEB/13639"
)
HEADERS = {"User-Agent": USER_AGENT}
HEADERS_BASE = {"User-Agent": USER_AGENT}


def get_new_token() -> tuple[str, str]:
    """return (token_name, token_value)"""
    OPEN_ID = os.getenv("OPEN_ID")
    UNION_ID = os.getenv("UNION_ID")
    CERT_URL = os.getenv("CERT_URL")
    if OPEN_ID is None:
        raise EnvironmentError("OPEN_ID parse failed")
    if UNION_ID is None:
        raise EnvironmentError("UNION_ID parse failed")
    if CERT_URL is None:
        raise EnvironmentError("CERT_URL parse failed")

    r = requests.get(
        CERT_URL,
        params={"openId": OPEN_ID, "unionId": UNION_ID},
        headers=HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()["data"]
    return data.get("tokenName", "satoken"), data["token"]


def get_room_id(
    token_name: str, token_val: str, campus_title: str, room_match: Optional[str] = None
) -> str:
    """
    campus_title : “文缘学生公寓” / “文星学生公寓” ……
    room_match   : 用来匹配 address 或 userSn（可选，
                   传 '1107' 就会找地址里带 1107 的那间）

    过程：
        1. /proxy/qy/sdcz/queryByTeam?team=水电充值
           └─ 找到 title==campus_title → 拿 param (=areaId)
        2. /proxy/qy/sdcz/getDefault?areaId=...
           └─ 取 result[园区数组][0].id 作为 roomId
    """
    hdr = HEADERS_BASE | {token_name: token_val}

    area_resp = requests.get(
        "https://api.215123.cn/proxy/qy/sdcz/queryByTeam",
        params={"team": "水电充值"},
        headers=hdr,
        timeout=10,
    ).json()["result"]

    try:
        area_id = next(a["param"] for a in area_resp if a["title"] == campus_title)
    except StopIteration:
        raise ValueError(f"campus_not_found {campus_title}")

    # step-2 取房间列表
    lst_resp = requests.get(
        "https://api.215123.cn/proxy/qy/sdcz/getDefault",
        params={"areaId": area_id},
        headers=hdr,
        timeout=10,
    ).json()["result"]

    key = next(k for k in lst_resp if lst_resp[k])  # find the first not empty key
    rooms = lst_resp[key]

    if room_match:
        rooms = [
            r
            for r in rooms
            if room_match in (r.get("address", "") + r.get("userSn", ""))
        ]

    print(rooms)

    if not rooms:
        raise ValueError("could not find room with satisfied condition")
    room_id = rooms[0]["id"]
    print(f"[{datetime.now()}] found roomId = {room_id}")
    return room_id


if __name__ == "__main__":
    camp = os.getenv("CAMPUS_TITLE")
    room = os.getenv("ROOM_MATCH")
    if camp is None or room is None:
        raise EnvironmentError()
    tn, tv = get_new_token()
    rid = get_room_id(tn, tv, campus_title=camp, room_match=room)
