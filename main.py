import util
from yuque import Yuque
from config import Config

if __name__ == '__main__':
    config = Config()
    yuque = Yuque(config['token'])
    if yuque.fresh_repos_and_docs():
        if yuque.export_docs('tmp/'):
            util.overwrite_dir('tmp', config['output'])
