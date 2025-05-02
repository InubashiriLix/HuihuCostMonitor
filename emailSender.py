import smtplib
import re
import os
import logging
from email.mime.text import MIMEText
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

import datetime

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
        message = MIMEText(
            f"today's dorm rest fee: {current_cost}",  # 邮件正文内容
            "plain",  # 邮件格式
            "utf-8",  # 编码
        )

        message["From"] = SENDER_EMAIL  # 发件人
        message["To"] = self._recipient_email  # 收件人
        message["Subject"] = (
            f"【dorm cost report】: {datetime.datetime.now().strftime('%Y-%m-%d')}"  # 邮件主题
        )

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


def send_email_async(recipient_email: str, cost: str) -> bool:
    sender = VerificationEmailSender(recipient_email)
    state_code_bool = sender.send(cost)
    return state_code_bool


def send_email_in_background(recipient_email: str, cost: str):
    # 使用线程池来异步发送邮件，测试专用函数
    with ThreadPoolExecutor() as executor:
        future = executor.submit(send_email_async, recipient_email, cost)
        return future.result()


# 如果需要测试该脚本
if __name__ == "__main__":
    # 异步发送邮件
    from get_cost import get_rest_cost

    cost = get_rest_cost() or "NULL"

    send_email_in_background("enterYourEmail@163.com", str(cost))
