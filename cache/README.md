# Purpose

`cache` is a container that hosts a `redis` cache. This is helpful for storing frequently accessed data that would be
shared between requests and servers.

# Features

- Backs up data periodically into a `redis_backup` volume.
- Exposes the default port `6379` (**with no access control**).

# Usage

Starting up the container:

```shell
$ docker compose up -d
```

To add a password, hash it using `SHA-256` first, then add the following line to `redis.conf`:

`user default on #(the hash)`

An access link might look something like:

```
redis://default@redis/0
redis://default:password@redis/0
```

# Alternatives

[redis.io](https://redis.io/pricing/#) offers a free tier with 30MB worth of cache.

Even though this is a container, note that it needs to be a persistent daemon, likely making it a bad fit for services
like GCP's cloud run. It would still make sense to deploy this in a node in a Kubernetes cluster or on a remote VM
instance.