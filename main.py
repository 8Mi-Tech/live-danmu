# 部分弹幕功能代码来自项目：https://github.com/IsoaSFlus/danmaku，感谢大佬
# 快手弹幕代码来源及思路：https://github.com/py-wuhao/ks_barrage，感谢大佬
# 仅抓取用户弹幕，不包括入场提醒、礼物赠送等。

import asyncio
import danmaku
import sys
import argparse
import datetime
import subprocess
from spotify_tools import spotify_search
from spotify_tools import spotify_add_to_playlist

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser()
parser.add_argument('--urls', '-l', nargs='+', help='直播间地址列表')
args = parser.parse_args()

async def printer(q):
    while True:
        m = await q.get()
        if m['msg_type'] == 'danmaku':
            print("["+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+" | "+f'{m["platform"]}] {m["name"]}：{m["content"]}')
            if m["content"].startswith("点歌"):
                song_request = m["content"][2:].strip()
                spotify_add_to_playlist(spotify_search(song_request))

async def main(url):
    print("连接成功："+url)
    q = asyncio.Queue()
    dmc = danmaku.DanmakuClient(url, q)
    asyncio.create_task(printer(q))
    await dmc.start()

# 获取直播间地址列表
if args.urls:
    urls = args.urls
else:
    sys.exit("请提供直播间地址列表")

if __name__ == '__main__':
    # 创建多个 main 协程对象并同时运行它们
    loop = asyncio.get_event_loop()
    coroutines = [main(url) for url in urls]
    loop.run_until_complete(asyncio.gather(*coroutines))



# 虎牙直播：https://www.huya.com/11352915
# 斗鱼直播：https://www.douyu.com/85894
# B站直播：https://live.bilibili.com/70155
# 快手直播：https://live.kuaishou.com/u/jjworld126
# 火猫直播：
# 企鹅电竞：https://egame.qq.com/383204988
# 花椒直播：https://www.huajiao.com/l/303344861?qd=hu
# 映客直播：https://www.inke.cn/liveroom/index.html?uid=87493223&id=1593906372018299
# CC直播：https://cc.163.com/363936598/
# 酷狗直播：https://fanxing.kugou.com/1676290
# 战旗直播：
# 龙珠直播：http://star.longzhu.com/wsde135864219
# PPS奇秀直播：https://x.pps.tv/room/208337
# 搜狐千帆直播：https://qf.56.com/520208a
# 来疯直播：https://v.laifeng.com/656428
# LOOK直播：https://look.163.com/live?id=196257915
# AcFun直播：https://live.acfun.cn/live/23682490
# 艺气山直播：http://www.173.com/96
