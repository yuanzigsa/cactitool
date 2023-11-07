import requests
import re
import time
import os
import shutil
import locale
import datetime
import pytesseract
import cv2
import json
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

##############################################################
# author：yuanzi
# Date：Nov. 3th, 2023
# Version：2.1
##############################################################

# 在一切开始之前，确保你已经配置了当前程序目录的config.json配置文件
# 读取JSON配置文件
with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

# 读取cacti登录账户密码信息、图表信息
cacti_login_info = config['cacti_login_info']
cacti_graph_info = config['cacti_graph_info']

# 读取钉钉api的配置
dingtalk_api = config['dingtalk_api']
app_key = dingtalk_api['app_key']
app_secret = dingtalk_api['app_secret']
workbook_id = dingtalk_api['workbook_id']
operator_id = dingtalk_api['operator_id']
range_address = dingtalk_api['range_address']
webhook = dingtalk_api['webhook']

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
    if request1.status_code == 200:
        print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 登陆成功，正在下载......")
    else :
        print ("登陆失败，请检查程序中关于Cacti登陆信息的配置，或者本机是否能够正常访问到该Cacti服务器")

# 下载图片并存入队列
def download_img(url, headers):
    request = session.get(url, headers=head)
    aw = request.content
    return aw

# 读取图片并转换为灰度图像
def read_image(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

# 检测文本区域
def detect_text(image):
    edges = cv2.Canny(image, 100, 50)
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
        text_image = image[y:y + h, x:x + w]

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
        "msgtype": "markdown",
        "markdown": {
            "title": "节点流量统计",
            "text": message
        }
    }
    response = requests.post(webhook, json=data, headers=headers)
    if response.status_code == 200:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 钉钉消息发送成功")
    else:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 钉钉消息发送失败，正在重试...")
        # 重试发送钉钉消息
        retry_count = 10  # 设置重试次数
        for i in range(retry_count):
            response = requests.post(webhook, json=data, headers=headers)
            if response.status_code == 200:
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 钉钉消息发送成功")
                break
            else:
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 钉钉消息发送失败，正在重试...")
        else:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 重试发送钉钉消息失败")

# 获取access_token
def get_access_token(app_key, app_secret):
    url = f"https://oapi.dingtalk.com/gettoken?appkey={app_key}&appsecret={app_secret}"
    response = requests.get(url)
    data = response.json()
    if data['errcode'] == 0:
        return data['access_token']
    else:
        return None
    
# 保存 sheet_id 到 JSON 文件
def save_sheet_id(sheet_id):
    with open('config.json', 'r', encoding='utf-8') as file:
        data =  json.load(file)
        data["dingtalk_api"]["sheet_id"] = sheet_id
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# 主程序开始
head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

# 获取当前时间一天前和当前系统时间的Unix时间戳
now = int(time.time())
one_day_ago = now - 86400

# 定义URL模板
url_template = "http://120.77.151.18/cacti/graph_image.php?local_graph_id={graph_id}&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start={start_time}&graph_end={end_time}"
# 更新urls数组
urls = [url_template.format(graph_id=cacti_graph_info[key]['graph_id'], start_time=one_day_ago, end_time=now) for key in cacti_graph_info]

# 创建下载目录
current_directory = os.getcwd()  # 获取当前目录
directory_path = os.path.join(current_directory, "graph")  # 要创建的目录路径
if os.path.exists(directory_path):  # 检查目录是否存在
    pass
else:
    os.makedirs(directory_path)  # 使用os.makedirs()函数创建目录

# 登录下载
session = requests.session()
login(ip=cacti_login_info['ip'], head=head, name=cacti_login_info['username'], passwd=cacti_login_info['password'], session=session)

# 创建Queue对象
imgQueue = Queue()

# 对下载图片方法进行多线程处理
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_img, url, head) for url in urls]
    for i, future in enumerate(futures):
        try:
            result = future.result()  # 获取线程的返回结果
            imgQueue.put((i, result))  # 将返回的图片数据和序号存入Queue
        except Exception as e:
            print(f"下载过程中出错, 异常为{e}")

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 下载完成，开始写入文件......")

