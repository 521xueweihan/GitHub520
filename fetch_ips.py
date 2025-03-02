#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2020-05-19 15:27
#   Desc    :   获取最新的 GitHub 相关域名对应 IP
import re
from typing import Any, List, Optional
from datetime import datetime
import sys
import asyncio
import aiodns

from pythonping import ping
from requests_html import HTMLSession
from retry import retry

from common import GITHUB_URLS, write_hosts_content


def select_ip_from_list(ip_list: list) -> str:
    ping_timeout = 1
    best_ip = ''
    min_ms = ping_timeout * 1000
    ip_set = set(ip_list)
    for ip in ip_set:
        ping_result = ping(ip, timeout=ping_timeout)
        print(f'ping {ip} {ping_result.rtt_avg_ms} ms')
        if ping_result.rtt_avg_ms == ping_timeout * 1000:
            # 超时认为 IP 失效
            continue
        else:
            if ping_result.rtt_avg_ms < min_ms:
                min_ms = ping_result.rtt_avg_ms
                best_ip = ip
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
        print("get: {url}, error: {ex}")
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
        print(f"DNS 查询失败: {e}")
        return []


async def get_ip(session: Any, github_url: str) -> Optional[str]:
    ip_list_web = []
    try:
        ip_list_web = get_ip_list_from_ipaddress_com(session, github_url)
    except Exception as ex:
        raise Exception("url: {github_url}, ipaddress empty")
    ip_list_dns = []
    try:
        ip_list_dns = await get_ip_list_from_dns(github_url, dns_server_list=DNS_SERVER_LIST)
    except Exception as ex:
        pass
    ip_list = list(set(ip_list_web + ip_list_dns))
    if len(ip_list) == 0:
        return None
    best_ip = select_ip_from_list(ip_list)
    return best_ip


async def main() -> None:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{current_time} - Start script.')
    session = HTMLSession()
    content = ""
    content_list = []
    for index, github_url in enumerate(GITHUB_URLS):
        try:
            ip = await get_ip(session, github_url)
            if ip is None:
                print(f"{github_url}: IP Not Found")
                continue
            content += ip.ljust(30) + github_url + "\n"
            content_list.append((ip, github_url,))
        except Exception:
            continue
        print(f'Process url: {index + 1}/{len(GITHUB_URLS)}, {github_url}')

    write_hosts_content(content, content_list)
    # print(hosts_content)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{current_time} - End script.')


if __name__ == "__main__":
    if sys.platform == "win32":
        # Windows 事件循环策略配置
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())