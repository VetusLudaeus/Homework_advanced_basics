#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import argparse
import datetime
import configparser
import gzip
import json
import operator
import os
import re
import logging
from collections import namedtuple
from string import Template

""" 
Log Analyzer
The program is supposed to be used to analyze Nginx access logs in the predefined format.
Example of allowed log names:
    * nginx-access-ui.log-20170630.gz
    * nginx-access-ui.log-20170630.log
"""

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TEMPLATE": "./report.html",
    "MIN_QUALITY": 0.89,
    "SORT_BY": "time_sum"
}
last_file = namedtuple('last_file', ['file', 'date'])
file_name_reg = re.compile(r'^nginx-access-ui\.log-(\d{8})\.(gz|log)$')


def parse_config(config_path):
    conf = configparser.RawConfigParser(allow_no_value=True)
    conf.read(config_path)
    return dict((name.upper(), value) for (name, value) in conf.items('default'))


def get_log_lines(log_path):
    if log_path.endswith('.gz'):
        log = gzip.open(log_path, mode='rt', encoding='utf-8')
    else:
        log = open(log_path)

    for line in log:
        yield line

    log.close()


def parse_log_line(log_line):
    line_splits = log_line.split(' ')
    try:
        u = line_splits[7].strip()
        t = float(line_splits[-1].strip())
    except Exception as ignore:
        logging.debug(f'{ignore}')
        return None, None
    return u, t


def median(data):
    quotient, remainder = divmod(len(data), 2)
    return sorted(data)[quotient] if remainder else sum(sorted(data)[quotient - 1: quotient + 1]) / 2.0


def analyze_log(log, conf):
    logs_count = total = times_sum = 0
    urls_agg = dict()
    for log_line in log:
        u, t = parse_log_line(log_line)
        if u and t:
            urls_agg[u] = urls_agg.get(u, list()) + [t]
            times_sum += t
            logs_count += 1
        total += 1
    if float(logs_count) / total < float(conf['MIN_QUALITY']):
        raise Exception("Too many incorrect log lines")

    data = []
    for url, times in urls_agg.items():
        data.append({
            'url': url,
            'count': len(times),
            'count_perc': round(float(len(times)) / logs_count, 3),
            'time_avg': round(sum(times) / len(times), 3),
            'time_max': max(times),
            'time_med': median(times),
            'time_perc': round(sum(times) / times_sum, 3),
            'time_sum': sum(times)
        })

    data.sort(key=operator.itemgetter(conf['SORT_BY']), reverse=True)
    return data


def get_last_file_by_date_in_name(dir_path):
    try:
        list_of_files = os.listdir(dir_path)
    except FileNotFoundError as err:
        logging.info(f'Read error: {err}')

    else:
        last_file_name = last_date = None
        for file_name in list_of_files:
            if os.path.isfile(os.path.join(dir_path, file_name)) and re.search(file_name_reg, file_name):
                current_date = datetime.datetime.strptime(re.findall(file_name_reg, file_name)[0][0], '%Y%m%d')

                if last_file_name is None:
                    last_file_name = os.path.join(dir_path, file_name)
                    last_date = current_date

                if last_date < current_date:
                    last_file_name = os.path.join(dir_path, file_name)
                    last_date = current_date

        return last_file(last_file_name, last_date)


def report_data(data_for_report, report_file, conf):
    with open(conf['TEMPLATE'], "rb") as f:
        template = Template(f.read().decode("utf-8"))

    try:
        with open(report_file, 'wb') as fp:
            fp.write(template.safe_substitute(table_json=json.dumps(data_for_report)).encode("utf-8"))
    except Exception as err:
        logging.info(f'Write error: {err}')


def main():
    conf = config.copy()
    # create report directory if not exist
    os.makedirs(conf['REPORT_DIR'], exist_ok=True)

    # find the path and date for the last log file by name
    last_log = get_last_file_by_date_in_name(conf['LOG_DIR'])
    logging.info(f'selected log file: {last_log.file}')
    if last_log.file:
        report_file = os.path.join(conf['REPORT_DIR'], f'report-{last_log.date.strftime("%Y.%m.%d")}.html')
        if not os.path.exists(report_file):
            data = analyze_log(get_log_lines(last_log.file), conf)
            report_data(data[:int(conf['REPORT_SIZE'])], report_file, conf)
            logging.info(f'report file: {report_file}')
        else:
            logging.info(f'this log file has already been processed, report file: {report_file}')
    else:
        logging.info('matching log files do not exist')


if __name__ == "__main__":
    # set logging params
    logging.basicConfig(format='[%(asctime)s] %(levelname)s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S',
                        filename=config.get('LOGGING_FILE'),
                        level=logging.INFO)
    # parse args
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-c', '--config', type=str, nargs='?', dest='config',
                            help=f'Path to config file. Default config: {config}', default='./configs/conf.ini')
    args = arg_parser.parse_args()
    if os.path.isfile(args.config) and args.config:
        # parse config file and update config
        config.update(parse_config(args.config))

    logging.info(f'current config: {config}')
    main()
