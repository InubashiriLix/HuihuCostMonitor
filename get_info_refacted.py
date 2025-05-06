from json import load
from typing import Optional, Tuple
import requests

from datetime import datetime
import os

from dotenv import load_dotenv

import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(funcName)s]- %(message)s",
)

load_dotenv()

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781 "
    "(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF "
    "WindowsWechat(0x63090c33)XWEB/13639"
)
HEADERS = {"User-Agent": USER_AGENT}

# load OPEN_ID
OPEN_ID = os.getenv("OPEN_ID")
if OPEN_ID is None:
    raise EnvironmentError("OPEN_ID parse failed, check OPEN_ID in .env !!!")


def get_new_token() -> tuple[str, str]:
    """
    this function is used to get a new token from the server.
    return (token_name, token_value)
    eg. ("satoken", "sfdfiihsadfas_token_value")
    """

    CERT_URL = "https://api.215123.cn/web-app/auth/certificateLogin"

    try:
        r = requests.get(
            CERT_URL,
            params={"openId": OPEN_ID},
            headers=HEADERS,
            timeout=10,
            verify=False,
        )

        r.raise_for_status()

    except requests.RequestException as e:
        logging.error("get token failed")
        raise e

    logging.info("get token response:")
    logging.info(r.json())

    data = r.json()["data"]
    rtn = data.get("tokenName", "satoken"), data["token"]

    if rtn is None or len(rtn) != 2:
        logging.error("get token failed")
        raise ValueError("get token failed")

    logging.info("get token name and satoken: ")
    logging.info(rtn)
    return rtn


def get_apartment_name(satoken: str) -> str:
    """
    @param str satoken: the token value, which is used to get the apartment name
    return the apartment name
    """
    logging.info("begin get apartment name")

    GET_CODE_URL = "https://api.215123.cn/pms/welcome/make-code-info"

    try:
        resp = requests.get(
            GET_CODE_URL,
            params={"satoken": satoken},
            headers=HEADERS,
            timeout=10,
            verify=False,
        )

        resp.raise_for_status()

    except requests.RequestException as e:
        logging.error("get apartment name failed")
        raise e

    data = resp.json()
    if data is None:
        logging.error("get apartment name failed")
        raise ValueError("get apartment name failed")
    if data["code"] != 200:
        logging.error("get apartment name failed without 200")
        raise ValueError("get apartment name failed")

    logging.info("get apartment name response:")
    logging.info(data)

    try:
        rtn_apratment_name = data.get("data").get("apartment").split(" ")[0]
    except Exception as e:
        logging.error("failed to parse apartment name")
        raise e

    logging.info("get apartment name:")
    logging.info(rtn_apratment_name)
    return rtn_apratment_name


def get_apartment_map() -> dict[str, str]:
    """返回 {'文星学生公寓': '1', ...}"""
    url = "https://api.215123.cn/proxy/qy/sdcz/queryByTeam"
    session = requests.Session()
    resp = session.get(
        url,
        params={"team": "水电充值"},
        proxies={"http": None, "https": None},  # type: ignore[arg-type]
        verify=False,
        timeout=8,
    )
    resp.raise_for_status()
    return {it["title"]: it["param"] for it in resp.json()["result"]}


