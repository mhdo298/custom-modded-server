#!/bin/bash
git -C /src init
while true
do
  git -C /src pull "$REPO_URL"
  git -C /src ls-files --format='%(objectname) %(objectsize) %(path)' > /src/version
  sleep 60
done