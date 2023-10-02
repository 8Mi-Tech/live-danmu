# live-danmu
部分代码来自[real-url](https://github.com/wbt5/real-url),<br>
该项已年久失修,所以我打算重新开源一版

:warning:`fork提醒: 请fork dev分支 主分支是稳定版推送`

### 使用方法
```shell
#安装前置方法
pip3 install -r requirements.txt

#启动方法
python3 main.py --urls <直播间地址1> <直播间地址2> ...
#理论无限个 只要是支持平台的
```

### 直播平台支持状态
状态标志 | :x: 不支持 | :o: 支持 | :question: 未知
| 平台 | 状态 | 备注 |
|- | - |- |
| [哔哩哔哩](https://live.bilibili.com) | :x: | 最近B站的改动很奇怪<br>就没搞懂他们在搞什么<br>可能 `bilibili.py` 这个得修复了<br>(在看 [bliveedm](https://github.com/xfgryujk/blivedm) 这个项目,别急) |
| [虎牙](https://huya.com) | :o: | 
| [斗鱼](https://douyu.com) | :o: | 
| [CC直播](https://cc.163.com) | :question: | 没直播间，自行测试 |
| [AcFun](https://live.acfun.cn/) | :question: | 没直播间，自行测试 |
| 其他平台 | :question: | 在项目的`danmaku`文件夹内查看是否支持<br>一般没有明确提及的都是未经测试的<br>(我自己没开通对应平台的直播间我咋测试哦) |

### 运行截图

连接了 B站 虎牙 斗鱼 且发送点歌弹幕执行效果<br>（点歌的列表在Spotify内部 使用的时候要注意一下）
![image](https://github.com/8Mi-Tech/live-danmu/assets/25455400/737dfbd8-0ee2-4cb9-bf8b-a0bcb1bb4c22)


### 彩蛋
或者说 接下来要分离的内容

一个配合Spotify客户端的模块<br>在`live-danmu`内是作为点歌的
```shell
#登录Spotify (不登录 咋控制播放器)
python3 spotify_tools.py
```
登录完成后 请在自己直播间测试 `点歌 xxx` 这个指令

知道我为啥要分离了吧，不分离的话就不兼容其他音乐软件（草）
<br>
<br>
#### 结尾相关
Copyright © 2017-Now 8Mi-Tech. All right reserved
