# docker-backer
Make an archive of a given folder to specified location using a cron periodically

Available on `docker-hub`: `docker pull helife/docker-backer`

## Run with docker manually:

Imagine you have a `/data` folder that you need to backup `every day at 23:00` to `/backups`
```bash
docker run --detach --rm \
  --name docker-backup-service
  -v /backups:/backup \
  -v /data:/data:ro \
  helife/docker-backer  \
  -d /data \
  -b /backups \
  -c '0 23 * * *'
```
The script will now run unless stopped or the machine is turned off and 

Run a backup manually when the script is already on:
```bash
# You need to specify again the data folder and backup folder
# It is made like this so you can backup specific things if wanted
# In case you have other folders 
docker exec docker-backup-service -d /data -b /backups -m
```

## Compose Example

```yaml
---
version: '3'

services:
    docker-backup-service:
        image: helife/docker-backer
        restart: unless-stopped
        command:
            - "--directory=/data"
            - "--backup=/backups"
            - "--cron='* * * * *'"
        volumes:
            - /data:/data:ro
            - /backups:/backups
```

## Changes to come

Because it is hard to make a real backup this way I intend to change the way the data is backed up.
The docker will consider /data as it's root folder so you can put `/` as `/data` `(but may not be recommended)` and will hold a dynamic configuration as a json to backup all datas

```json
{
    "data": [
        "file1path", "file2path", "file3path"
    ],
    "backup_location": "path"
}
```

The data will then be outputed like this:

```json
{
    "version": "version-string",
    "data": [
        {
            "filename": "file1path",
            "is_archive": true,
            "rodata": "base64data=="
        }

        {
            "filename": "file2path",
            "is_archive": false,
            "rodata": "base64data=="
        }
    ]
}
```

When is archive is true it means that the given file is a folder otherwise it is a single file

It will then be minified and compressed to avoid losing too much space
Another possibility could be using SQL instead and generating a sql static file but that would require a sql server and make the project much less lightweight :/

ZIP may be used instead of tar to enforce encryption

A restoring docker service that can be used to restore all backed up files when runned.

It will simply decompress and decrypt the file then populate at the good locations
A flask service could also be on to restore the backup and ensure 'healthcheck'

A flask service for the backup service also

Finally an interface to write plugins to send files to clouds
