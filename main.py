from yuque import Yuque
from config import Config

if __name__ == '__main__':
    config = Config()
    config.load()
    yuque = Yuque(config.token)
    yuque.fresh_repos_and_docs()
    yuque.export_docs()
