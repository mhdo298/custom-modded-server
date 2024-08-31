# Purpose

`file_host` is a container that serves static mod files based on a git repo. Since we want to properly trigger updates from the client, we need to keep track of when the mod files have changed, which our server can then use to update its manifest file.

# Features

- Static files are served via `nginx`.
- Static files are updated periodically from git.
- Automatically generate `versions` file for server to read from.


# Usage
First, set the repository name in `upadater.env`. Then do:

    $ docker compose up


