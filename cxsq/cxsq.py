import hit
from requests import Session
import logging
import yaml
import json
import argparse
import datetime


from typing import Tuple

logging.basicConfig(level=logging.INFO)


def read_config() -> Tuple:
    # username
    # password
    
    pass


def get_xg_session() -> Session:
    # TODO
    # hit.ids.login()
    pass

def get_date() -> Session:
    pass

def main():
    parser = argparse.ArgumentParser(
        prog='cxsq', description='Auto submitter for xg.hit.edu.cn cxsq')
    parser.add_argument('-c', '--conf-file', help='Set config file path', required=True)

    args = parser.parse_args()
    # rq -> 日期
    # cxly -> 出校理由
    # cxlx -> 出校类型
    # yjlxjsrq -> 离校日期
    # id
    (username, password, brzgtw, gnxxdz) = read_config(args.conf_file)
    
def cxsq(session: Session, date: datetime.date):
    try:
        session: Session = get_xg_session()
        response = session.post(
            'https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xsCxsq/getCxsq', data={'id': 'id'})
        cxsq = json.loads(response.text)
        if not cxsq['isSuccess']:
            raise Exception('Failed to get getCxsq')
        id = cxsq['module']['id']
        # d.strftime('%m-%-d')
        # d.strftime('%-m-%-d')
        # '12-7'

        info = {
            'module': {
                'rq': date.strftime('%Y-%-m-%-d'),
                'cxly': '',
                'cxlx': '01',
                'yjlxjsrq': '',
                'id': id,
            }
        }
        body = {
            'info': json.dumps(info),
        }
    except:
        pass
