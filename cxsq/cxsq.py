import argparse
import datetime
import json
import logging
import traceback
from typing import Tuple
from random import choice

from hit.ids import idslogin
import requests
import yaml
from requests import Session

logging.basicConfig(level=logging.INFO)


def read_config(filename: str) -> Tuple[str, str]:
    try:
        logging.info("Reading config from %s", filename)
        o = open(filename, 'r')
        c: dict = yaml.load(o, Loader=yaml.SafeLoader)
        username = c['username']
        password = c['password']
        reasons = c.get('reasons', [' '])

        if not isinstance(reasons, list):
            raise TypeError()
        for reason in reasons:
            if not isinstance(reason, str):
                raise TypeError()

        ret = (username, password, reasons)
        return ret
    except OSError:
        logging.error('Fail to read configuration from %s', filename)
    except yaml.YAMLError:
        logging.error('Fail to parse YAML')
    except TypeError:
        logging.error('Wrong type in yaml')
    exit(1)


def get_xg_session(username: str, password: str) -> Session:
    # hit.ids.login()
    logging.info('Logging in to xg.hit.edu.cn')
    try:
        session = idslogin(username, password)
        session.get('https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/shsj/common')
        return session
    except Exception as e:
        logging.error('Failed to log in')
        logging.error(e)
        traceback.print_stack(e)
        exit(1)


def get_date() -> Session:
    pass


def main():
    arg_date_format = '%Y%m%d'
    arg_today = datetime.date.today().strftime(arg_date_format)
    arg_tomorrow = (datetime.date.today() +
                    datetime.timedelta(days=1)).strftime(arg_date_format)

    parser = argparse.ArgumentParser(
        prog='cxsq', description='Auto submitter for xg.hit.edu.cn cxsq')
    parser.add_argument('-c', '--conf-file',
                        help='Set config file path', required=True)
    date_group = parser.add_argument_group('date')
    date_group.add_argument('-t', '--today', action='append_const', dest='dates',
                            const=arg_today, help='add today to date list')
    date_group.add_argument('-T', '--tomorrow', action='append_const', dest='dates',
                            const=arg_tomorrow, help='add tomorrow to date list')
    date_group.add_argument('-d', '--dates', nargs='+', action='append', dest='dates',
                            metavar='date', help='yyyyMMdd, add several dates to date list')

    args = parser.parse_args()
    # rq -> 日期
    # cxly -> 出校理由
    # cxlx -> 出校类型
    # yjlxjsrq -> 离校日期
    # id
    if not args.dates:
        parser.error('No dates given, add -t, -T or -d')
    try:
        dates = []
        for i in args.dates:
            if isinstance(i, list):
                for _ in i:
                    dates.append(_)
            else:
                dates.append(i)
        datelist = [datetime.datetime.strptime(
            arg, arg_date_format).date() for arg in dates]
        logging.info('datelist: %s', datelist)
    except ValueError as e:
        parser.error('wrong date format, format is yyyyMMdd')
    username, password, reasons = read_config(args.conf_file)
    session = get_xg_session(username, password)
    date: datetime.date
    for date in datelist:
        try:
            logging.info('cxsq on %s', date.isoformat())
            cxsq(session, date, choice(reasons))
        except Exception as e:
            logging.error('error: %s', e)


def cxsq(session: Session, date: datetime.date, reason: str):
    try:
        response = session.post(
            'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsCxsq/getCxsq',
            data={'info': '{"id": "id"}'})
        if not response.ok:
            logging.error('response.status_code: %s', response.status_code)
            raise Exception('Failed to get getCxsq')
        logging.debug('response.status_code: %s', response.status_code)
        logging.debug('response.text: %s', response.text)
        cxsq = response.json()
        if not cxsq['isSuccess']:
            logging.error('response: %s', cxsq)
            raise Exception('Failed to get getCxsq')
        _id = cxsq['module']['id']
        # d.strftime('%m-%-d')
        # d.strftime('%-m-%-d')
        # '12-7'

        info = {
            'model': {
                'rq': date.isoformat(),
                'cxly': ' ',
                'cxlx': '01',
                'yjlxjsrq': '',
                'id': _id,
                'lsjcjg': '',
                'lsbgcjyy': '',
                'lsjcsj': '-undefined-undefined',
                'lsljjkmys': '',
                'lsdsjxcmys': '',
            }
        }
        body = {
            'info': json.dumps(info),
        }
        logging.debug(json.dumps(info))
        response = session.post(
            'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsCxsq/saveCxsq', data=body)
        if not response.ok:
            raise Exception('Failed to post saveCxsq')
        logging.debug(response.text)
        cxsq = response.json()
        if not cxsq['isSuccess']:
            raise Exception(cxsq['msg'])
        logging.info('successfully send cxsq, reason: %s', reason)
    except requests.RequestException as e:
        raise e
    except Exception as e:
        raise e


if __name__ == '__main__':
    main()
