import re
import httpx
from config import Config
from typing import List


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

    def _fresh_login_id(self):
        res = httpx.get(self.url + '/user', headers=self.head)
        userinfo = res.json()
        self.login_id = userinfo['data']['login']

    def _get_docs(self, repo_id) -> List:
        res_docs = httpx.get(self.url + '/repos/' + str(repo_id) + '/docs', headers=self.head)
        docs = res_docs.json()
        docs_list = []
        for doc in docs['data']:
            slug = doc['slug']
            doc_json = {}
            res_content = httpx.get(self.url + '/repos/' + str(repo_id) + '/docs/' + slug, headers=self.head)
            content = res_content.json()
            doc_json['title'] = content['data']['title']
            body = content['data']['body']
            doc_json['body'] = self._parse_body(body)

            docs_list.append(doc_json)
        return docs_list

    def _parse_body(self, raw_body):
        posts_text = re.sub(r'\\n', "\n", raw_body)
        result = re.sub(r'<a name="(.*)"></a>', "", posts_text)
        return result

    def fresh_repos_and_docs(self):
        self._fresh_login_id()
        res_repos = httpx.get(self.url + '/users/' + self.login_id + '/repos', headers=self.head)
        repos = res_repos.json()
        for repo in repos['data']:
            repo_content = {
                'id': repo['id'],
                'name': repo['name'],
                'public': True if repo['public'] == 1 else False,
                'docs': self._get_docs(repo['id'])
            }
            self.repos.append(repo_content)

    def export_docs(self, output_path=OUTPUT_PATH):
        if len(self.repos) > 0:
            for repo in self.repos:
                if self.allow_private_repos or repo['public'] is True:
                    print(f"{repo['name']}")
                    for doc in repo['docs']:
                        print(f"- {doc['title']}")
                        Yuque.write_file(output_path + doc['title'] + '.md', doc['body'])


if __name__ == '__main__':
    config = Config()
    config.load()
    yuque = Yuque(config.token)
    yuque.fresh_repos_and_docs()
    yuque.export_docs()
    print(yuque.repos)
