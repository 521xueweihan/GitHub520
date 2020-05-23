#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2020-05-19 15:27
#   Desc    :   获取最新的 GitHub 相关域名对应 IP
import os
import re
from datetime import datetime, timezone, timedelta
from collections import Counter

from retry import retry

import requests

RAW_URL = [
    "github.githubassets.com",
    "camo.githubusercontent.com",
    "github.map.fastly.net",
    "github.global.ssl.fastly.net",
    "github.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "avatars5.githubusercontent.com",
    "avatars4.githubusercontent.com",
    "avatars3.githubusercontent.com",
    "avatars2.githubusercontent.com",
    "avatars1.githubusercontent.com",
    "avatars0.githubusercontent.com"]
IPADDRESS_PREFIX = ".ipaddress.com"


def write_file(hosts_content: str):
    update_time = datetime.utcnow().astimezone(
        timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    output_file_path = os.path.join(os.path.dirname(__file__), "README.md")
    template_path = os.path.join(os.path.dirname(__file__),
                                 "README_template.md")
    with open(output_file_path, "r") as old_readme_fb:
        old_content = old_readme_fb.read()
        old_hosts = old_content.split("```bash")[1].split("```")[0].strip()
    if old_hosts == hosts_content:
        print("host not change")
        return

    with open(template_path, "r") as temp_fb:
        template_str = temp_fb.read()
        hosts_content = template_str.format(hosts_str=hosts_content,
                                            update_time=update_time)
        with open(output_file_path, "w") as output_fb:
            output_fb.write(hosts_content)


def make_ipaddress_url(raw_url: str):
    """
    生成 ipaddress 对应的 url
    :param raw_url: 原始 url
    :return: ipaddress 的 url
    """
    dot_count = raw_url.count(".")
    if dot_count > 1:
        raw_url_list = raw_url.split(".")
        tmp_url = raw_url_list[-2] + "." + raw_url_list[-1]
        ipaddress_url = "https://" + tmp_url + IPADDRESS_PREFIX + "/" + raw_url
    else:
        ipaddress_url = "https://" + raw_url + IPADDRESS_PREFIX
    return ipaddress_url


@retry(tries=3)
def get_ip(session: requests.session, raw_url: str):
    url = make_ipaddress_url(raw_url)
    try:
        rs = session.get(url, timeout=5)
        pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        ip_list = re.findall(pattern, rs.text)
        ip_counter_obj = Counter(ip_list).most_common(1)
        if ip_counter_obj:
            return raw_url, ip_counter_obj[0][0]
        raise Exception("ip address empty")
    except Exception as ex:
        print("get: {}, error: {}".format(url, ex))
        raise Exception


def main():
    hosts_template = """# GitHub520 Host Start\n{content}# GitHub520 Host End"""
    session = requests.session()
    content = ""
    for raw_url in RAW_URL:
        try:
            host_name, ip = get_ip(session, raw_url)
            content += ip.ljust(50) + host_name + "\n"
        except Exception:
            continue

    if content:
        hosts_content = hosts_template.format(content=content)
        print(hosts_content)
        write_file(hosts_content)


if __name__ == '__main__':
    main()
