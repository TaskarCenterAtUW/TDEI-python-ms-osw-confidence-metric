import os
import shutil


def clean_up(path):
    if os.path.isfile(path):
        print(f' Removing File: {path}')
        os.remove(path)
    else:
        folder = os.path.join(path)
        print(f' Removing Folder: {path}')
        shutil.rmtree(folder, ignore_errors=False)
