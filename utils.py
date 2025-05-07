import requests
import socket


def is_online(
    probes=None,
    timeout: float = 3.0,
) -> bool:
    """
    判断是否真正连上外网（已过认证）。
    probes: [(url, expect_status, expect_keyword | None), ...]
    返回 True 表示已联网，否则 False
    """
    if probes is None:
        probes = [
            # status,    关键字 (None 表示不用检查内容)
            ("https://www.gstatic.com/generate_204", 204, None),
            ("http://connectivitycheck.gstatic.com/generate_204", 204, None),
            ("https://www.apple.com/library/test/success.html", 200, None),
            ("http://www.baidu.com", 200, "baidu.com"),
        ]

    headers = {"User-Agent": "Mozilla/5.0"}  # 少数站点拒绝空 UA

    for url, expected_status, keyword in probes:
        try:
            resp = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=False,  # 关键：禁止自动跳到登录页
            )
            if resp.status_code != expected_status:
                continue
            if keyword and keyword not in resp.text.lower():
                continue
            # 一切符合预期
            return True
        except requests.RequestException:
            # 超时、被墙、TLS 失败……直接测下一个
            pass

    return False


def file_sys_ensure(folder_path: str):
    """
    创建空文件夹，如果文件夹已存在则不创建。

    Parameters
    ----------
    folder_path : str
        要创建的文件夹路径
    """
    import os

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")
