#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2020-05-19 15:27
#   Desc    :   获取最新的 GitHub 相关域名对应 IP
import re
from typing import Any, Optional
from datetime import datetime

from pythonping import ping
from requests_html import HTMLSession
from retry import retry

from common import GITHUB_URLS, write_hosts_content


def get_best_ip(ip_list: list) -> str:
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
def get_ip(session: Any, github_url: str) -> Optional[str]:
    url = f'https://sites.ipaddress.com/{github_url}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1'
                      '06.0.0.0 Safari/537.36'}
    try:
        rs = session.get(url, headers=headers, timeout=5)
        pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        ip_list = re.findall(pattern, rs.html.text)
        best_ip = get_best_ip(ip_list)
        if best_ip:
            return best_ip
        else:
            raise Exception("url: {github_url}, ipaddress empty")
    except Exception as ex:
        print("get: {url}, error: {ex}")
        raise Exception


def main() -> None:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{current_time} - Start script.')
    session = HTMLSession()
    content = ""
    content_list = []
    for index, github_url in enumerate(GITHUB_URLS):
        try:
            ip = get_ip(session, github_url)

            content += ip.ljust(30) + github_url + "\n"
            content_list.append((ip, github_url,))
        except Exception:
            continue
        print(f'Process url: {index + 1}/{len(GITHUB_URLS)}, {github_url}')

    write_hosts_content(content, content_list)
    # print(hosts_content)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{current_time} - End script.')


if __name__ == '__main__':
    main()
