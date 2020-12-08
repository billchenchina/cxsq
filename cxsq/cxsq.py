import hit
from requests import Session
import logging
import yaml
import json
import argparse
import datetime
import traceback


from typing import Tuple

logging.basicConfig(level=logging.INFO)


def read_config(filename: str) -> Tuple[str, str]:
    try:
        logging.info("Reading config from %s" % filename)
        o = open(filename, 'r')
        c = yaml.load(o, Loader=yaml.SafeLoader)
        ret = (c['username'], c['password'])
        return ret
    except OSError:
        logging.error('Fail to read configuration from %s' % filename)
    except yaml.YAMLError:
        logging.error('Fail to parse YAML')
    exit(1)


def get_xg_session(username: str, password: str) -> Session:
    # TODO
    # hit.ids.login()
    logging.info('Logging in to xg.hit.edu.cn')
    try:
        session = hit.ids.idslogin(username, password)
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
    date_group.add_argument('-d', '--dates', nargs='+', action='extend', dest='dates',
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
        datelist = [datetime.datetime.strptime(
            arg, arg_date_format).date() for arg in args.dates]
        logging.info('datelist: ' + str(datelist))
    except Exception as e:
        parser.error('wrong date format, format is yyyyMMdd')
    username, password = read_config(args.conf_file)
    session = get_xg_session(username, password)
    date: datetime.date
    for date in datelist:
        try:
            logging.info('cxsq on ' + date.isoformat())
            cxsq(session, date)
        except Exception as e:
            logging.error('error: ' + str(e))


def cxsq(session: Session, date: datetime.date):
    try:
        response = session.post(
            'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsCxsq/getCxsq', data={'info': '{"id": "id"}'})
        if not response.ok:
            logging.error('response.status_code:' + str(response.status_code))
            raise Exception('Failed to get getCxsq')
        logging.debug('response.status_code:' + str(response.status_code))
        logging.debug('response.text:' + response.text)
        cxsq = response.json()
        if not cxsq['isSuccess']:
            logging.error('response: ' + str(cxsq))
            raise Exception('Failed to get getCxsq')
        id = cxsq['module']['id']
        # d.strftime('%m-%-d')
        # d.strftime('%-m-%-d')
        # '12-7'

        info = {
            'model': {
                'rq': date.strftime('%Y-%-m-%-d'),
                'cxly': ' ',
                'cxlx': '01',
                'yjlxjsrq': '',
                'id': id,
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
    except Exception as e:
        raise e


if __name__ == '__main__':
    main()
