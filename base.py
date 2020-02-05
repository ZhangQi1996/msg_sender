#!python3
from ex import *
from abc import abstractmethod, ABC


class MsgSenderBase(ABC):

    # this is a list or none, used to store some cell nums or some nicknames that will recv msgs.
    MSG_RECEIVERS = None

    # this is a dict or none, stored a map reflecting from phone num to nickname.
    PHONENUM_NICKNAME_MAP = None

    # set debug mode, if true, it will not call the ex handling method
    DEBUG = False

    def init(self, *args, **kwargs):
        """
        init relevant settings or confs.
        override it
        :return:
        """
        pass

    def check_before(self, *args, **kwargs):
        """
        this method is used to check some settings or confs if they are suitable...
        you can override this method in a subclass
        :return: bool or a err_msg that is a str type
        """
        return True

    def exception_handler(self, e: Exception, *args, **kwargs):
        """
        this method will be called after an exception happens.
        you should override it if you want do sth after that situation.
        :param e:
        :return:
        """
        pass

    def main(self):
        """
        plz not modify or override this method and just call it unless you make sure what you will do..
        :return:
        """
        try:
            chk_ret = self.check_before()
            # no ret val
            if chk_ret is None:
                raise CheckingNotPassBeforeRunMsgSender("the method check_before expect a return_val..")
            # ret val is false
            if chk_ret is False:
                raise CheckingNotPassBeforeRunMsgSender()
            # ret val is a err_msg(str type)
            if isinstance(chk_ret, str):
                raise CheckingNotPassBeforeRunMsgSender(chk_ret)
            # do HA ops
            self.high_available_handler()
            self.run()
        except Exception as e:
            if not self.DEBUG:  # if at debug mode, not execs the ex handling method
                self.exception_handler(e)
            else:
                raise e
        finally:
            self.cleanup()

    def cleanup(self, *args, **kwargs):
        """
        do sth after the job
        you can override this method in a subclass
        :return: None
        """
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        just override it, and write down your transaction codes.
        :return:
        """

    def get_msg_send_api_interface(self, *args, **kwargs):
        """
        get an api interface like an url, an impl interface etc.
        maybe you should override this method.
        :return: api interface
        """
        pass

    @abstractmethod
    def msg_content_generate(self, *args, **kwargs):
        """
        uses to generate msg content.
        you should override it.
        :param args:
        :param kwargs:
        :return:
        """

    def send_before(self, *args, **kwargs):
        pass

    def send_after(self, *args, **kwargs):
        pass

    @abstractmethod
    def send_msg(self, msg, *args, **kwargs):
        """
        send msg to phonenum
        override it
        :return:
        """

    @staticmethod
    def high_available_handler(*args, **kwargs):
        """
        do some HA ops to make sure the program to run normally.
        e.g. uses zookeeper
        just overrides it.
        :return:
        """
        pass

