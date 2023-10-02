#!/bin/python3
import os
import sys
import time
import configparser
from spotify_tools import spotify_checklogin

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

sp = spotify_checklogin()
folder_path = 'spotify_getnow'
# 定义配置文件的名称变量
config_file_name = 'spotify_getnow/config.ini'
# 定义输出文件的名称
output_file_name = 'spotify_getnow/output.txt'

# 判断文件夹是否存在
if not os.path.exists(folder_path):
    # 如果文件夹不存在，则创建它
    os.makedirs(folder_path)
    print(f"文件夹 '{folder_path}' 创建成功！")

# 定义 spotify_output_file 函数
def spotify_output_file(filename, filecontent):
    with open(filename, 'w') as output_file:
        output_file.write(filecontent + "\n")
# 如果配置文件不存在，则创建一个默认配置文件
if not os.path.exists(config_file_name):
    config = configparser.ConfigParser()
    config['output'] = {'output-format': '正在播放: {track_name} - {track_artist_names}'}
    with open(config_file_name, 'w') as configfile:
        config.write(configfile)
# 创建一个配置解析器对象并读取配置文件
config = configparser.ConfigParser()
config.read(config_file_name)

while True:
    try:
        current_track = sp.current_playback()
        if current_track is not None and current_track['is_playing']:
            track_name = current_track['item']['name']
            artists = [artist['name'] for artist in current_track['item']['artists']]
            artist_names = ', '.join(artists)
            output_format = config.get('output', 'output-format')
            output_text = output_format.format(track_name=track_name, track_artist_names=artist_names)
            clear_terminal()
            print(output_text)
            spotify_output_file(output_file_name, output_text)
        else:
            clear_terminal()
            print("Spotify当前没有播放歌曲。")
        time.sleep(1)
    except Exception as e:
        try:
            error_data = json.loads(e.response.content)
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"错误信息: {error_message}")
        except json.JSONDecodeError:
            print("无法解析 JSON 响应")
        print("重新登录 Spotify...")
        sp = spotify_checklogin()