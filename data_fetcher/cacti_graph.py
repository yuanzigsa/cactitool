from django.shortcuts import render, HttpResponse
import requests, re, time, os, shutil, time, datetime

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

name = ""
passwd = ""
ip = ""
head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

# 获取当前时间一天前和当前系统时间的Unix时间戳
now = int(time.time())
one_day_ago = now - 86400

# 替换11个url连接中的start和end参数值为当前时间一天前和当前系统时间的Unix时间戳
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