def get_balance(satoken: str, apartment_name: str) -> Optional[float]:
    # WARNING: this operation need python 3.10+
    hdr = HEADERS | {"satoken": satoken}

    if apartment_name == "文缘学生公寓":
        areaid = get_apartment_map()["文缘学生公寓"]
        BALANCE_URL_WENYUAN = "https://api.215123.cn/proxy/qy/sdcz/balance"

        # get the room_id
        try:
            lst_resp = requests.get(
                "https://api.215123.cn/proxy/qy/sdcz/getDefault",
                params={"areaId": areaid},
                headers=hdr,
                timeout=10,
            )
            if (lst_resp.status_code != 200) or (lst_resp.json() is None):
                logging.error("get room id failed")
                return None

            lst_resp = lst_resp.json()["result"]

            room_id = lst_resp.get("wenyuan")[0].get("id")
            logging.info(f"get room id: {room_id}")

        except requests.RequestException as e:
            logging.error("get room id failed")
            raise e

        # get the balance
        try:
            params_wenyuan = {"roomId": room_id}

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639",
                "satoken": satoken,
                "Accept": "*/*",
                "Content-Type": "application/json",
            }

            response = requests.get(
                BALANCE_URL_WENYUAN, params=params_wenyuan, headers=headers, timeout=10
            )  # timeout added for safety
            if response.status_code != 200:
                logging.error(
                    "request balance failed, return code:", response.status_code
                )
                return None

            rtn_balance = response.json().get("result")
            if rtn_balance is None:
                logging.error("get balance from response failed")
                return None

            logging.info(f"get balance: {rtn_balance}")
            return rtn_balance

        except KeyboardInterrupt:
            logging.error("interrupted，exiting")
            exit(0)
        except requests.exceptions.RequestException as e:
            logging.error(f"error while requesting: {e}")
            raise e

    elif apartment_name == "文星学生公寓":
        areaid = get_apartment_map()["文星学生公寓"]
        BALANCE_URL_WENXING = "https://api.215123.cn/proxy/qy/sdcz/getRoomBalance"

        try:
            lst_resp = requests.get(
                "https://api.215123.cn/proxy/qy/sdcz/getDefault",
                params={"areaId": areaid},
                headers=hdr,
                timeout=10,
            ).json()["result"]
            logging.info(f"get response: {lst_resp}")

            apartment_id = lst_resp.get("other")[0].get("apartmentId")
            room_id = lst_resp.get("other")[0].get("id")

        except requests.RequestException as e:
            logging.error("get room id failed")
            raise e

        # get the balance
        params_wenxing = {"apartmentId": apartment_id, "roomId": room_id}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639",
            "satoken": satoken,
            "Accept": "*/*",
            "Content-Type": "application/json",
        }
        # TODO: add all response code decision

        try:
            response = requests.get(
                BALANCE_URL_WENXING, params=params_wenxing, headers=headers, timeout=10
            )  # timeout added for safety
            if response.status_code != 200:
                logging.error(
                    "request balance failed, return code:", response.status_code
                )
                return None

            rtn_balance = response.json().get("result")
            if rtn_balance is None:
                logging.error("get balance from response failed")
                return None

            return rtn_balance

        except KeyboardInterrupt:
            logging.error("interrupted，exiting")
            exit(0)
        except requests.exceptions.RequestException as e:
            logging.error(f"error while requesting: {e}")
            raise e
    else:
        raise ValueError(
            "apartment name not supported, we only support 文缘学生公寓 and 文星学生公寓"
        )


def _get_cost_() -> Optional[float]:
    """
    WARNING:
    JUST FOR TEST
    this function is used to get the cost of the apartment.
    """
    satoken_val = get_new_token()[1]
    apt_name = get_apartment_name(satoken_val)
    return get_balance(satoken_val, apt_name)


if __name__ == "__main__":
    # # test for get_apartment_name function
    # try:
    #     token_name, token_val = get_new_token()
    #     logging.info(f"token_name: {token_name}, token_val: {token_val}")
    #     apartment_name = get_apartment_name(token_val)
    #     logging.info(f"apartment name: {apartment_name}")
    # except Exception as e:
    #     print(f"Error: {e}")

    # test for get_room_id function
    # get_balance(get_new_token()[1], "文缘学生公寓")
    # print(get_balance(get_new_token()[1], "文星学生公寓"))

    # # test for get_apartment_map function
    # result = get_apartment_map()
    # for k, v in result.items():
    #     print(f"{k}: {v}")

    # test for integration
    satoken_val = get_new_token()[1]
    apt_name = get_apartment_name(satoken_val)
    print(get_balance(satoken_val, apt_name))
