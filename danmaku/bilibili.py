import json
import random
from struct import pack, unpack
import aiohttp
import zlib
from .bilibili_login.qrcode import bilibili_login_event

async def get_danmu_info(ID):
    url = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo'
    params = {'id': ID, 'type': 0}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                response_data = await response.json()
                data = response_data.get('data', {})
                if data:
                    token = data['token']
                    host_list = data.get('host_list', [])
                    if host_list:
                        host = host_list[0].get('host', None)
                        port = host_list[0].get('wss_port', None)
                        if host:
                            result = {'token': token, 'url': f'{host}:{port}'}
                            return result
            else:
                print(response.status)
    return {'token': '', 'url': 'broadcastlv.chat.bilibili.com'}

class Bilibili:
    #wss_url = 'wss://broadcastlv.chat.bilibili.com/sub'
    heartbeat = b'\x00\x00\x00\x1f\x00\x10\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x5b\x6f\x62\x6a\x65\x63\x74\x20' \
                b'\x4f\x62\x6a\x65\x63\x74\x5d '
    heartbeatInterval = 60

    @staticmethod
    async def get_ws_info(url):
        danmu_info = await get_danmu_info(url.split('/')[-1])
        wss_url = 'wss://' + danmu_info['url'] + '/sub'
        url = 'https://api.live.bilibili.com/room/v1/Room/room_init?id=' + url.split('/')[-1]

        data = {
            'roomid': None,
            'uid': None,
            'protover': 3,
            'platform': 'web',
            'type': 2,
            'key': None,
            'buvid': None,
        }

        async with aiohttp.ClientSession(cookies=bilibili_login_event()['cookies']) as session:
            async with session.get('https://data.bilibili.com/v') as resp:
                if resp.status == 200:
                    buvid_cookie = resp.cookies.get('buvid3', None)
                    if buvid_cookie is not None:
                        data['buvid']=buvid_cookie.value

        async with aiohttp.ClientSession(cookies=bilibili_login_event()['cookies']) as session:
            async with session.get(url) as resp:
                room_json = json.loads(await resp.text())
                room_id = room_json['data']['room_id']
                data['roomid'] = room_id
                data['uid'] = int(1e14 + 2e14 * random.random())
                data['key'] = danmu_info['token'] if danmu_info['token'] is not None else data['key']

                data_json = json.dumps(data, separators=(',', ':'))
                data_bytes = data_json.encode('ascii')
                data_length = len(data_bytes) + 16
                data_packet = pack('>i', data_length) + b'\x00\x10\x00\x01' + pack('>i', 7) + pack('>i', 1) + data_bytes
                reg_datas = [data_packet]

        #print(reg_datas)
        return wss_url, reg_datas

    @staticmethod
    def decode_msg(data):
        dm_list_compressed = []
        dm_list = []
        ops = []
        msgs = []
        while True:
            try:
                packetLen, headerLen, ver, op, seq = unpack('!IHHII', data[0:16])
            except Exception as e:
                break
            if len(data) < packetLen:
                break
            if ver == 1 or ver == 0:
                ops.append(op)
                dm_list.append(data[16:packetLen])
            elif ver == 2:
                dm_list_compressed.append(data[16:packetLen])
            if len(data) == packetLen:
                data = b''
                break
            else:
                data = data[packetLen:]

        for dm in dm_list_compressed:
            d = zlib.decompress(dm)
            while True:
                try:
                    packetLen, headerLen, ver, op, seq = unpack('!IHHII', d[0:16])
                except Exception as e:
                    break
                if len(d) < packetLen:
                    break
                ops.append(op)
                dm_list.append(d[16:packetLen])
                if len(d) == packetLen:
                    d = b''
                    break
                else:
                    d = d[packetLen:]

        for i, d in enumerate(dm_list):
            try:
                msg = {}
                if ops[i] == 5:
                    j = json.loads(d)
                    msg['msg_type'] = {
                        'SEND_GIFT': 'gift',
                        'DANMU_MSG': 'danmaku',
                        'WELCOME': 'enter',
                        'NOTICE_MSG': 'broadcast',
                        'LIVE_INTERACTIVE_GAME': 'interactive_danmaku'  # 新增互动弹幕，经测试与弹幕内容一致
                    }.get(j.get('cmd'), 'other')

                    # 2021-06-03 bilibili 字段更新, 形如 DANMU_MSG:4:0:2:2:2:0
                    if msg.get('msg_type', 'UNKNOWN').startswith('DANMU_MSG'):
                        msg['msg_type'] = 'danmaku'

                    if msg['msg_type'] == 'danmaku':
                        msg['name'] = (j.get('info', ['', '', ['', '']])[2][1]
                                       or j.get('data', {}).get('uname', ''))
                        msg['content'] = j.get('info', ['', ''])[1]
                    elif msg['msg_type'] == 'interactive_danmaku':
                        msg['name'] = j.get('data', {}).get('uname', '')
                        msg['content'] = j.get('data', {}).get('msg', '')
                    elif msg['msg_type'] == 'broadcast':
                        msg['type'] = j.get('msg_type', 0)
                        msg['roomid'] = j.get('real_roomid', 0)
                        msg['content'] = j.get('msg_common', 'none')
                        msg['raw'] = j
                    else:
                        msg['content'] = j
                else:
                    msg = {'name': '', 'content': d, 'msg_type': 'other'}
                #结尾签名平台名称
                msg['platform'] = '哔哩哔哩'
                msgs.append(msg)
            except Exception as e:
                pass

        return msgs
