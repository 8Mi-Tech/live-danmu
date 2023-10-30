#!/bin/python3
import os
import sys
import time
import json
import spotipy
#import webbrowser
import requests
from spotipy.oauth2 import SpotifyOAuth

def spotify_login():
    # 客户端 ID 和客户端密钥，替换为你自己的
    client_id = '44c3dded81f94b9eb820fcd1b095c866'
    client_secret = '06fb2f3e2f3b44bbbbc3def798f61db7'
    redirect_uri = 'http://127.0.0.1:8001'  # 指定本地Web服务器的地址和端口
    # 创建SpotifyOAuth对象，并设置open_browser参数为True
    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='user-read-playback-state user-modify-playback-state user-read-currently-playing', open_browser=True, show_dialog=True)
    while True:
        try:
            if not sp_oauth.get_cached_token():
                sp_oauth.get_access_token()
            break
        except spotipy.oauth2.SpotifyOauthError as e:
            file_path = ".cache"  # 指定要删除的文件路径
            if os.path.exists(file_path):
                os.unlink(file_path)
    token_info = sp_oauth.get_cached_token()
    # 创建一个Spotify客户端对象
    if token_info and 'access_token' in token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        return sp  # 返回Spotify客户端对象
    else:
        print("无法获取访问令牌", file=sys.stderr)
        return None

def spotify_checklogin(onlyToken=False):
    # 检查令牌是否存在
    try:
        with open('.cache', 'r') as cache_file:
            token_info = json.load(cache_file)
        if onlyToken is True:
            return token_info['access_token']
    except FileNotFoundError:
        print(".cache file not found. Please login first.", file=sys.stderr)
    if 'access_token' in token_info and 'expires_at' in token_info:
        current_time = int(time.time())
        expires_at = token_info['expires_at']    
        # 如果令牌已过期，刷新登录状态
        if current_time >= expires_at:
            #print("Token has expired. Refreshing login...", file=sys.stderr)
            return spotify_login()
        # 否则，使用现有令牌创建Spotify客户端对象
        else:
            sp = spotipy.Spotify(auth=token_info['access_token'])
            #print("Login is Still", file=sys.stderr)
            return sp
    else:
        return spotify_login()

def spotify_add_to_playback(track_id):
    sp = spotify_checklogin()
    # 构建track的URI
    track_uri = f"spotify:track:{track_id}"
    # 将歌曲加入当前播放列表
    return sp.add_to_queue(track_uri)

def spotify_search(query):
    sp = spotify_checklogin()
    # 发起带有访问令牌的搜索请求
    result = sp.search(q=query, type='track', limit=1)
    # 提取第一首歌曲的ID
    if 'tracks' in result and 'items' in result['tracks'] and len(result['tracks']['items']) > 0:
        track_id = result['tracks']['items'][0]['id']
        # 打印歌曲信息到标准错误流
        track_info = result['tracks']['items'][0]
        print(f"添加歌曲: {track_info['name']} - {', '.join([artist['name'] for artist in track_info['artists']])}, TrackID: {track_info['id']}", file=sys.stderr)
        return track_id
    else:
        print("No tracks found.", file=sys.stderr)

def spotify_get_playback_list(loop=False,auto_clean_terminal=False,isjson=False):
    while True:
        sp = spotify_checklogin()
        current_track = sp.current_playback()
        json_data = json.loads(requests.get("https://api.spotify.com/v1/me/player/queue", headers={'Authorization': f'Bearer {spotify_checklogin(onlyToken=True)}'}).text)

        if auto_clean_terminal is True:
            clear_terminal()
        
        if current_track:
            track_name = current_track['item']['name']
            artist_names = [artist['name'] for artist in current_track['item']['artists']]
            print(f'当前播放曲目：{track_name} - {", ".join(artist_names)}')
            
            # 取接下来要播放的歌曲
            print('接下来的曲目(播放队列):')
            for index, item in enumerate(json_data['queue'], start=1):
                track_name = item['name']
                artist_names = [artist['name'] for artist in item['artists']]
                print(f'|- {track_name} - {", ".join(artist_names)}')
        else:
            print('没有当前播放曲目。')
        
        if loop:  # 这里的condition是你需要检测的条件
            time.sleep(1)
        else: 
            break

def clear_terminal():
    # 获取当前操作系统类型
    platform = sys.platform
    # 根据操作系统类型选择清空终端的命令
    if platform.startswith('linux') or platform == 'darwin':
        os.system('clear')  # 对于Linux和macOS
    elif platform == 'win32':
        os.system('cls')  # 对于Windows
    else:
        # 在其他操作系统上的默认处理方式
        pass

if __name__ == "__main__":
    sp = spotify_login()
    if sp:
        print("Spotify 登录成功")
        # 在这里可以使用sp_client来进行与Spotify API的操作
        # 例如，获取当前用户的播放状态等
        #playback_state = sp.current_playback()
        #print(playback_state)