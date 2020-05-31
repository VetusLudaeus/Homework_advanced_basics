#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import gzip
import os

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def main():
    path = os.getcwd()
    print(os.listdir(path))  # TODO delete this
    os.makedirs(config['REPORT_DIR'], exist_ok=True)
    os.makedirs(config['LOG_DIR'], exist_ok=True)
    check_new_log(path)
    # with gzip.open()


def check_new_log(path):
    print(os.listdir('./logs'))


if __name__ == "__main__":
    main()
