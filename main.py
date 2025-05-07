import socket
import time
import dotenv
import os
from datetime import datetime, timedelta
import threading


from get_info_refacted import get_balance, get_new_token, get_apartment_name, logging
from create_image import plot_balance
from recorder import update_csv
from emailSender import send_email_async
from utils import is_online, file_sys_ensure, get_base_dir
from auto_net_connector import NetAuth

use_email: bool = True if os.getenv("USE_EMAIL") == "TRUE" else False
update_interval: float = float(os.getenv("UPDATE_INTERVAL", 4))  # 默认 4 小时
desc_email = os.getenv("DESC_EMAIL")
send_desc_hour: int = int(os.getenv("SENDING_HOUR", 8)) % 24
send_desc_min: int = int(os.getenv("SENDING_MIN", 0)) % 60

use_auto_connector: bool = True if os.getenv("USE_AUTO_NET_LOGIN") == "TRUE" else False

fee = None

BASE_DIR = get_base_dir()


def send_email_task():
    global desc_email, fee
    logging.info(f"[{datetime.now()}] send_email_task run")
    if desc_email is None:
        raise EnvironmentError("email parse failed")
    send_email_async(str(desc_email), str(fee))
    schedule_next()


def schedule_next(hour: int = send_desc_hour, minute: int = send_desc_min):
    """
    按每天指定的 hour:minute 调度 send_email_task。
    """
    now = datetime.now()
    target = now.replace(hour=hour % 24, minute=minute % 60, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    delay = (target - now).total_seconds()

    t = threading.Timer(delay, send_email_task)
    t.daemon = True  # ← 关键：把定时器线程设为 daemon
    t.start()

    logging.info(
        f"[{datetime.now()}] 下一次 send_email_task 安排在 {target} (in {int(delay)}s)"
    )


if __name__ == "__main__":
    file_sys_ensure("data")

    if use_auto_connector:
        logging.info("you have set the auto net connect, thread start now")
        auto_net_connector = NetAuth()
        execute_auto_net_connect_thread = threading.Thread(
            target=auto_net_connector.execute, daemon=True
        )
        execute_auto_net_connect_thread.start()

    if use_email:  # if you set
        logging.info("you have set the sending email on, starting thread")
        schedule_next()

    while True:
        try:
            if not is_online():
                time.sleep(10)
                continue
            else:
                logging.info("Network is online.")

            try:
                satoken = get_new_token()[1]
            except Exception as e:
                continue

            apartment_name = get_apartment_name(satoken)
            fee = get_balance(satoken, apartment_name)

            if fee is None:
                logging.error("get fee failed")
                time.sleep(10)
                continue
            else:
                logging.info(f"update fee: {fee}")
                update_csv(str(fee), BASE_DIR / "data/fee.csv")
                plot_balance(
                    (BASE_DIR / "data/fee.csv"), save_to=(BASE_DIR / "data/fee.png")
                )
                fee = None
                time.sleep(int(60 * 60 * update_interval))  # 4 hour update
        except KeyboardInterrupt:
            logging.error("\ninterrupted，exiting")
            exit(0)
        except EnvironmentError as e:
            logging.error(e)
            logging.error("environment variable parse failed or file not found")
            exit(1)
        except Exception:
            time.sleep(20)
