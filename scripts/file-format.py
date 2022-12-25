import os
import shutil
from pathlib import Path


def renameInvalid(data_path):
    files = list(Path(data_path).rglob("*.[cC][sS][vV]"))
    for file in files:

        filepath = ("/".join(file.parts)
                    ).replace("//", "/")
        newFilePath = filepath.replace("->>", "-++")
        old_dir = "/".join(filepath.split("/")[0:-1]) + "/"
        new_dir = "/".join(newFilePath.split("/")[0:-1]) + "/"

        if "OPTIONS" not in filepath:
            continue

        try:
            os.makedirs(new_dir)
        except FileExistsError:
            count = 1

        if os.path.isfile(filepath):
            shutil.copyfile(filepath, newFilePath)
            print('copied', newFilePath)


renameInvalid(
    "/Users/harshitagrawal/Desktop/projects/halfbottle/halfbottle-backtest/data/OPTIONS")
