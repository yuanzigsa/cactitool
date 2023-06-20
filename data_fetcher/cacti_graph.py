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

url1 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=12664&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url2 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5350&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url3 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url4 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url5 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url6 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url7 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url8 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url9 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url10 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"
url11 = "http://120.77.151.18/cacti/graph_image.php?local_graph_id=5385&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1687166825&graph_end=1687253225"

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