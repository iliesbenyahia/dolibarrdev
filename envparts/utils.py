import os
import shutil
import requests

def replaceInFiles(root_dir, replacements):
    with os.scandir(root_dir) as it:
        for entry in it:
            if not entry.is_file():
                continue

            with open(entry.path, 'r') as file:
                filedata = file.read()

            for search_text, replace_text in replacements.items():
                filedata = filedata.replace(search_text, replace_text)

            with open(entry.path, 'w') as file:
                file.write(filedata)

