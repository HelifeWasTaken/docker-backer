from sys import argv
from backup_service import BackupService
import time

if __name__ == '__main__':

    b = BackupService('config.json')
    while True:
        e, log = b.backup()
        print(e)
        print(log)
        time.sleep(10)