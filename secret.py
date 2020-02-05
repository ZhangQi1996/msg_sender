import requests
import json
from urllib import parse
from ex import MsgSendAPIException

"""
所提供的的账号密码请勿更改
请合理合法使用所提供的的账号密码
----------------------------
plz do not modify the acc and pw provided, and
use these accs in a suitable and legal way.  
"""

# 平台: 网建
# 网址: http://sms.sms.cn/?1580361084&
# 账号: zq12138
# 密码: zq15067522063
# 手机号: 17135192845
def func1(phone, content, nickname='你好'):
    url = 'http://api.sms.cn/sms/?'
    params = ['ac=send', 'uid=zq12138', 'pwd=3bfc51858f660d8b22a409cc03c037a9', 'template=527860',
              'mobile=%s' % phone, 'content=' + parse.quote('{"nickname": "%s", "content": "%s"}' % (nickname, content))]
    url = url + '&'.join(params)   # url编码
    rsp = requests.post(url)
    # {"stat":"100","message":"发送成功"}
    ret_data = parse.unquote(rsp.content.decode('utf-8'))
    if json.loads(ret_data)['message'] != '发送成功':
        raise MsgSendAPIException("api is called unsuccessfully.")


# https://new.dashboard.mob.com/#/
# 手机号18866478549
# 密码:zq15067522063
# 支持: 仅仅支持验证码的免费发送，详细请见登录后信息
# 注: 具体实现暂未实现
def func2(phone, content, nickname=''):
    pass