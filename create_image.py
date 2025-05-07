from pathlib import Path
from typing import Union, Optional

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")  # 或 "TkAgg" 如果只是保存 PNG 不弹窗


def plot_balance(
    csv_path: Union[str, Path],
    *,
    save_to: Optional[Union[str, Path]] = None,
):
    """
    余额折线图

    Parameters
    ----------
    csv_path : str | pathlib.Path
        CSV 文件路径，格式：YYYY-MM-DD-HH,balance（缺失用 --）
    save_to : str | pathlib.Path | None, default None
        若提供则把图保存为 PNG，否则只弹窗显示

    Returns
    -------
    pandas.DataFrame
        处理后的数据表
    """
    # ---------- 读 & 清洗 ----------
    df = (
        pd.read_csv(
            csv_path,
            header=None,
            names=["timestamp", "balance"],
            na_values="--",
        )
        .dropna(subset=["balance"])  # 去掉 "--"
        .drop_duplicates(subset=["timestamp", "balance"])  # 去重
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d-%H")
    df = df.sort_values("timestamp").reset_index(drop=True)

    # ---------- 画 ----------
    # import matplotlib
    plt.figure(figsize=(8, 4))
    plt.plot(df["timestamp"], df["balance"], marker="o")
    plt.title("Dormitory Balance Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Balance (currency units)")
    plt.xticks(rotation=45)
    plt.grid(ls="--", alpha=0.3)
    plt.tight_layout()

    if save_to is not None:
        plt.savefig(save_to, dpi=150)

    return df
