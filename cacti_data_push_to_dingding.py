import requests
import re
import time
import os
import shutil
import locale
import datetime
import pytesseract
import cv2
from django.shortcuts import render, HttpResponse

# 登录
def login(ip, head, name, passwd, session):
    url = "http://" + ip + "/cacti/index.php"
    # 获取csrf值
    res1 = session.get(url, headers=head).text
    c_token = re.findall('var csrfMagicToken = "(.*?)";', res1)[0]
    data = {
        "__csrf_magic": c_token,
        "action": "login",
        "login_username": name,
        "login_password": passwd,
    }

    # 登录成功返回200
    request1 = session.post(url=url, data=data, headers=head)
    statu = request1.status_code
    print(statu)
    if statu == 200:
        return 1
        print("yes")
    else:
        return 0
        print("NO")

# 识别图片中的数据

# 读取图片并转换为灰度图像
def read_image(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

# 检测文本区域
def detect_text(image):
    edges = cv2.Canny(image, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    text_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 100 and h > 10:
            text_regions.append((x, y, w, h))

    return text_regions

# 提取Max:后的数据
def extract_max_value(image, text_regions):
    max_values = []
    for region in text_regions:
        x, y, w, h = region
        text_image = image[y:y+h, x:x+w]

        text = pytesseract.image_to_string(text_image, lang='chi_sim+eng')
        matches = re.findall(r'Max:\s*([\d.]+)', text)
        if matches:
            max_values.extend([float(match) for match in matches])

    return max_values

# 返回每张图片中的最大值
def get_max_values(image_paths):
    max_values = []
    for image_path in image_paths:
        image = read_image(image_path)
        text_regions = detect_text(image)
        max_values_in_image = extract_max_value(image, text_regions)
        if max_values_in_image:
            max_value = max(max_values_in_image)
            max_values.append(max_value)

    return max_values

# 发送钉钉消息
def send_dingtalk_message(webhook, message):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    response = requests.post(webhook, json=data, headers=headers)
    if response.status_code != 200:
        print("Failed to send message to DingTalk:", response.text)

# 主程序开始
name = ""
passwd = ""
ip = ""
head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

# 获取当前时间一天前和当前系统时间的Unix时间戳
now = int(time.time())
one_day_ago = now - 86400

# 设置11个图的url，并替换11个url连接中的start和end参数值为当前时间一天前和当前系统时间的Unix时间戳
url1 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=12664&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url2 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=5350&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url3 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url4 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=5306&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url5 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=3228&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url6 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=15207&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url7 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=16091&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url8 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=16093&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url9 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=16092&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url10 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=14365&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"
url11 = f"http://120.77.151.18/cacti/graph_image.php?local_graph_id=14364&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={one_day_ago}&graph_end={now}"

# 创建下载目录
current_directory = os.getcwd()  # 获取当前目录
directory_path = os.path.join(current_directory, "graph")  # 要创建的目录路径
if os.path.exists(directory_path):  # 检查目录是否存在
    pass
else:
    os.makedirs(directory_path)  # 使用os.makedirs()函数创建目录

# 登录下载
session = requests.session()
login(ip=ip, head=head, name=name, passwd=passwd, session=session)
print("登陆成功，正在下载......")

urls = [url1, url2, url3, url4, url5, url6, url7, url8, url9, url10, url11] #将需要下载的URL放在列表中
for i, url in enumerate(urls):
    f = open(f"./graph/{i}.png", "wb") #根据循环次数给图片命名
    request = session.get(url, headers=head)
    aw = request.content
    f.write(aw)
    f.close()
print("图片下载成功!")

# 测试结果输出
image_paths = ['./graph/0.png', './graph/1.png', './graph/2.png', './graph/3.png','./graph/4.png','./graph/5.png','./graph/6.png','./graph/7.png','./graph/8.png', './graph/9.png', './graph/10.png']

max_values = get_max_values(image_paths)
formatted_max_values = ["{:.2f}G".format(value) for value in max_values]

# 创建一个字典，记录每个图的名称和带宽
##############################################################
image_info = {
    '0.png': {'name': '天水电信', 'value': 100},
    '1.png': {'name': '惠州移动', 'value': 100},
    '2.png': {'name': '武汉铁通', 'value': 40},
    '3.png': {'name': '济宁移动', 'value': 40},
    '4.png': {'name': '武汉移动', 'value': 60},
    '5.png': {'name': '荆州联通', 'value': 100},
    '6.png': {'name': '合肥电信（三线）', 'value': 140},
    '7.png': {'name': '合肥移动（三线）', 'value': 100},
    '8.png': {'name': '合肥联通（三线）', 'value': 100},
    '9.png': {'name': '武汉联通（三线）', 'value': 5.33},
    '10.png': {'name': '武汉移动（三线）', 'value': 16},
}
##############################################################

# 获取前一天月份和日期并格式化
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
formatted_date = yesterday.strftime("%m月%d日").lstrip("0")

message_today = f"【{formatted_date}节点流量统计】\n"
message_warning = "【流量低于报警值】\n"

for image_path, max_value in zip(image_paths, formatted_max_values):
    image_name = image_path.split('/')[-1]
    message_today += "{} {}\n".format(image_info[image_name]['name'], max_value)

for image_path, max_value in zip(image_paths, max_values):
    image_name = image_path.split('/')[-1]
    if max_value < image_info[image_name]['value'] * 0.75:
        message_warning += "{}\n".format(image_info[image_name]['name'])

# 发送钉钉消息
# webhook = "https://oapi.dingtalk.com/robot/send?access_token=b7921f1a760c42966ecb18a4c11dfa89456dbc7bea164f75acd9b9f83d1e6b2f"  # 替换为您的钉钉机器人Webhook地址
# send_dingtalk_message(webhook, message_today)
# send_dingtalk_message(webhook, message_warning)

print(message_today)
print(message_warning)