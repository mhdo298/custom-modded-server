import json
import os
import time

import requests
from flask import Flask, send_file, redirect
from redis import Redis, exceptions

app = Flask(__name__)
r = Redis.from_url(os.getenv('REDIS_HOST'))
base_url = os.getenv('ASSETS_URL')
filehost_url = os.getenv('FILE_HOST')
OAPM_path = "/temp/OriginalAssetPathsManifest"
modded_version_path = "/temp/version"
CSCA_path = "/temp/ClientServerContentAssociations.txt"


def get_or_default(param, method, default=None, attempts=10, timeout=0.5):
    error = None
    for _ in range(attempts):
        try:
            return method(param) or default
        except exceptions.ConnectionError as exc:
            time.sleep(timeout)
            error = exc
    if default is None:
        if error is not None:
            raise error
    return default


def check_if_file_changed(url_path, file_path, attempts=2, timeout=2.5):
    print(url_path)
    if os.path.exists(file_path):
        headers = {
            'if_modified_since': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(os.path.getmtime(file_path)))}
    else:
        headers = None
    req = None
    for _ in range(attempts):
        try:
            req = requests.get(url_path, timeout=timeout, headers=headers)
        except requests.exceptions.Timeout as e:
            print(f'Server timed out, check if URL is still valid: {e}.')
            pass
    if req and req.text:
        return req.text
    else:
        return ''


@app.route('/')
def index():
    return f'<p>page is online</p>'


@app.route("/ClientServerContentAssociations.txt")
def client_server():
    content = check_if_file_changed(base_url + "/ClientServerContentAssociations.txt", CSCA_path)
    if content:
        latest_version = next(reversed(sorted(json.loads(content).keys())))
        # TODO: add ability to specify client version
        data = {
            latest_version: {
                "appVersions": [
                    "1.50.2",
                    "1.50.7"
                ],
                "serverVersion": "6e4e821fdeb9d05793cacff5b9183387"
            }
        }
        content = json.dumps(data)
        with open(CSCA_path, 'w') as f:
            f.write(content)
    return send_file(CSCA_path, conditional=True)


@app.route("/<platform>/<version>/manifest_version")
def manifest_version(platform, version):
    version = get_or_default('manifest', r.incr, 1)
    return str(version)


def version_file_to_dict(version_file, old_dict):
    version_dict = {}
    for lines in version_file.strip().split("\n"):
        data = lines.split(" ", 3)
        if len(data) != 3:
            print(f'{data} does not conform to required format, skipped.')
            continue
        internal_ver, size, server_name = data
        if server_name.endswith('_live'):
            live = True
            name = server_name[:-5]
        else:
            live = False
            name = server_name
        parts = name.rsplit('_', 1)
        if parts[-1].isdigit():
            name = parts[0]
        version = 1
        if internal_ver in old_dict:
            version = old_dict[name]["Version"]
            if internal_ver != old_dict[name]["Hash"]:
                version += 1
        version_dict[name] = {"Hash": internal_ver, "Size": size, "Version": version, "Live": live, "Path": server_name,
                              "Name": name.rsplit("/", 1)[-1]}
    return version_dict


def get_up_to_date_version(check=True):
    # TODO: If the file host is local, just compare getmtime between modded_version_path and /src/version
    if check or not os.path.isfile(modded_version_path):
        modded_content = check_if_file_changed(filehost_url + f'/version', modded_version_path)
        if modded_content:
            if os.path.isfile(modded_version_path):
                with open(modded_version_path, 'r') as f:
                    old_modded_content = f.read()
            else:
                old_modded_content = '{}'
            version_cache = version_file_to_dict(modded_content, json.loads(old_modded_content))
            with open(modded_version_path, 'w') as f:
                f.write(json.dumps(version_cache))
            return version_cache
    if os.path.isfile(modded_version_path):
        with open(modded_version_path, 'r') as f:
            version_cache = json.loads(f.read())
    else:
        version_cache = {}
    return version_cache


@app.route("/<platform>/<version>/AssetPathsManifest")
def asset_paths_manifest(platform, version):
    content = check_if_file_changed(base_url + f'/{platform}/{version}/AssetPathsManifest', OAPM_path)
    if content:
        with open(OAPM_path, 'w') as f:
            f.write(content)
    else:
        if os.path.isfile(OAPM_path):
            with open(OAPM_path, 'r') as f:
                content = f.read()
        else:
            content = '{}'
    content = json.loads(content)

    version_cache = get_up_to_date_version()
    for file in version_cache:
        content['BundleNameToDetails'][file]["Size"] = version_cache[file]["Size"]
        if version_cache[file]["Live"]:
            content['BundleNameToDetails'][file]["Version"] = int(get_or_default('manifest', r.get, 1))
        else:
            content['BundleNameToDetails'][file]["Version"] = version_cache[file]["Version"]
    return json.dumps(content)


@app.route("/<platform>/<version>/<path:request_file>")
def assets(platform, version, request_file):
    version_cache = get_up_to_date_version(check=False)
    if request_file in version_cache:
        # TODO: Instead of send file, just have nginx run in front of the whole system, and we can skip the check too.
        # Basically, if the host is local, then we shouldn't have to touch anything here since nginx will deal with it for us.
        if filehost_url == 'http://filehost':
            return send_file(f'/src/{version_cache[request_file]["Path"]}',
                             # download_name=version_cache[request_file]["Name"],
                             conditional=True, mimetype=None)
        return redirect(f'{filehost_url}/{version_cache[request_file]["Path"]}')
    else:
        return redirect(f'{base_url}/{platform}/{version}/{request_file}')
