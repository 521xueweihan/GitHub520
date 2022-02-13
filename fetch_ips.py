#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2020-05-19 15:27
#   Desc    :   获取最新的 GitHub 相关域名对应 IP
import os
import re
import json

from datetime import datetime, timezone, timedelta
from collections import Counter

import requests
from retry import retry

RAW_URL = [
    "alive.github.com",
    "live.github.com",
    "github.githubassets.com",
    "central.github.com",
    "desktop.githubusercontent.com",
    "assets-cdn.github.com",
    "camo.githubusercontent.com",
    "github.map.fastly.net",
    "github.global.ssl.fastly.net",
    "gist.github.com",
    "github.io",
    "github.com",
    "github.blog",
    "api.github.com",
    "raw.githubusercontent.com",
    "user-images.githubusercontent.com",
    "favicons.githubusercontent.com",
    "avatars5.githubusercontent.com",
    "avatars4.githubusercontent.com",
    "avatars3.githubusercontent.com",
    "avatars2.githubusercontent.com",
    "avatars1.githubusercontent.com",
    "avatars0.githubusercontent.com",
    "avatars.githubusercontent.com",
    "codeload.github.com",
    "github-cloud.s3.amazonaws.com",
    "github-com.s3.amazonaws.com",
    "github-production-release-asset-2e65be.s3.amazonaws.com",
    "github-production-user-asset-6210df.s3.amazonaws.com",
    "github-production-repository-file-5c1aeb.s3.amazonaws.com",
    "githubstatus.com",
    "github.community",
    "github.dev",
    "media.githubusercontent.com",
    "cloud.githubusercontent.com",
    "objects.githubusercontent.com"]

IPADDRESS_PREFIX = ".ipaddress.com"
HOSTFILE_PATH = "/etc/hosts"

HOSTS_TEMPLATE = """# Github Hosts Start
{content}

# Update time: {update_time}
# Github Hosts End\n"""


def write_file(hosts_content: str):
    mark_start = "# Github Hosts Start"
    mark_end = "# Github Hosts End"
    start = 0
    end = 0
    final_content = ""
    with open(HOSTFILE_PATH, 'r') as hosts_file:
        lines = hosts_file.readlines()
        count = 0
        for l in lines:
            if l.find(mark_start) != -1:
                start = count
            if l.find(mark_end) != -1:
                end = count
                break
            count = count + 1
        del lines[start:end + 1]
        final_content = ' '.join(map(str, lines))
    print(final_content)
    final_content = final_content + hosts_content
    print(final_content)
    with open(HOSTFILE_PATH, 'w') as hosts_file:
        hosts_file.write(final_content)


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
    if os.geteuid() != 0:
        print("need root.")
        return
    session = requests.session()
    content = ""
    content_list = []
    for raw_url in RAW_URL:
        try:
            host_name, ip = get_ip(session, raw_url)
            content += ip.ljust(30) + host_name + "\n"
            content_list.append((ip, host_name,))
        except Exception:
            continue

    if not content:
        return
    update_time = datetime.utcnow().astimezone(
        timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    hosts_content = HOSTS_TEMPLATE.format(content=content, update_time=update_time)
    write_file(hosts_content)


if __name__ == '__main__':
    main()
