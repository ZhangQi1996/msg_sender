from secret import func1, func2


def api_func1(phone, content, nickname='你好'):
    """实现api接口的调用"""
    func1(phone, content, nickname)


def api_func2(phone, content, nickname='你好'):
    func2(phone, content, nickname)


# 该数组列出左右可用的api接口供调用
API = [
    api_func1,
]