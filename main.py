import socket
import time
import dotenv
import os
from datetime import datetime, timedelta
import threading


from get_cost import get_rest_cost
from recorder import update_csv
from emailSender import send_email_async


use_email: bool = True if os.getenv("USE_EMAIL") == "TRUE" else False
update_interval: float = float(os.getenv("UPDATE_INTERVAL", 4))  # 默认 4 小时
desc_email = os.getenv("DESC_EMAIL")
send_desc_hour: int = int(os.getenv("SENDING_HOUR", 8)) % 24
send_desc_min: int = int(os.getenv("SENDING_MIN", 0)) % 60

fee = None


def is_online(host="8.8.8.8", port=53, timeout=3) -> bool:
    """
    尝试和指定 host:port 建 TCP 连接（默认 Google DNS）。
    超时或异常即认为网络不通。
    """
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except OSError:
        return False


def send_email_task():
    global desc_email, fee
    print(f"[{datetime.now()}] send_email_task run")
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

    print(
        f"[{datetime.now()}] 下一次 send_email_task 安排在 {target} (in {int(delay)}s)"
    )


if __name__ == "__main__":
    if use_email:
        schedule_next()
    while True:
        try:
            if not is_online():
                time.sleep(10)
                continue
            else:
                print("Network is online.")
            fee = get_rest_cost()
            if fee is None:
                print("get fee failed")
                time.sleep(10)
                continue
            else:
                print(f"update fee: {fee}")
                update_csv(str(fee))
                fee = None
                time.sleep(int(60 * 60 * update_interval))  # 4 hour update
        except KeyboardInterrupt:
            print("\ninterrupted，exiting")
            exit(0)
