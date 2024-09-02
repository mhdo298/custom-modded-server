# Purpose

`file_host` is a container that serves static mod files based on a git repo. Since we want to properly trigger updates from the client, we need to keep track of when the mod files have changed, which our server can then use to update its manifest file.

# Features

- Static files are served via `nginx`.
- Static files are updated periodically from a given `git` repo.
- Automatically generate `version` file for server to read from using `git`.


# Usage
The repository url is set in `repo.env`. 

Starting up the container:
```shell
$ docker compose up -d
```

Files and folders can be banned via `nginx.conf`. For example, `.git` is banned by default:
```
location ~ /\.git {
    deny all;
}
 ```
Add other paths after `.git` to ban them as well. Files that are not in the repo will lead to a 404 on request.
# Alternatives
It's likely that you'll be better off hosting files on external services. Please make sure that the service offers a path-like access structure. Each time an update is made to your files, remember to generate a `version` file with the following format for each row:

`(version name) (size in bytes) (file path)`

The version name should not contain spaces. For example:

`1 6424693 cards/card_data`

Even though this is a container, note that it needs to be a persistent daemon, likely making it a bad fit for services like GCP's cloud run. It would still make sense to deploy this in a node in a Kubernetes cluster or on a remote VM instance.