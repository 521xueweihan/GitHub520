#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2020-05-19 15:27
#   Desc    :   获取最新的 GitHub 相关域名对应 IP
import os
import re
import json
import argparse
from typing import Any, Optional

from datetime import datetime, timezone, timedelta

from pythonping import ping
from requests_html import HTMLSession
from retry import retry

GITHUB_URLS = [
    'alive.github.com', 'api.github.com', 'assets-cdn.github.com',
    'avatars.githubusercontent.com', 'avatars0.githubusercontent.com',
    'avatars1.githubusercontent.com', 'avatars2.githubusercontent.com',
    'avatars3.githubusercontent.com', 'avatars4.githubusercontent.com',
    'avatars5.githubusercontent.com', 'camo.githubusercontent.com',
    'central.github.com', 'cloud.githubusercontent.com', 'codeload.github.com',
    'collector.github.com', 'desktop.githubusercontent.com',
    'favicons.githubusercontent.com', 'gist.github.com',
    'github-cloud.s3.amazonaws.com', 'github-com.s3.amazonaws.com',
    'github-production-release-asset-2e65be.s3.amazonaws.com',
    'github-production-repository-file-5c1aeb.s3.amazonaws.com',
    'github-production-user-asset-6210df.s3.amazonaws.com', 'github.blog',
    'github.com', 'github.community', 'github.githubassets.com',
    'github.global.ssl.fastly.net', 'github.io', 'github.map.fastly.net',
    'githubstatus.com', 'live.github.com', 'media.githubusercontent.com',
    'objects.githubusercontent.com', 'pipelines.actions.githubusercontent.com',
    'raw.githubusercontent.com', 'user-images.githubusercontent.com',
    'vscode.dev', 'education.github.com', 'private-user-images.githubusercontent.com'
]

HOSTS_TEMPLATE = """# GitHub520 Host Start
{content}

# Update time: {update_time}
# Update url: https://raw.hellogithub.com/hosts
# Star me: https://github.com/521xueweihan/GitHub520
# GitHub520 Host End\n"""


def write_file(hosts_content: str, update_time: str) -> bool:
    output_doc_file_path = os.path.join(os.path.dirname(__file__), "README.md")
    template_path = os.path.join(os.path.dirname(__file__),
                                 "README_template.md")
    write_host_file(hosts_content)
    if os.path.exists(output_doc_file_path):
        with open(output_doc_file_path, "r") as old_readme_fb:
            old_content = old_readme_fb.read()
            if old_content:
                old_hosts = old_content.split("```bash")[1].split("```")[0].strip()
                old_hosts = old_hosts.split("# Update time:")[0].strip()
                hosts_content_hosts = hosts_content.split("# Update time:")[
                    0].strip()
                if old_hosts == hosts_content_hosts:
                    print("host not change")
                    return False

    with open(template_path, "r") as temp_fb:
        template_str = temp_fb.read()
        hosts_content = template_str.format(hosts_str=hosts_content,
                                            update_time=update_time)
        with open(output_doc_file_path, "w") as output_fb:
            output_fb.write(hosts_content)
    return True


def write_host_file(hosts_content: str) -> None:
    output_file_path = os.path.join(os.path.dirname(__file__), 'hosts')
    with open(output_file_path, "w") as output_fb:
        output_fb.write(hosts_content)


def write_json_file(hosts_list: list) -> None:
    output_file_path = os.path.join(os.path.dirname(__file__), 'hosts.json')
    with open(output_file_path, "w") as output_fb:
        json.dump(hosts_list, output_fb)


def get_best_ip(ip_list: list) -> str:
    ping_timeout = 2
    best_ip = ''
    min_ms = ping_timeout * 500
    ip_set = set(ip_list)
    for ip in ip_set:
        ping_result = ping(ip, timeout=ping_timeout)
        print(ping_result.rtt_avg_ms)
        if ping_result.rtt_avg_ms == ping_timeout * 500:
            # 超时认为 IP 失效
            continue
        else:
            if ping_result.rtt_avg_ms < min_ms:
                min_ms = ping_result.rtt_avg_ms
                best_ip = ip
    return best_ip


@retry(tries=3)
def get_json(session: Any) -> Optional[list]:
    url = 'https://raw.hellogithub.com/hosts.json'
    try:
        rs = session.get(url)
        data = json.loads(rs.text)
        return data
    except Exception as ex:
        print(f"get: {url}, error: {ex}")
        raise Exception


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
            raise Exception(f"url: {github_url}, ipaddress empty")
    except Exception as ex:
        print(f"get: {url}, error: {ex}")
        raise Exception


def main(verbose=False, model='server') -> None:
    if verbose:
        print('Start script.')
    session = HTMLSession()
    content = ""
    if model == 'server':
        content_list = []
        for index, github_url in enumerate(GITHUB_URLS):
            try:
                ip = get_ip(session, github_url)

                content += ip.ljust(30) + github_url + "\n"
                content_list.append((ip, github_url,))
            except Exception:
                continue
            if verbose:
                print(f'process url: {index + 1}/{len(GITHUB_URLS)}')
    else:
        content_list = get_json(session)
        for item in content_list:
            content += item[0].ljust(30) + item[1] + "\n"

    if not content:
        return
    update_time = datetime.utcnow().astimezone(
        timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    hosts_content = HOSTS_TEMPLATE.format(content=content,
                                          update_time=update_time)
    has_change = write_file(hosts_content, update_time)
    if has_change:
        write_json_file(content_list)
    if verbose:
        print(hosts_content)
        print('End script.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run fetch ips script")
    # 2. 定义参数
    parser.add_argument('model', metavar='model', type=str, nargs='?')
    # 3. 解析命令行
    args = parser.parse_args()
    main(True, args.model)
