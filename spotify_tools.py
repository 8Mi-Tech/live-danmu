#!/bin/python3
import sys
import time
import json
import spotipy
#import webbrowser
from spotipy.oauth2 import SpotifyOAuth

def spotify_login():
    # 客户端 ID 和客户端密钥，替换为你自己的
    client_id = '44c3dded81f94b9eb820fcd1b095c866'
    client_secret = '06fb2f3e2f3b44bbbbc3def798f61db7'
    redirect_uri = 'http://127.0.0.1:8001'  # 指定本地Web服务器的地址和端口
    # 创建SpotifyOAuth对象，并设置open_browser参数为True
    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='user-read-playback-state user-modify-playback-state user-read-currently-playing', open_browser=True)
    if not sp_oauth.get_cached_token():
        sp_oauth.get_access_token()
    token_info = sp_oauth.get_cached_token()
    # 创建一个Spotify客户端对象
    if token_info and 'access_token' in token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        return sp  # 返回Spotify客户端对象
    else:
        print("无法获取访问令牌", file=sys.stderr)
        return None

def spotify_checklogin():
    # 检查令牌是否存在
    try:
        with open('.cache', 'r') as cache_file:
            token_info = json.load(cache_file)
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

def spotify_add_to_playlist(track_id):
    sp = spotify_checklogin()
    # 构建track的URI
    track_uri = f"spotify:track:{track_id}"
    # 将歌曲加入当前播放列表
    try:
        sp.add_to_queue(track_uri)
        print("[Spotify] 添加成功")
    except spotipy.SpotifyException as e:
        try:
            # 解析异常的JSON响应
            error_data = json.loads(e.response.content)
            # 提取错误信息
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
            print("[Spotify] 错误:", error_message)
        except json.JSONDecodeError:
            print("[Spotify] 我知道他发生了故障，但是错误都不给，嘤嘤嘤")


def spotify_search(query):
    sp = spotify_checklogin()
    # 发起带有访问令牌的搜索请求
    result = sp.search(q=query, type='track', limit=1)
    # 提取第一首歌曲的ID
    if 'tracks' in result and 'items' in result['tracks'] and len(result['tracks']['items']) > 0:
        track_id = result['tracks']['items'][0]['id']
        # 打印歌曲信息到标准错误流
        track_info = result['tracks']['items'][0]
        print(f"[Spotify] 搜索结果: {track_info['name']} - {', '.join([artist['name'] for artist in track_info['artists']])}, TrackID: {track_info['id']}", file=sys.stderr)
        return track_id
    else:
        print("No tracks found.", file=sys.stderr)

if __name__ == "__main__":
    sp = spotify_login()
    if sp:
        print("Spotify 登录成功")
        # 在这里可以使用sp_client来进行与Spotify API的操作
        # 例如，获取当前用户的播放状态等
        #playback_state = sp.current_playback()
        #print(playback_state)