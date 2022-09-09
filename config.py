import json


class Config:
    CONFIG_FILENAME = "config.json"

    def __init__(self, config_filename=CONFIG_FILENAME):
        self.config_filename = config_filename
        self.config_content = {}
        self.token = ''

    def __getitem__(self, key):
        if not self.config_content:
            self._load()
        return self.config_content[key]

    def _load(self):
        self._load_content()

    def _load_content(self):
        with open(self.config_filename, 'r', encoding='utf8') as f:
            self.config_content = json.load(f)


if __name__ == '__main__':
    config = Config()
    print(config['token'])
    print(config['output'])
