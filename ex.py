class NickNameException(Exception):
    pass


class PhoneNumException(Exception):
    pass


class NotExistPhoneNumReflectionException(PhoneNumException):
    def __init__(self, phonenum):
        super().__init__("there not exists a reflection from phonenum '%s' to nickname..." % phonenum)


class PhoneNumReflectionNotUniqueException(PhoneNumException):
    def __init__(self, phonenum):
        super().__init__("there exists more than a reflection from phonenum '%s' to nickname, "
                         "plz make sure that it is unique..." % phonenum)


class CheckingNotPassBeforeRunMsgSender(Exception):
    def __init__(self, *args):
        if len(args) == 0:
            super().__init__("checking not pass before running msg sender..")
        else:
            super().__init__(args)


class ConfIllegalException(Exception):
    pass


class ConfFileIllegalException(ConfIllegalException):
    pass


class ConfFilePerLineFormatException(ConfFileIllegalException):
    def __init__(self, mode, expect_num, actual_num):
        super().__init__("in %s mode, expect %s items per line, but %s items are got.." % (mode, expect_num, actual_num))


class PhoneNumFormatException(PhoneNumException):
    def __init__(self, phonenum):
        super().__init__("the phonenum %s you input is illegal.." % phonenum)


class MsgSendFailedException(Exception):
    def __init__(self, phonenum):
        super().__init__("the msg send to %s is failed, means all api interfaces are invalid." % phonenum)


class MsgSendAPIException(Exception):
    pass
