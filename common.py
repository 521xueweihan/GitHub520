#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   XueWeiHan
#   E-mail  :   595666367@qq.com
#   Date    :   2025-01-16 15:27
#   Desc    :   公共函数
import os
import json
from typing import Any, Optional
from datetime import datetime, timezone, timedelta

from retry import retry

GITHUB_URLS = [
    'alive.github.com', 'api.github.com', 'api.individual.githubcopilot.com',
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
    'vscode.dev', 'education.github.com', 'private-user-images.githubusercontent.com',
    'release-assets.githubusercontent.com'
]

HOSTS_TEMPLATE = """# GitHub520 Host Start
{content}

# Update time: {update_time}
# Update url: https://raw.hellogithub.com/hosts
# Star me: https://github.com/521xueweihan/GitHub520
# GitHub520 Host End\n"""


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


def write_hosts_content(content: str, content_list: list) -> str:
    if not content:
        return ""
    update_time = datetime.now(timezone.utc).astimezone(
        timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()
    hosts_content = HOSTS_TEMPLATE.format(content=content,
                                          update_time=update_time)
    has_change = write_file(hosts_content, update_time)
    if has_change:
        write_json_file(content_list)
    return hosts_content
