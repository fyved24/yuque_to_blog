import shutil
import os


def overwrite_dir(source, target):
    if os.path.exists(target):
        shutil.rmtree(target)
    if os.path.exists(source):
        shutil.move(source, target)


def rmtree_ifexits(target):
    if os.path.exists(target):
        shutil.rmtree(target)
