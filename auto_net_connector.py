import requests
import time

import dotenv
from dotenv import load_dotenv
import os
import logging

from utils import is_online

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(funcName)s] - %(message)s",
)

load_dotenv()


class NetAuth:
    USE_AUTO_NET_LOGIN = os.getenv("USE_AUTO_NET_LOGIN")

    if USE_AUTO_NET_LOGIN == "TRUE":
        USE_AUTO_NET_LOGIN = True
    else:
        USE_AUTO_NET_LOGIN = False

    if USE_AUTO_NET_LOGIN:
        USERNAME = os.getenv("USERNAME")
        PASSWORD = os.getenv("PASSWORD")
        TELE_COMP_SHORT = os.getenv("TELE_COMP_SHORT")
        USE_LOW_COST_STRATEGY = os.getenv("USE_LOW_COST_STRATEGY")

        # check wheter use low cost stra
        if USE_LOW_COST_STRATEGY == "TRUE":
            USE_LOW_COST_STRATEGY = True
        else:
            USE_LOW_COST_STRATEGY = False

        # validate the check interval, default time 15
        try:
            CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 15))
        except TypeError:
            raise EnvironmentError(
                "CHECK_INTERVAL Must be an Integer greater than 5, CHECK YOUR .env file"
            )
        assert CHECK_INTERVAL > 5, (
            "CHECK_INTERVAL Must be an Integer greater than 5, CHECK YOUR .env file"
        )

        # validate the username, pswd, and telcom name
        if (USERNAME is None) or (PASSWORD is None) or (TELE_COMP_SHORT is None):
            logging.error(
                "username or password or tele_comp_short parse failed,"
                "please chcck your .env file"
            )
            raise EnvironmentError(
                "username or password or tele_comp_short parse failed"
            )

        _avaliable_list = ["cmcc", "telecom", "unicom"]
        if TELE_COMP_SHORT not in _avaliable_list:
            raise EnvironmentError(
                f"the TELE_COMP_SHORT must be one of the following company: {', '.join(_avaliable_list)}"
            )

    def __init__(self):
        if self.USE_AUTO_NET_LOGIN:
            self.account = {"username": self.USERNAME, "password": self.PASSWORD}

        self.url = "http://10.10.16.12/api/portal/v1/login"

        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es;q=0.5",
            "Connection": "keep-alive",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "10.10.16.12",
            "Origin": "http://10.10.16.12",
            "Referer": "http://10.10.16.12/portal/mobile.html?v=202208181518",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Mobile Safari/537.36 Edg/135.0.0.0",
            "X-Requested-With": "XMLHttpRequest",
        }

        self.payload = {
            "domain": self.TELE_COMP_SHORT,
            "username": self.account["username"],
            "password": self.account["password"],
        }

    def execute(self):
        """
        this function is use to run the autologin
        I prefer to use another thread to run this function
        """
        if self.USE_AUTO_NET_LOGIN:
            while True:
                if is_online():
                    # if the network is normal then delay a specified interval
                    logging.info("Auth: online")
                    time.sleep(self.CHECK_INTERVAL)
                else:
                    logging.info("Auth: off line detected")
                    if self._net_auth():
                        if self.USE_LOW_COST_STRATEGY:  # if use this strategy
                            logging.info(
                                "Auth: use low-cost strategy: delaying for 5 hours"
                            )
                            time.sleep(
                                60 * 60 * 5
                            )  # delay for 5 hours (save resources)
                        else:
                            logging.info("Auth: retry immediately")
                            continue
        else:
            logging.info(
                "Auth: Auto net login is enabled, if you want to enable it, set the USE_AUTO_NET_LOGIN=TRUE in the .env file"
            )
            logging.info("now attempts to cancel the thread")
            try:
                import threading

                current_thread = threading.current_thread()
                if current_thread.is_alive():
                    logging.info("Stopping the current thread")
                    raise SystemExit("Thread cancelled")
            except SystemExit as e:
                logging.error(f"Auth: Thread cancelled with message: {e}")
            except Exception as e:
                logging.error(f"Auth: Failed to canncel the thread: {e}")

    def _net_auth(self) -> bool:
        """
        Attempts to authenticate to the network by sending a POST request to the specified URL.
        Returns:
            bool: True if authentication is successful (HTTP 200 response), False otherwise.
        Exceptions:
            - Handles `requests.exceptions.RequestException` to log network-related errors.
            - Handles generic exceptions to log unexpected errors.
        Logging:
            - Logs success message if authentication is successful.
            - Logs error messages for authentication failure or exceptions.
        """

        try:
            response = requests.post(
                self.url, headers=self.headers, json=self.payload, timeout=10
            )
            if response.status_code == 200:
                logging.info("Auth: Net auth success")
                return True
            else:
                logging.error("Auth: Authentication failed")
                logging.error(f"report: {response.text}")
                return False
        except requests.exceptions.RequestException as req_e:
            logging.error("Auth: request failed, you may not in the 慧湖通校园网")
            logging.error(f"request error: {req_e}")
            return False
        except Exception as e:
            logging.error("Auth: unknown error")
            logging.error(f"request error: {e}")
            return False


if __name__ == "__main__":
    NetAuth()._net_auth()
