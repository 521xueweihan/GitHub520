#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2020-05-19 15:27
#   Desc    :   获取最新的 GitHub 相关域名对应 IP
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
import sys
import asyncio
import aiodns

from pythonping import ping
from requests_html import HTMLSession
from retry import retry

from common import GITHUB_URLS, write_hosts_content


PING_TIMEOUT_SEC: int = 1
DISCARD_LIST: List[str] = ["1.0.1.1", "1.2.1.1", "127.0.0.1"]


PING_LIST: Dict[str, int] = dict()


def ping_cached(ip: str) -> int:
    global PING_LIST
    if ip in PING_LIST:
        return PING_LIST[ip]
    ping_times = [ping(ip, timeout=PING_TIMEOUT_SEC).rtt_avg_ms for _ in range(3)]
    ping_times.sort()
    print(f'Ping {ip}: {ping_times} ms')
    PING_LIST[ip] = ping_times[1] # 取中位数
    return PING_LIST[ip]


def select_ip_from_list(ip_list: List[str]) -> Optional[str]:
    if len(ip_list) == 0:
        return None
    ping_results = [(ip, ping_cached(ip)) for ip in ip_list]
    ping_results.sort(key=lambda x: x[1])
    best_ip = ping_results[0][0]
    print(f"{ping_results}, selected {best_ip}")
    return best_ip


@retry(tries=3)
def get_ip_list_from_ipaddress_com(session: Any, github_url: str) -> Optional[List[str]]:
    url = f'https://sites.ipaddress.com/{github_url}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1'
                      '06.0.0.0 Safari/537.36'}
    try:
        rs = session.get(url, headers=headers, timeout=5)
        pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        ip_list = re.findall(pattern, rs.html.text)
        return ip_list
    except Exception as ex:
        print(f"get: {url}, error: {ex}")
        raise Exception


DNS_SERVER_LIST = [
    "1.1.1.1",  # Cloudflare
    "8.8.8.8",  # Google
    "101.101.101.101",  # Quad101
    "101.102.103.104",  # Quad101
]


def windows_compatibility_check():
    if sys.platform == "win32":
        # 检查 pycares 是否正常加载
        try:
            import pycares
        except ImportError:
            raise RuntimeError("请先执行 'pip install pycares'")


async def get_ip_list_from_dns(
    domain,
    record_type="A",
    dns_server_list=["1.2.4.8", "114.114.114.114"],
):
    # Windows 兼容性检查
    windows_compatibility_check()

    # 配置 DNS 服务器
    resolver = aiodns.DNSResolver()
    resolver.nameservers = dns_server_list

    try:
        # 执行异步查询
        result = await resolver.query(domain, record_type)
        return [answer.host for answer in result]
    except aiodns.error.DNSError as e:
        print(f"{domain}: DNS 查询失败: {e}")
        return []


async def get_ip(session: Any, github_url: str) -> Optional[str]:
    ip_list_web = []
    try:
        ip_list_web = get_ip_list_from_ipaddress_com(session, github_url)
    except Exception as ex:
        pass
    ip_list_dns = []
    try:
        ip_list_dns = await get_ip_list_from_dns(github_url, dns_server_list=DNS_SERVER_LIST)
    except Exception as ex:
        pass
    ip_list_set = set(ip_list_web + ip_list_dns)
    for discard_ip in DISCARD_LIST:
        ip_list_set.discard(discard_ip)
    ip_list = list(ip_list_set)
    ip_list.sort()
    if len(ip_list) == 0:
        return None
    print(f"{github_url}: {ip_list}")
    best_ip = select_ip_from_list(ip_list)
    return best_ip


async def main() -> None:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{current_time} - Start script.')
    session = HTMLSession()
    content = ""
    content_list = []
    for index, github_url in enumerate(GITHUB_URLS):
        print(f'Start Processing url: {index + 1}/{len(GITHUB_URLS)}, {github_url}')
        try:
            ip = await get_ip(session, github_url)
            if ip is None:
                print(f"{github_url}: IP Not Found")
                ip = "# IP Address Not Found"
            content += ip.ljust(30) + github_url
            global PING_LIST
            if PING_LIST.get(ip) is not None and PING_LIST.get(ip) == PING_TIMEOUT_SEC * 1000:
                content += "  # Timeout"
            content += "\n"
            content_list.append((ip, github_url,))
        except Exception:
            continue

    write_hosts_content(content, content_list)
    # print(hosts_content)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{current_time} - End script.')


if __name__ == "__main__":
    if sys.platform == "win32":
        # Windows 事件循环策略配置
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())