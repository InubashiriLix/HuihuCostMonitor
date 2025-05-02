import os
import datetime
import csv


def update_csv(
    fee: str, datetime: str = datetime.datetime.now().strftime("%Y-%m-%d-%H")
) -> None:
    file_path = os.path.join(os.path.dirname(__file__), "fee.csv")
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime, fee])  # 写入日期和费用


if __name__ == "__main__":
    update_csv("100")
