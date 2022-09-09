import json


class Config:
    CONFIG_FILENAME = "config.json"

    def __init__(self, config_filename=CONFIG_FILENAME):
        self.config_filename = config_filename
        self.config_content = {}
        self.token = ''

    def load(self):
        self._load_content()
        self._pares_token()

    def _load_content(self):
        with open(self.config_filename, 'r', encoding='utf8') as f:
            self.config_content = json.load(f)

    def _pares_token(self):
        if self.config_content:
            self.token = self.config_content['token']
        else:
            self._load_content()
            self.token = self.config_content['token']


if __name__ == '__main__':
    config = Config()
    config.load()
    print(config.token)
