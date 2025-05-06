from json import encoder
import re
import os

import pathlib
from pathlib import Path

import smtplib
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

import datetime

import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(funcName)s]- %(message)s",
)

# 加载环境变量
load_dotenv()

# 从环境变量中读取配置
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


class VerificationEmailSender:
    _smtp_server = "smtp.163.com"
    _smtp_port = 25

    def __init__(self, recipient_email: str):
        if not self._validate_email(recipient_email):
            raise ValueError("Invalid email address format")
        self._recipient_email = recipient_email

    @staticmethod
    def _validate_email(email: str) -> bool:
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(email_regex, email) is not None

    def send(self, current_cost: str) -> bool:
        if SENDER_EMAIL is None:
            raise EnvironmentError("email parse failed")

        if SENDER_PASSWORD is None:
            raise EnvironmentError("email password parse failed")

        # 设置邮件内容
        message = MIMEMultipart()

        message["From"] = SENDER_EMAIL  # 发件人
        message["To"] = self._recipient_email  # 收件人
        message["Subject"] = (
            f"【Dorm Balance】: {datetime.datetime.now().strftime('%Y-%m-%d')}"  # 邮件主题
        )

        # ATTACH FILES
        csv_path = "data/fee.csv"
        csv_image_path = "data/fee.png"

        mine_type, _ = mime_type, _ = mimetypes.guess_type(csv_path)
        mine_type, sub_type = (mine_type or "application/octet-stream").split("/")

        if os.path.exists(csv_image_path):
            # send the png plot
            with open(csv_image_path, "rb") as f:
                part = MIMEBase(mine_type, sub_type)
                part.set_payload(f.read())
                encoders.encode_base64(part)

            file_name = os.path.basename(csv_image_path)
            part.add_header(
                "Content-Disposition", f'attachment; filename="{file_name}"'
            )
            message.attach(part)
            image_exist_flag = True
            logging.info("csv PIC exists and attached")
        else:
            logging.error("csv pic NOT EXISTS")
            image_exist_flag = False

        if os.path.exists(csv_path):
            # send the raw csv
            with open(csv_path, "rb") as f:
                part = MIMEBase(mine_type, sub_type)
                part.set_payload(f.read())
                encoders.encode_base64(part)

            file_name = os.path.basename(csv_path)
            part.add_header(
                "Content-Disposition", f'attachment; filename="{file_name}"'
            )
            message.attach(part)
            csv_exist_flag = True
            logging.info("the scv exists and attached")
        else:
            csv_exist_flag = False
            logging.error("the scv NOT exists")

        # THE TEXT CONTENT
        _content = f"Today's Balance: {current_cost}\n"

        _content = (
            _content + "csv file not exists (error)\n"
            if not csv_exist_flag
            else _content
        )

        _content = (
            _content + "csv png file not exists (error)\n"
            if not image_exist_flag
            else _content
        )
        body = MIMEText(_content, "plain", "utf-8")
        message.attach(body)

        # SEND EMAIL
        try:
            # 使用 SMTP 而非 SMTP_SSL 来发送邮件
            with smtplib.SMTP(self._smtp_server, self._smtp_port) as smtp_connection:
                smtp_connection.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp_connection.sendmail(
                    SENDER_EMAIL, [self._recipient_email], message.as_string()
                )

            print("邮件发送成功！")
            return True

        except smtplib.SMTPException as e:
            logging.error("邮件发送失败：%s", e)
            print("邮件发送失败：", e)
            return False
        finally:
            return False


def send_email_async(recipient_email: str, cost: str) -> bool:
    sender = VerificationEmailSender(recipient_email)
    state_code_bool = sender.send(cost)
    return state_code_bool


def send_email_in_background(recipient_email: str, cost: str):
    with ThreadPoolExecutor() as executor:
        future = executor.submit(send_email_async, recipient_email, cost)
        return future.result()


# 如果需要测试该脚本
if __name__ == "__main__":
    # 异步发送邮件
    from get_info_refacted import _get_cost_

    cost = _get_cost_() or "NULL"

    send_email_in_background("13329001003@163.com", str(cost))