# 从队列中按顺序取出图片数据并写入文件
while not imgQueue.empty():
    i, img_data = imgQueue.get()
    with open(f"./graph/{i}.png", "wb") as f:
        # 根据取出的序号给图片命名
        f.write(img_data)

# 获取graph目录下的所有文件路径
image_dir = "./graph/"
image_paths = []

for filename in os.listdir(image_dir):
    if filename.endswith(".png"):
        image_path = os.path.join(image_dir, filename)
        image_paths.append(image_path)

# 对文件路径进行按数字顺序排序
image_paths = sorted(image_paths, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

max_values = get_max_values(image_paths)

if len(max_values) == len(image_paths):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 获取到的节点数据数量：" + str(len(max_values)) + "个，" + "详细信息如下：")
else:
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 获取到的max_values的值的数量小于下载图片的数量，等待一分钟后重新下载图片并识别图中的数据")
    time.sleep(60)
    # 重新下载图片并识别图中的数据
    while len(max_values) != len(image_paths):
        for i, url in enumerate(urls):
            # 根据循环次数给图片命名
            f = open(f"./graph/{i}.png", "wb")
            request = session.get(url, headers=head)
            aw = request.content
            f.write(aw)
            f.close()
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 图片重新下载成功!")

        # 重新测试结果输出
        max_values = get_max_values(image_paths)
        formatted_max_values = ["{:.2f}G".format(value) for value in max_values]

        # 判断max_values的值的数量是否与下载图片的数量一致
        if len(max_values) == len(image_paths):
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 获取到的节点数据数量：", len(max_values))
        else:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 重新下载图片后仍然无法获取到正确的节点数据数量")
            time.sleep(60)  # 如果不一致，等待60秒再试一次

formatted_max_values = ["{:.2f}G".format(value) for value in max_values]

# 提取阈值以供后面做判断
threshold_values = []

for key, value in cacti_graph_info.items():
    threshold = value['threshold']
    digits = ''.join(filter(str.isdigit, threshold))
    threshold_values.append(digits)
threshold_values = [float(value) for value in threshold_values]

# 每月2号对低于流量阈值数量统计字典进行归零
# 获取当前日期
today = datetime.date.today()
# 如果是每月的第一天（ps：不要问为什么下面是2，因为每月2号才会统计1号的数据呀）
if today.day == 2:
    # 归零操作
    for key in config["cacti_graph_info"]:
        config["cacti_graph_info"][key]["low_threshold_counts"] = 0
    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)    

# 获取前一天月份和日期并格式化
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
formatted_date = yesterday.strftime("%m月%d日").lstrip("0")

message_today = f"## 【{formatted_date}节点流量统计】\n\n"
message_today += " 节点名称 | 带宽/阈值 | 当日流量最大值 \n"

for index, (image_path, max_value, threshold_value) in enumerate(zip(image_paths, max_values, threshold_values), start=1):
    message_today += "- {} | {}/{} | **{}G**\n".format(cacti_graph_info[f'{index}']['name'], cacti_graph_info[f'{index}']['bandwidth'], cacti_graph_info[f'{index}']['threshold'], max_value)

message_warning = "## 【流量低于报警值】\n\n"
message_warning += " 节点名称 | 本月累计出现 \n"
for index, (image_path, max_value, threshold_value) in enumerate(zip(image_paths, max_values, threshold_values), start=1):
    if max_value < threshold_value:
        graph_info = cacti_graph_info[f'{index}']
        node_name = graph_info['name']
        config["cacti_graph_info"][f'{index}']["low_threshold_counts"] += 1
        with open('config.json', 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)  
        count = cacti_graph_info[f'{index}']["low_threshold_counts"]
        message_warning += "- {} | {}天\n".format(node_name, count)
message_combined = message_today + "\n" + message_warning
print(message_combined)

# 发送钉钉消息
send_dingtalk_message(webhook, message_combined)

