from django.shortcuts import render,HttpResponse
import requests, re, time, os, shutil,time,datetime


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
        # "login_mobile": "",
        # "login_code": "",
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

name = "admin"
passwd = ""
ip = ""
head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

url1 = "http://212.64.77.78/cacti/graph_image.php?action=zoom&local_graph_id=17014&rra_id=0&view_type=tree&graph_start=1687140284&graph_end=1687226684&graph_height=120&graph_width=500&title_font_size=10"
url2 = "http://212.64.77.78/cacti/graph_image.php?action=zoom&local_graph_id=9357&rra_id=0&view_type=tree&graph_start=1687141003&graph_end=1687227403&graph_height=120&graph_width=500&title_font_size=10"
url3 = "http://212.64.77.78/cacti/graph_image.php?action=zoom&local_graph_id=9554&rra_id=0&view_type=tree&graph_start=1687141068&graph_end=1687227468&graph_height=120&graph_width=500&title_font_size=10"
session = requests.session()
login(ip=ip, head=head, name=name, passwd=passwd, session=session)

urls = [url1, url2, url3] #将需要下载的URL放在列表中
for i, url in enumerate(urls):
    f = open(f"./graph/{i}.png", "wb") #根据循环次数给图片命名
    request = session.get(url, headers=head)
    aw = request.content
    f.write(aw)
    f.close()
print("图片下载成功")