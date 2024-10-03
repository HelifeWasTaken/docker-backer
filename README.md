# docker-backer
Make an archive of a given folder to specified location using a cron periodically

Available on `docker-hub`: `docker pull helife/docker-backer`

## Run with docker manually:

Imagine you have a `/data` folder that you need to backup `every day at 23:00` to `/backup`
```bash
docker run --detach --rm \
  --name docker-backup-service
  -v /backup:/backup \
  -v /data:/data:ro \
  helife/docker-backer  \
  --cron='0 23 * * *'
```
The script will now run unless stopped or the machine is turned off and 

Run a backup manually when the script is already on:
```bash
docker exec docker-backup-service --single
```

Restore the data from a specific backup
```bash
docker exec docker-backup-service --restore 'backup-2024-10-01-03-18-27.zip'
```

Restore from the latest backup
```bash
docker exec docker-backup-service --restore 'latest'
```

## Compose Example:

```yaml
---
version: '3'

services:
  docker-backup-service:
    image: helife/docker-backer:latest
    restart: unless-stopped
    command: "--cron='0 23 * * *'"
    volumes:
      - ./data:/data:ro
      - ./backup:/backup
```

## Additionnals arguments:
```bash
usage: docker-backer [-h] [--data DATA] [--backup BACKUP]
                     [--cron CRON] [--single]
                     [--restore RESTORE]

Backup service

options:
  -h, --help                    | show this help message and exit
  --data DATA, -d DATA          | Data directory to backup
  --backup BACKUP, -b BACKUP    | Backup directory
  --cron CRON, -c CRON          | Cron schedule
  --single, -s                  | Run a single time
  --restore RESTORE, -r RESTORE | Restore backup
```

## Changes to come:

Enforce encryption

An interface to write plugins to send/restore files to/from clouds