# 删除所有图形文件
for filename in os.listdir(image_dir):
    file_path = os.path.join(image_dir, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 流量图缓存已清理")

# 获取到动态的access_token
access_token = get_access_token(app_key, app_secret)
# 尝试加载 sheet_id
sheet_id = dingtalk_api['sheet_id']

# 获取当前日期并判断今天是否是1月、4月、7月或者10月的2号
current_date = datetime.datetime.now().date()
if current_date.day == 2 and current_date.month in [1, 4, 7, 10]:
    if current_date.month in [1, 2, 3]:
        sheetname = f"{current_date.year}年1月-3月"
    elif current_date.month in [4, 5, 6]:
        sheetname = f"{current_date.year}年4月-6月"
    elif current_date.month in [7, 8, 9]:
        sheetname = f"{current_date.year}年7月-9月"
    elif current_date.month in [10, 11, 12]:
        sheetname = f"{current_date.year}年10月-12月"

    # 构建请求头和请求数据并发送post请求
    headers = {
        'Host': 'api.dingtalk.com',
        'x-acs-dingtalk-access-token': f'{access_token}',
        'Content-Type': 'application/json',
    }
    data = {
        "name": f"{sheetname}",
        "visibility" : "visible"
    }
    url = f'https://api.dingtalk.com/v1.0/doc/workbooks/{workbook_id}/sheets?operatorId={operator_id}'
    response = requests.post(url, json=data, headers=headers)
    # 提取id对应的值
    response_data = response.json()
    sheet_id = response_data['id']

    # 保存新的sheetid到配置文件
    save_sheet_id(sheet_id)

# 获取钉钉在线表格信息
params = {'operatorId': 'dOaiiROp6uNPr67AjoWJFngiEiE'}
headers = {
    'x-acs-dingtalk-access-token': f'{access_token}',
    'Content-Type': 'application/json'
}
url = f'https://api.dingtalk.com/v1.0/doc/workbooks/{workbook_id}/sheets/{sheet_id}/ranges/{range_address}?select=values'
response = requests.get(url, params=params, headers=headers)
data = json.loads(response.text)
if response.status_code == 200:
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 已成功获取到钉钉在线文档的表格信息，正在进行数据处理和推送......")
else:
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 获取钉钉在线文档信息出错，请检查sheet_id.json文件是否存在并且已经包含了合法的表格id")

# 确定编辑的起始位置
data = json.loads(response.text)

def find_first_empty_row(values):
    for i in range(len(values) - 1):
        if all(cell == "" for cell in values[i]) and all(cell == "" for cell in values[i + 1]):
            return i + 2
    return None

start_address = find_first_empty_row(data["values"])

# 格式化请求数据并进行推送
data = {
    "values": [[f"{formatted_date}", "", "", ""], 
               ["节点", "接入带宽/报警值", "18-24点流量最大值", "是否低于报警值"]],
    "backgroundColors": [["white", "white", "white", "white"],
                        ["00B14D", "00B14D", "00B14D", "00B14D"]]
}

# 遍历图像信息并追加到请求体
for index, (image_path, max_value, threshold_value) in enumerate(zip(image_paths, max_values, threshold_values), start=1):
    graph_name = cacti_graph_info[f'{index}']['name']
    bandwidth = cacti_graph_info[f'{index}']['bandwidth']
    threshold = cacti_graph_info[f'{index}']['threshold']
    is_below_threshold = "是" if max_value < threshold_value else ""
    background_color = ["white", "white", "white", "white"] if is_below_threshold == "" else ["yellow", "yellow", "yellow", "yellow"]
    # 追加到请求体数据
    data["values"].append([graph_name, f"{bandwidth}/{threshold}", f"{max_value}G", is_below_threshold])
    data["backgroundColors"].append(background_color)

# 确定所需编辑区域的大小
values_list = data["values"]
num_rows = len(values_list)
end_address = start_address + num_rows - 1
range_address = f"A{start_address}:D{end_address}"

# 构建请求头
headers = {
    "Host": "api.dingtalk.com",
    "x-acs-dingtalk-access-token": access_token,
    "Content-Type": "application/json"
}

# 构建请求URL
url = f"https://api.dingtalk.com/v1.0/doc/workbooks/{workbook_id}/sheets/{sheet_id}/ranges/{range_address}?operatorId={operator_id}"
# 发送PUT请求
response = requests.put(url, headers=headers, data=json.dumps(data))

# 检查响应状态码
if response.status_code == 200:
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 已成功将数据同步更新到钉钉在线文档")
else:
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " 更新钉钉在线文档出错，请检查api密钥是否失效")
