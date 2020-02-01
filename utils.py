import re
from email.mime.text import MIMEText
import smtplib
from ex import ConfIllegalException
import sys


def is_a_note(s: str):
    """s是否是一条注释，即是#开头的"""
    s = s.strip()
    if re.match(r"^\s*#", s) is None:
        return False
    else:
        return True


def check_is_dict_and_not_empty(o):
    if isinstance(o, dict) and len(o) > 0:
        return True
    else:
        return False


def check_is_list_and_not_empty(o):
    if isinstance(o, list) and len(o) > 0:
        return True
    else:
        return False


def check_phone_num(phonenum):
    """
    check if the phone num is valid
    if you wanna change this regex you can override this method.
    :return: bool
    """
    if re.match(r"^(?:\+?86)?1(?:3\d{3}|5[^4\D]\d{2}|8\d{3}|7"
                r"(?:[01356789]\d{2}|4(?:0\d|1[0-2]|9\d))|9[189]\d{2}|6[567]\d{2}|4[579]\d{2})\d{6}$", phonenum) is None:
        return False
    else:
        return True


def _send_email_check_before(conf: dict):
    if conf is None:
        raise ConfIllegalException("the conf arg cannot be null...")
    for _ in ('from', 'subject', 'content', 'smtp_addr', 'acc', 'pw'):
        if not isinstance(conf[_], str):
            raise ConfIllegalException("conf['%s'] must be str type, but accepts a %s type" % (_, type(conf[_])))
    if not isinstance(conf['to'], list):
        raise ConfIllegalException("conf['to'] must be list type, but accepts a %s type" % type(conf['to']))
    if isinstance(conf['smtp_use_ssl'], str) and conf['smtp_use_ssl'] in ('true', 'false'):
        conf['smtp_port'] = True if conf['smtp_port'] == 'true' else False
    elif not isinstance(conf['smtp_use_ssl'], bool):
        raise ConfIllegalException(
            "conf['smtp_use_ssl'] must be bool type, but accepts a %s type" % type(conf['smtp_use_ssl']))
    else:
        raise ConfIllegalException(
            "conf['smtp_use_ssl'] cannot be %s" % conf['smtp_use_ssl'])
    if isinstance(conf['smtp_port'], str):
        conf['smtp_port'] = int(conf['smtp_port'])
    elif not isinstance(conf['smtp_port'], int):
        raise ConfIllegalException(
            "conf['smtp_port'] must be int type, but accepts a %s type" % type(conf['smtp_port']))


def send_email(conf: dict):
    """
    conf(dict):
    REQUIRED:
        from(str): 从什么地方发
        to(list): 发给谁
        subject(str): 主题
        content(str): 内容
        smtp_addr(str): smtp服务器地址
        smtp_use_ssl(bool): 是否使用ssl
        smtp_port(int): 服务器端口
        acc(str): 发送邮件的账户
        pw(str): 发送账户的密码
    OPTIONS:
        content_type(str, dft: 'html'): 发送的内容类型
        content_encoding(str, dft: 'utf-8'): 发送内容的编码
    :param conf:
    :return:
    """
    # 保证required的都是不空且符合类型
    _send_email_check_before(conf)
    content = MIMEText(conf['content'], conf.setdefault('content_type', 'html'),
                       conf.setdefault('content_encoding', 'utf-8'))
    recvrs = ",".join(conf['to'])
    content['To'] = recvrs  # 接收者，多个接收者之间用逗号隔开
    content['From'] = str(conf['from'])  # 邮件的发送者,最好写成str("这里填发送者")，不然可能会出现乱码
    content['Subject'] = conf['subject']  # 邮件的主题

    if conf['smtp_use_ssl']:
        smtp_server = smtplib.SMTP_SSL(conf['smtp_addr'], conf['smtp_port'])
    else:
        smtp_server = smtplib.SMTP(conf['smtp_addr'], conf['smtp_port'])
    smtp_server.login(conf['acc'], conf['pw'])
    smtp_server.sendmail(conf['from'], conf['to'], content.as_string())
    smtp_server.quit()


def json_str2dict(json_str: str):
    """将json格式的字符串转成dict格式"""
    import json
    return json.loads(json_str)


def md5(tgt: bytes) -> str:
    """将目标字节数组转换成md5加密的16进制字符串"""
    import hashlib
    m = hashlib.md5()
    m.update(tgt)
    return m.hexdigest()


def str2md5(tgt_str: str, encoding='utf-8') -> str:
    """
    md5加密返回16进制字符串
    :param tgt_str:
    :param encoding: 对tgt_str编码成bytes
    :return:
    """
    return md5(tgt_str.encode(encoding))


def conf_log(stream=sys.stderr, level='DEBUG', format='%(asctime)s [%(levelname)s] %(message)s', date_fmt='%Y-%m-%d %H:%M:%S'):
    """
    设置log
    :param stream: 写文件可以stream=open('my_logs.log', 'a', 'utf-8')
    :param level:
    :param format:
    :param date_fmt:
    :return:
    """
    import logging
    logging.basicConfig(stream=stream, level=level, datefmt=date_fmt, format=format)
