import json

import requests
import os


def open_file():
    try:
        with open('AssetPathsManifest', 'r') as f:
            return f.read()
    except FileNotFoundError as e:
        fallback_url = os.environ["FALLBACK_URL"] + '/AssetPathsManifest'
        print(f"No AssetPathsManifest file found, downloading from {fallback_url}...")
        return requests.get(fallback_url).text


data = json.loads(open_file())

updated_files = input().split(os.sep)

# for files in updated_files:
for file in updated_files:
    filedata = data['BundleNameToDetails'][file]
    filedata['Size'] = os.path.getsize(file)
    filedata['Version'] += 1

with open('AssetPathsManifest', 'w') as f:
    json.dump(data, f)
