### msg sender
* 一个信息发送的小程序
* 提供抽象类
* 支持拓展高可用的接口
#### MsgSenderBase抽象类
1. 必须重写函数如下
    1. msg_content_generate
    2. send_msg
    3. run
#### MyMsgSender实现的功能
1. 支持多人发送,每人的信息发送都由单一线程处理
2. 支持程序异常获取，发送邮件通知
     