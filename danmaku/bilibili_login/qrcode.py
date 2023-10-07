import requests
import qrcode
import time
import json
import os

def get_bilibili_login_qrcode_data():
    url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
    response = requests.get(url)
    data = response.json()
    token = data['data']['qrcode_key']
    return token, data['data']['url']

def print_qrcode_to_terminal(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

def bilibili_monitor_qrcode_scan():
    token, url = get_bilibili_login_qrcode_data()
    print_qrcode_to_terminal(url)
    
    last_output = ""
    result_dict = {}
    while True:
        poll_url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'
        response = requests.get(poll_url, params={'qrcode_key': token})
        data = response.json()['data']

        code = data['code']
        message = data['message']
        cookie = None

        if code == 0:
            output = "登录成功"
            result_dict['URL'] = data['url']
            result_dict['refresh_token'] = data['refresh_token']
            result_dict['Timestamp'] = data['timestamp']
            result_dict['cookies'] = response.cookies.get_dict()
        elif code == 86090:
            output = "等待确认登录"
        elif code == 86101:
            output = ""
        else:
            output = f"Error code: {code}, Message: {message}"
            return output

        if output != last_output:
            print(output)
            last_output = output
        
        if code == 0:
        # 登录成功，将信息写入JSON文件
            with open('bili_session.json', 'w') as json_file:
                json.dump(result_dict, json_file)
            
            return result_dict
            break
        
        time.sleep(2)

    return None

def bilibili_login_event():
    def login():
        result = bilibili_monitor_qrcode_scan()
        if result:
            #print("登录成功")
            return result
        else:
            print("登录失败")
            return None

    if os.path.exists('bili_session.json'):
        try:
            with open('bili_session.json', 'r') as json_file:
                session_data = json.load(json_file)
                if 'refresh_token' in session_data and 'Timestamp' in session_data:
                    #print("存在有效的登录信息")
                    return session_data
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    print("执行重新登录")
    return login()

#result = monitor_qrcode_scan()
#print(result)  # 输出字典结果
