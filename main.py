from impl import MyMsgSender
from utils import conf_log
if __name__ == '__main__':
    # 配置全局的日志
    conf_log()
    # you should call the func init before main.
    MyMsgSender().init().main()
