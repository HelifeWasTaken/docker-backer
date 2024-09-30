from argparse import ArgumentParser, Namespace as ArgParseNamespace
from pathlib import Path
from json import load as json_load, dump as json_dump
from random import randbytes
from shutil import make_archive
from base64 import b64encode
from datetime import datetime
from zipfile import ZipFile

def _get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def _add_log(base, hash, content: str) -> None:
    return f'{base}\n({hash}) - [{_get_time()}] - {content}'

def _make_hash() -> str:
    return ''.join([f'{x:02x}' for x in randbytes(8)])

class BackupService:

    VERSION = '1'

    def __init__(self, config_path) -> None:
        self.config = Path(config_path)

    def backup(self) -> (int, str):
        '''
        Returns -1 if a fatal error occured
        Returns 0 if the backup was successful
        Returns n For n recoverable errors
        Always returns a log as second argument
        '''

        task_hash = _make_hash()
        log = _add_log('', task_hash, f'Starting backup of {self.config}')

        if not self.config.exists():
            return -1, _add_log(log, task_hash, f'Config file {self.config} does not exist')
        
        current_config = None

        try:
            with open(self.config) as file:
                current_config = json_load(file)
            if not isinstance(current_config, dict):
                raise ValueError(f'File does not contain a dictionary')
        except Exception as e:
            return -1, _add_log(log, task_hash, f'Error reading config file: {e}')

        if not isinstance(current_config.get('backup_location'), str):
            return -1, _add_log(log, task_hash, f'Invalid config file, backup_location is not a string or field missing')
        if not isinstance(current_config.get('data'), list):
            return -1, _add_log(log, task_hash, f'Invalid config file, data is not a list or field is missing')

        to_remove = []
        for data in current_config['data']:
            if not isinstance(data, str):
                log = _add_log(log, task_hash, f'Invalid data entry {data}, not a string (ignoring)')
                to_remove.append(data)
            elif not Path(data).exists():
                log = _add_log(log, task_hash, f'Invalid data entry {data}, does not exist (ignoring)')
                to_remove.append(data)
        
        for data in to_remove:
            current_config['data'].remove(data)

        backup_location = Path(current_config['backup_location'])
        if not backup_location.exists():
            backup_location.mkdir(parents=True)

        ecount = len(to_remove)

        first = True

        backup_name = f'{_get_time()}-{task_hash}'
        backup_name_json = backup_location / f'{backup_name}.json'

        with open(backup_name_json, 'w+') as file:
            file.write(f'{{"version":"{BackupService.VERSION}","data":[')

            for data in current_config['data']:
                data = Path(data)
                encoded_data = None
                data_type = None

                if data.is_dir():
                    data_type = 'dir'
                    # make an archive then encode it in base64 and write it to the file
                    archive_name = f'{backup_location}-{data.name}-{_get_time()}'
                    try:
                        archive_path = make_archive(archive_name, 'zip', data)
                    except Exception as e:
                        log = _add_log(log, task_hash, f'Error making archive {archive_name}: {e}')
                        ecount += 1
                        continue
                    try:
                        with open(archive_path, 'rb') as archive:
                            encoded_data = b64encode(archive.read())
                    except Exception as e:
                        log = _add_log(log, task_hash, f'Error reading archive {archive_path}: {e}')
                        ecount += 1
                        Path(archive_path).unlink()
                        continue
                    Path(archive_path).unlink()
                else:
                    # encode the file in base64 and write it to the file
                    data_type = 'file'
                    try:
                        with open(data, 'rb') as dataf:
                            encoded_data = b64encode(dataf.read())
                    except Exception as e:
                        log = _add_log(log, task_hash, f'Error reading file {data}: {e}')
                        ecount += 1
                        continue
                encoded_data = encoded_data.decode('utf-8')
                if not first:
                    file.write(',')
                else:    
                    first = False
                file.write(f'{{"type":"{data_type}","name":"{data.name}","data":"{encoded_data}"}}')
            file.write(']}')

        # compress the file
        try:
            archive_path = backup_location / f'{backup_name}.zip'
            with ZipFile(archive_path, 'w') as archive:
                archive.write(backup_name_json, backup_name_json.name)
        except Exception as e:
            log = _add_log(log, task_hash, f'Error making final archive {backup_location / f"{_get_time()}-{task_hash}.json"}: {e}')
            ecount += 1
            return ecount, log
        Path(backup_name_json).unlink()
        return ecount, _add_log(log, task_hash, f'Backup finished with {ecount} errors and saved to {archive_path}')

    @staticmethod
    def from_args(args):# -> (ArgParseNamespace, BackupService):
        parser = ArgumentParser(description='Backup service')
        parser.add_argument('--config', '-f', type=str, help='Config file', required=True)
        args = parser.parse_args(args)
        return BackupService(args.config)
