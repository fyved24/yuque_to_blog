import datetime
import os
import re
import httpx

import util
from config import Config
from typing import List
from log import logger_config
import shutil


class Yuque:
    URL = 'https://www.yuque.com/api/v2'
    OUTPUT_PATH = 'docs/'

    def __init__(self, token, allow_private_repos=False, url=URL, output_path=OUTPUT_PATH):
        self.url = url
        self.head = Yuque._build_head(token)
        self.output_path = output_path
        self.login_id = ''
        self.allow_private_repos = allow_private_repos
        self.repos = []
        self.log = logger_config('logs.txt', Yuque.__name__)

    @staticmethod
    def _build_head(token):
        head = {
            'User-Agent': "Edg/105.0.1343.27",
            'X-Auth-Token': token
        }
        return head

    @staticmethod
    def write_file(path, content):
        with open(path, 'w') as f:
            f.writelines(content)

    @staticmethod
    def _build_meta_info(repo_name, doc):
        meta_info = f"""---
title: {doc['title']}
date: {datetime.datetime.strptime(doc['created_at'], '%Y-%m-%dT%H:%M:%S.000Z').strftime('%Y-%m-%d %H:%M:%S')}
categories: 
  - {repo_name}
tags:
  - {repo_name}
---

"""
        return meta_info

    @staticmethod
    def _parse_body(raw_body):
        posts_text = re.sub(r'\\n', "\n", raw_body)
        result = re.sub(r'<a name="(.*)"></a>', "", posts_text)
        return result

    @staticmethod
    def _build_doc(repo_name, doc):
        meta_info = Yuque._build_meta_info(repo_name, doc)
        body = meta_info + Yuque._parse_body(doc['body'])
        return body

    def _fresh_login_id(self):
        res = httpx.get(self.url + '/user', headers=self.head)
        userinfo = res.json()
        self.login_id = userinfo['data']['login']

    def _get_docs(self, repo) -> List:
        res_docs = httpx.get(self.url + '/repos/' + str(repo['id']) + '/docs', headers=self.head)
        docs = res_docs.json()
        docs_list = []
        for doc in docs['data']:
            slug = doc['slug']
            doc_json = {}
            res_content = httpx.get(self.url + '/repos/' + str(repo['id']) + '/docs/' + slug, headers=self.head)
            content = res_content.json()
            doc_data = content['data']
            doc_json['title'] = doc_data['title']
            doc_json['body'] = self._build_doc(repo['name'], doc_data)
            docs_list.append(doc_json)
        return docs_list

    def fresh_repos_and_docs(self):
        try:
            self._fresh_login_id()
            res_repos = httpx.get(self.url + '/users/' + self.login_id + '/repos', headers=self.head)
        except httpx.HTTPError as e:
            self.log.error(f'语雀api请求错误{e}')
            return False
        repos = res_repos.json()
        for repo in repos['data']:
            repo_content = {
                'id': repo['id'],
                'name': repo['name'],
                'public': True if repo['public'] == 1 else False,
                'docs': self._get_docs(repo)
            }
            self.repos.append(repo_content)
        return True

    def export_docs(self, output_path=OUTPUT_PATH):
        if len(self.repos) > 0:
            try:
                util.rmtree_ifexits(output_path)
                os.mkdir(output_path)
                for repo in self.repos:
                    if self.allow_private_repos or repo['public'] is True:
                        self.log.info(f"获取到知识库: {repo['name']}")
                        for doc in repo['docs']:
                            self.log.info(f"- {doc['title']}")
                            Yuque.write_file(output_path + doc['title'] + '.md', doc['body'])
            except IOError as e:
                self.log.error(f'写入文件文件错误{e}')
                return False
        return True


if __name__ == '__main__':
    config = Config()
    yuque = Yuque(config['token'])
    # print(yuque._build_meta_info("测试后", "测试"))
    yuque.fresh_repos_and_docs()
    print(yuque.repos)
