from base import MsgSenderBase
from ex import *
from utils import *
from configparser import ConfigParser
from threading import Thread
import time
from api import API
import traceback
import logging


def thread_wrapper(func):
    def run(*args, **kwargs):
        self = args[0]
        msg = args[1]
        self.send_before()
        func(self, msg, *args[2:], **kwargs)
        self.send_after()
        phonenum = kwargs['phonenum']
        nickname = self._phone_num_2nickname(phonenum)
        logging.info('发送给的%s的信息成功' % nickname)

    def wrapper(self, msg, *args, **kwargs):
        t = Thread(target=run, args=(self, msg, *args), kwargs=kwargs)
        t.start()
    return wrapper


class MyMsgSender(MsgSenderBase):

    def _product_msg_generator(self):
        times = {}
        while True:
            phonenum = yield
            nickname = self._phone_num_2nickname(phonenum)
            time = times.setdefault(phonenum, 1)
            msg = self.msg_content_generate(nickname=nickname, time=time)
            yield msg
            times[phonenum] = time + 1

    def msg_content_generate(self, *args, **kwargs):
        return "你家小哥哥会一直一直喜欢你的~~~"

    def get_msg_send_api_interface(self, *args, **kwargs):
        for api in API:
            yield api

    @thread_wrapper
    def send_msg(self, msg, *args, **kwargs):
        if kwargs.__contains__('phonenum') is False and kwargs.__contains__('phone_num') is False:
            raise ValueError('you should provide arg phonenum or phone_num')
        else:
            phone_num = kwargs['phonenum'] if kwargs.__contains__('phonenum') else kwargs['phone_num']
        for api in self.get_msg_send_api_interface():
            try:
                api(phone_num, msg, self._phone_num_2nickname(phone_num))
                logging.info(msg)
                return
            except Exception as e:
                traceback.print_exc()
                continue
        raise MsgSendFailedException(phone_num)

    def _get_msg(self, phonenum):
        """根据手机号获取消息"""
        self.msg_generator.send(None)
        return self.msg_generator.send(phonenum)

    def run(self, *args, **kwargs):
        # 这里实现给每个号码轮回发送信息
        # check_before已经确保全部是手机号
        while True:
            for phonenum in self.MSG_RECEIVERS:
                msg = self._get_msg(phonenum)
                self.send_msg(msg, phonenum=phonenum)
            self._wait()

    def _wait(self):
        """每次发送后等待若干秒"""
        time.sleep(100)

    def exception_handler(self, e: Exception, *args, **kwargs):
        """捕获异常，并发送邮件通知"""
        import traceback

        mail_content = '''
            <html>
                <body>
                    <h3>您的msg_sender出现异常</h3>
                    <p><font color="red">%s</font></p>
                </body>
            </html>
        ''' % traceback.format_exc()
        # 需要设置content
        self.email_conf['content'] = mail_content
        send_email(self.email_conf)

    def _read_email_conf_file(self, fp='email.ini', encoding='utf-8') -> None:
        conf = ConfigParser()
        conf.read(fp, encoding=encoding)
        # 确保有所有特定sec
        for sec in ('base', 'smtp', 'login'):
            if sec not in conf.sections():
                raise ConfFileIllegalException("the email conf file(%s) must have base, "
                                               "smtp and login section. but %s section not exists" % (fp, sec))

        self.email_conf = {}

        def local_check(check_iterable, sec):
            """检查sec中必须存在check_iterable中的所有项"""
            for op in check_iterable:
                if op not in conf.options(sec):
                    raise ConfFileIllegalException("the %s section must have %s options, but %s not exists"
                                                   % (sec, ",".join(check_iterable), op))
                else:
                    self.email_conf[op] = conf.get(sec, op).strip()
        # base section
        local_check(('from', 'to', 'subject'), 'base')
        self.email_conf['content_type'] = conf.get('base', 'content_type', fallback='text/html').strip()
        self.email_conf['content_encoding'] = conf.get('base', 'content_encoding', fallback='utf-8').strip()
        # smtp section
        local_check(('smtp_addr', 'smtp_port', 'smtp_use_ssl'), 'smtp')
        # login section
        local_check(('acc', 'pw'), 'login')
        self.email_conf['to'] = [_.strip() for _ in self.email_conf['to'].split(',')]

    def _read_recvrs_conf_file(self, fp='recvrs.conf', encoding='utf-8'):
        self.MSG_RECEIVERS = []
        with open(file=fp, mode='r', encoding=encoding) as f:
            while True:
                line = f.readline()
                # 读到文件末尾退出
                if not line:
                    break
                # 去除行前后空白
                line = line.strip()
                # 判断当前行是否为空行或者为注释行
                if len(line) == 0 or is_a_note(line):
                    continue
                # 删除行末注释以及其他空白符
                recvr = re.sub(r"#.*$", '', line).strip()
                self.MSG_RECEIVERS.append(recvr)

    def _read_map_conf_file(self, fp='map.conf', encoding='utf-8'):
        """
        在fp所指定的phone num到nickname映射文件中读取相关配置
        conf文件格式为
        =========================
        phonenum1 nickname1
        phonenum2 nickname2
        =========================
        :param fp:
        :param encoding:
        :return:
        """
        self.PHONENUM_NICKNAME_MAP = {}
        with open(file=fp, mode='r', encoding=encoding) as f:
            while True:
                line = f.readline()
                # 读到文件末尾退出
                if not line:
                    break
                # 去除行前后空白
                line = line.strip()
                # 判断当前行是否为空行或者为注释行
                if len(line) == 0 or is_a_note(line):
                    continue
                # 删除行末注释
                line = re.sub(r"#.*$", '', line).strip()
                # 将行根据空白拆分
                _ = re.split(r"\s+", line)
                if len(_) < 2:
                    raise ConfFilePerLineFormatException("phonenum nickname", 2, len(_))
                else:
                    phonenum, nickname = _
                    self.PHONENUM_NICKNAME_MAP[phonenum] = nickname

    def init(self, *args, **kwargs):
        """
        kwargs可中配置
        debug, 当是debug模式的时候程序出现异常不会触发ex_handler方法
        map_conf, map_conf_encoding
        recvrs_conf, recvrs_conf_encoding
        email_conf, email_conf_encoding
        不配置使用默认值
        :param args:
        :param kwargs:
        :return:
        """
        # 读取模式
        self.DEBUG = kwargs.setdefault('debug', False)  # 默认不是debug模式
        # 读取配置文件
        self._read_map_conf_file(kwargs.setdefault('map_conf', 'map.conf'),
                                 kwargs.setdefault('map_conf_encoding', 'utf-8'))
        self._read_recvrs_conf_file(kwargs.setdefault('recvrs_conf', 'recvrs.conf'),
                                    kwargs.setdefault('recvrs_conf_encoding', 'utf-8'))
        self._read_email_conf_file(kwargs.setdefault('email_conf', 'email.ini'),
                                   kwargs.setdefault('email_conf_encoding', 'utf-8'))
        self.msg_generator = self._product_msg_generator()
        return self

    def _phone_num_2nickname(self, phonenum: str) -> str:
        """
        this method will try to convert it to a nickname.
        in failure, raise an exception
        """
        nickname = self.PHONENUM_NICKNAME_MAP[phonenum]
        if nickname is None:
            raise NotExistPhoneNumReflectionException(phonenum)
        return nickname

    def _nickname2phone_num(self, nickname: str) -> str:
        """找到第一个满足的"""
        for key in self.PHONENUM_NICKNAME_MAP:
            if self.PHONENUM_NICKNAME_MAP[key] == nickname:
                return key
        raise NickNameException("cannot find a nickname(%s) to phone num.." % nickname)

    def check_before(self, *args, **kwargs):
        """确保PHONENUM_NICKNAME_MAP与MSG_RECEIVERS不空,且MSG_RECEIVERS中全部是手机号"""
        if not check_is_dict_and_not_empty(self.PHONENUM_NICKNAME_MAP):
            raise CheckingNotPassBeforeRunMsgSender("PHONENUM_NICKNAME_MAP should be a dict type and not empty..")
        if not check_is_list_and_not_empty(self.MSG_RECEIVERS):
            raise CheckingNotPassBeforeRunMsgSender("MSG_RECEIVERS should be a list type and not empty..")
        for phone_num in self.PHONENUM_NICKNAME_MAP.keys():
            # check format of a cell num not passing
            if not check_phone_num(phone_num):
                raise PhoneNumFormatException(phone_num)
        # 保证MSG_RECEIVERS全部为手机号
        for k, v in enumerate(self.MSG_RECEIVERS):
            if not check_phone_num(v):  # 不是手机号
                self.MSG_RECEIVERS[k] = self._nickname2phone_num(v)     # 转为手机号
        return True