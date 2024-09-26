import os
import sys
import argparse
import shutil
import pathlib
import time
import datetime

from crontab import CronTab

def _get_time():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def backup(directory, backup):
    shutil.make_archive(f"{backup}/backup-{_get_time()}", 'zip', directory)
    print(f"{_get_time()} - Backup created")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Backup service')

    parser.add_argument('--directory', '-d', type=str, help='Directory to backup', required=True)
    parser.add_argument('--backup', '-b', type=str, help='Backup directory', required=True)
    parser.add_argument('--cron', '-c', type=str, help='Cron schedule', required=False)
    parser.add_argument('--manual', '-m', action='store_true', help='Run backup manually')

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"Directory {args.directory} does not exist")
        sys.exit(1)

    # Create backup directory if it does not exist
    if not os.path.exists(args.backup):
        os.makedirs(args.backup)

    dir = pathlib.Path(args.directory)
    backup = pathlib.Path(args.backup)
    if dir.samefile(backup):
        print("Backup and directory cannot be the same", file=sys.stderr)
        sys.exit(1)

    if args.manual and args.cron:
        print("Cannot use manual and cron together", file=sys.stderr)
        sys.exit(1)

    if args.manual:
        backup(args.directory, args.backup)
        sys.exit(0)
    
    cron = CronTab(args.cron, loop=True)
    while True:
        time.sleep(cron.next()) 
