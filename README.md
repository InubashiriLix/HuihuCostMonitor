# HuihuCostMonitor

## Intro

- newest: 支持断网重连！！！不用担心断网了！
- 一个简单的Python脚本，用于监控慧湖通水电费消费情况，以及在定时点钟将水电费情况发送到设置的邮箱账号上
- 目前发送邮箱只支持163邮箱
- 目前仅仅在作者的机子上试验过，
- 支持文缘，文星，文荟，文萃
- 个人推荐在宿舍部署一个linux主机，用于监控水电费消费情况，

## Dependencies

- python3.8 +
- pip install
    1. socket
    2. requests
    3. dotenv

## Installation

1. 设置.env, 模版可以在主目录下的".env_model"找到

```env
# get stoken # WARNING: REQUIRED
# 先登录慧湖通，打开开发者工具，刷新页面，找到OPEN_ID 需要wechat 开发者版？(没试过)
# 我直接使用reqable软件抓包了
OPEN_ID="fetch it by your self"

# email 设置部分
SENDER_EMAIL=yourEmail@163.com # 163 only
SENDER_PASSWORD=yourEmailPassword # 163 only
RECV_EMAIL=yourDescEmail@whatever.com

USE_EMAIL=TRUE
UPDATE_INTERVAL_HOUR=4
SENDING_HOUR=8
SENDING_MIN=30

# 断网重连设置部分
USE_AUTO_NET_LOGIN=TRUE
USERNAME_DORM_NET="12332112332"
PASSWORD_DORM_NET="123321"
TELE_COMP_SHORT="telecom"
# cmcc for 中国移动
# telecom for 中国电信
# unicom for 中国联通
CHECK_INTERVAL=15
USE_LOW_COST_STRATEGY=FALSE

# WARNING: rename this as .env after all setted
```

2. 设置完成以后将模版重命名为".env"

3. main.py 文件是入口

4. 如何设置开机自启（linux）直接gpt问去

5. 什么是USE_LOW_COST_STRATEGY：

- 因为每次连上网以后有一段时间不会断网（至少大于5小时）如果启动low cost 模式，则可以在5小时内省去检测网络通断的开支

## TODO

1. 找别人测试
2. linux / windows 一键自启脚本
3. 支持更多邮箱
4. 有时候真的觉得编程就图一乐呵，反正也没人看这个readme，那我随便说了。世界就是如此荒谬，不可理解，什么都干了，什么都做了，得不到赏识，我不懂为何我要努力，我不懂为何我要伤心，罪也受了，也思考了，但是仍然不能理解。世界如此荒谬，不妨我也过得荒谬一些，好让自己过的好点。
5. 真的变坏一点吧，孩子啊。

