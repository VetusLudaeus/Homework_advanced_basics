import os
import unittest

import datetime

import log_analyzer

logs = [
    u'1.168.65.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/internal/banner/24294027/info HTTP/1.1" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 0.146',
    u'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/1769230/banners HTTP/1.1" 200 1020 "-" "Configovod" "-" "1498697422-2118016444-4708-9752747" "712e90144abee9" 0.628',
    u'1.194.135.240 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "1498697422-3979856266-4708-9752772" "8a7741a54297568b" 0.067',
    u'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752771" "712e90144abee9" 0.138',
    u'1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/appinstall_raw/2017-06-29/ HTTP/1.0" 200 28358 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" "-" "-" "-" 0.003',
    u'1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4822/groups HTTP/1.1" 200 22 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752773" "2a828197ae235b0b3cb" 0.157',
    u'1.195.208.16 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/test/auth/ HTTP/1.0" 401 55 "https://rb.mail.ru/api/v2/test/auth/" "MR HTTP Monitor" "-" "1498697423-1957913694-4708-9752786" "-" 0.003',
    u'1.195.28.16 -  - [29/Jun/2017:03:50:23 +0300] "GET /accounts/login/ HTTP/1.0" 200 9982 "https://rb.mail.ru/accounts/login/" "MR HTTP Monitor" "-" "1498697423-1957913694-4708-9752785" "-" 0.035',
    u'1.200.76.128 f032b48fb33e1e692  - [29/Jun/2017:03:50:23 +0300] "GET /api/1/banners/?campaign=7789704 HTTP/1.1" 200 604049 "-" "-" "-" "1498697421-4102637017-4708-9752733" "-" 2.577',
    u'1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/25040266 HTTP/1.1" 200 984 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752765" "dc7161be3" 1.680',
    u'scdscdsdc',
]


def logs_gen():
    for log in logs:
        yield log


class LogAnalyzerTest(unittest.TestCase):

    def setUp(self):
        self.config = {
            "REPORT_SIZE": 100,
            "REPORT_DIR": "./reports",
            "LOG_DIR": "./logs",
            "LOGGING_FILE": "./logging/tmp/logging.log",
            "MIN_QUALITY": 0.89,
        }

    def test_should_not_return_last_create_file_from_dir(self):
        self.assertIsNone(log_analyzer.get_last_file_by_date_in_name('some_dit'))

    def test_should_not_returned_logs(self):
        with self.assertRaises(FileNotFoundError):
            log_analyzer.get_log_lines('some_file').__next__()

    def test_should_build_analyze_data(self):
        self.assertIsNotNone(log_analyzer.analyze_log(logs_gen()))

    def test_should_not_build_analyze_data(self):
        with self.assertRaises(Exception):
            log_analyzer.analyze_log(logs_gen(), 0.999)

    def test_should_report_analyze_data(self):
        report_file = f"{self.config['REPORT_DIR']}/report-{datetime.date.today().strftime('%Y.%m.%d')}.html"
        data = log_analyzer.analyze_log(logs_gen())
        log_analyzer.report_data(data, report_file)
        self.assertTrue(os.path.isfile(report_file))
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), report_file)
        os.remove(path)


if __name__ == '__main__':
    unittest.main()
