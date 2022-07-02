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
import traceback

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
    "collector.github.com",
    "pipelines.actions.githubusercontent.com",
    "media.githubusercontent.com",
    "cloud.githubusercontent.com",
    "objects.githubusercontent.com",
    "vscode.dev"]

IPADDRESS_PREFIX = ".ipaddress.com"

HOSTS_TEMPLATE = """# GitHub520 Host Start
{content}

# Update time: {update_time}
# Update url: https://raw.hellogithub.com/hosts
# Star me: https://github.com/521xueweihan/GitHub520
# GitHub520 Host End\n"""


def write_file(hosts_content: str, update_time: str):
    output_doc_file_path = os.path.join(os.path.dirname(__file__), "README.md")
    template_path = os.path.join(os.path.dirname(__file__),
                                 "README_template.md")
    write_host_file(hosts_content)
    if os.path.exists(output_doc_file_path):
        with open(output_doc_file_path, "r") as old_readme_fb:
            old_content = old_readme_fb.read()
            old_hosts = old_content.split("```bash")[1].split("```")[0].strip()
            old_hosts = old_hosts.split("# Update time:")[0].strip()
            hosts_content_hosts = hosts_content.split("# Update time:")[0].strip()
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


def write_host_file(hosts_content: str):
    output_file_path = os.path.join(os.path.dirname(__file__), 'hosts')
    with open(output_file_path, "w") as output_fb:
        output_fb.write(hosts_content)


def write_json_file(hosts_list: list):
    output_file_path = os.path.join(os.path.dirname(__file__), 'hosts.json')
    with open(output_file_path, "w") as output_fb:
        json.dump(hosts_list, output_fb)


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


@retry(tries=3)
def update_gitee_gist(session: requests.session, host_content):
    gitee_token = os.getenv("gitee_token")
    gitee_gist_id = os.getenv("gitee_gist_id")
    gist_file_name = os.getenv("gitee_gist_file_name")
    url = "https://gitee.com/api/v5/gists/{}".format(gitee_gist_id)
    headers = {
        "Content-Type": "application/json"}
    data = {
        "access_token": gitee_token,
        "files": {gist_file_name: {"content": host_content}},
        "public": "true"}
    json_data = json.dumps(data)
    try:
        response = session.patch(url, data=json_data, headers=headers,
                                 timeout=20)
        if response.status_code == 200:
            print("update gitee gist success")
        else:
            print("update gitee gist fail: {} {}".format(response.status_code,
                                                         response.content))
    except Exception as e:
        traceback.print_exc(e)
        raise Exception(e)


def main():
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
    has_change = write_file(hosts_content, update_time)
    if has_change:
        write_json_file(content_list)
    print(hosts_content)


if __name__ == '__main__':
    main()
