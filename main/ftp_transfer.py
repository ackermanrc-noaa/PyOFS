# coding=utf-8
"""
FTP pulldown of custom PyOFS data slices (2 and 4 kilometer non-DA).

Created on Aug 9, 2018

@author: zachary.burnett
"""

import datetime
import ftplib
import os

FTP_URI = 'tidepool.nos.noaa.gov'
INPUT_DIR = '/pub/outgoing/CSDL'

DATA_DIR = os.environ['OFS_DATA']

OUTPUT_DIR = os.path.join(DATA_DIR, 'input')
LOG_DIR = os.path.join(DATA_DIR, 'log')

if __name__ == '__main__':
    start_time = datetime.datetime.now()

    # create boolean flag to determine if script found any new files
    num_downloads = 0

    # create folders if they do not exist
    for dir in [OUTPUT_DIR, LOG_DIR]:
        if not os.path.isdir(dir):
            os.mkdir(dir)

    # define log filename
    log_path = os.path.join(LOG_DIR, f'{datetime.datetime.now().strftime("%Y%m%d")}_ftp_transfer.log')

    # check whether logfile exists
    log_exists = os.path.exists(log_path)

    # write initial message
    with open(log_path, 'a') as log_file:
        message = f'{datetime.datetime.now().strftime("%Y%m%dT%H%M%S")} ({(datetime.datetime.now() - start_time).total_seconds():.2f}s): Starting FTP transfer...' + '\n'
        log_file.write(message)

    # instantiate FTP connection
    with ftplib.FTP(FTP_URI) as ftp_connection:
        ftp_connection.login()
        input_paths = ftp_connection.nlst(INPUT_DIR)

        for input_path in input_paths:
            with open(log_path, 'a') as log_file:
                extension = os.path.splitext(input_path)[-1]
                filename = os.path.basename(input_path)
                output_path = os.path.join(OUTPUT_DIR, filename)

                # filter for NetCDF and TAR archives
                if ('.nc' in filename or extension == '.tar') and 'mod' not in filename:
                    current_start_time = datetime.datetime.now()

                    # download file (copy via binary connection) to local destination if it does not already exist
                    if not (os.path.exists(output_path) and os.stat('somefile.txt').st_size > 232000):
                        with open(output_path, 'wb') as output_file:
                            ftp_connection.retrbinary(f'RETR {input_path}', output_file.write)
                            message = f'{datetime.datetime.now().strftime("%Y%m%dT%H%M%S")} ({(datetime.datetime.now() - current_start_time).total_seconds():.2f}s): Copied "{input_path}" to "{output_path}"'
                            log_file.write(message + '\n')
                            print(message)
                            num_downloads += 1
                    else:
                        message = f'{datetime.datetime.now().strftime("%Y%m%dT%H%M%S")} ({(datetime.datetime.now() - current_start_time).total_seconds():.2f}s): Destination file already exists: "{output_path}"'

                        # only write 'file exists' message on the first run of the day
                        if not log_exists:
                            log_file.write(message + '\n')
                        print(message)

    with open(log_path, 'a') as log_file:
        message = f'{datetime.datetime.now().strftime("%Y%m%dT%H%M%S")} (0.00s): Downloaded {num_downloads} files. Total time: {(datetime.datetime.now() - start_time).total_seconds():.2f} seconds' + '\n'
        log_file.write(message)
        print(message)

        if num_downloads == 0:
            exit(1)

    print('done')
