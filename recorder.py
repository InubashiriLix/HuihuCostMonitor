import os
import datetime
import csv
from typing import Union
from pathlib import Path


def update_csv(
    fee: str,
    file_path: Union[str, Path],
    datetime: str = datetime.datetime.now().strftime("%Y-%m-%d-%H"),
) -> None:
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime, fee])  # 写入日期和费用
