# Purpose
`file_host` is a container that serves static mod files based on a git repo.
# Features
- Static files are served via `nginx`.
- (Unimplemented) Static files are updated periodically via `cronjob` from git.
- (Unimplemented) Manifest file is updated periodically via `cronjob` based on repo and original server.