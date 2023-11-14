# Cacti流量统计程序v2.1-使用说明


# 一、简介

​		这个Python脚本程序主要通过图文识别的方式将cacti系统中特定流量图的值进行统计，并将结果通过钉钉机器人发送到钉钉群进行提醒，同时会自动同步数据到钉钉在线文档。

​		该程序使用了程序+数据分离的方式，主程序为`cacti_data_push_to_dingtalk.py`，节点信息、cacti登录信息和钉钉api的数据配置存储在`config.json`中用于程序的调用。

![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/44efaa6a-2c1c-4df1-b0f1-1360d3a3ea4c)

## 1.1 主程序（cacti_data_push_to_dingtalk）

​		在主程序中，定义了cacti登录、图片下载读取、数据处理以及钉钉api的一些功能函数，程序登录Cacti并下载网络流量图表，然后读取和处理这些图片以获取流量的最大值，最后将统计结果发送到钉钉，具体说明如下：

- **读取json配置**：从`config.json`文件中读取一些持久化数据配置信息，用于程序的登录和数据记录操作，在下面的配置文件介绍会详细说明。
- **登录Cacti**：使用`login`函数登录Cacti，一个用于网络流量监控的工具。
- **读取和处理图片**：使用`read_image`、`detect_text`和`extract_max_value`函数读取下载的图片，将其转换为灰度图像，检测文本区域，并提取出流量的最大值。
- **下载图片**：使用`download_img`函数下载Cacti生成的网络流量图表。
- **获取最大值**：使用`get_max_values`函数获取每张图片中的最大值。
- **构建钉钉消息体**：按照预期的汇报格式一一填充数据将其构建成一个完整的markdown格式消息。
- **发送钉钉消息**：使用`send_dingtalk_message`函数将网络流量的统计结果发送到钉钉。
- **构建钉钉文档请求体：**格式化请求数据，并将低于阈值的数据整行标注成黄色。
- **推送到钉钉文档：**根据请求体确定好所需编辑区域及空行起始位置并开始进行推送，如果是新一季度就开始创建新的sheet。

​		除此之外，这个脚本还提供了一些诸如数据校验，环境检测的功能。当然，实现以上所有功能不可避免的需要依赖一些外部库，如`requests`、`re`、`cv2`、`pytesseract`等，用于网络请求、正则表达式匹配、图像处理和图像中的文本提取等操作。

## 1.2 配置文件（config.json）

​		主程序的顺利执行必须能够调用的配置文件`config.json`中的配置信息，这主要包括了如下信息：

- **Cacti登录信息**

  - IP地址：这是Cacti应用程序的服务器IP地址，用于访问和管理Cacti系统。

  - 用户名和密码：这是用于登录Cacti应用程序的凭据。

- **钉钉API信息**

  - Webhook：这是DingTalk机器人的Webhook地址，用于发送通知和消息到DingTalk群。

  - App Key和App Secret：这是DingTalk API的应用程序密钥和密钥，用于访问和授权钉钉文档。

  - Workbook ID：这是钉钉文档工作区的ID，用于在工作表中进行数据操作和管理。

  - Operator ID：这是钉钉文档操作员的ID，用于标识执行操作的用户。

  - Range Address：这是钉钉文档工作表中的范围地址，指定了要操作的单元格范围。

  - Sheet ID：这是钉钉文档工作表的ID，用于在工作表中进行数据操作和管理。

- **Cacti图表信息**
  - 图表1至图表9：这些图表包含了不同网络设备或服务的监控数据。
    - 名称：这是图表的名称，用于标识不同的监控对象。
    - 带宽：这是监控节点的带宽容量。
    - 阈值：这是设定的阈值，用于判断是否超过了预设的限制。
    - 图表ID：这是图表在Cacti系统中的唯一标识符。
    - 低阈值计数：这是记录月低于阈值的次数。

​		关于`config.json`中所有数据具体如何获取，在后面第三章会有介绍。

## 1.3 将主程序和配置文件上传至服务器

1. 给服务器安装lrzsz

   ```shell
   yum install lrzsz
   ```

2. 将主程序和配置文件上传至服务器

   ```shell
   rz
   ```

   然后分别选择主程序和配置文件等待上传完成即可

# 二、程序部署（CentOS）

## 2.1 安装python环境

#### 2.1.1 更新系统软件包

```shell
sudo yum update
```

#### 2.1.2 安装Python开发工具包

```bash
sudo yum groupinstall "Development Tools"
```

#### 2.1.3 安装依赖库

```bash
sudo yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel libffi-devel
```

#### 2.1.4 下载Python源代码

```bash
wget <https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz>
```

#### 2.1.5 解压源代码

```bash
tar -xf Python-3.9.7.tgz
```

#### 2.1.6 进入源代码目录

```bash
cd Python-3.9.7
```

#### 2.1.7 配置编译选项

```bash
./configure 
```

#### 2.1.8 编译并安装Python

```bash
make && sudo make install
```

#### 2.1.9 验证安装

```bash
python3.9 --version
```

## 2.3 使用pip安装所需外部库

- requests：用于发送HTTP请求和处理响应。

  ```bash
  pip3.9 install requests
  ```

- pytesseract：用于OCR（光学字符识别）。

  ```bash
  pip3.9 install pytesseract
  ```

- 安装opencv-python库的依赖项：

  ```bash
  sudo yum install -y numpy
  ```


- cv2：用于图像处理和计算机视觉。

  ```bash
  pip3.9 install opencv-python
  ```

- 下载对应版本的urllib3

  ```shell
  pip3.9 install urllib3==1.26.6
  ```

## 2.3 Centos系统下安装Tesseract

#### 2.3.1 安装Leptonica

1. 打开终端并执行以下命令，使用 wget 下载 Leptonica 的源代码压缩包：

   ```bash
   wget <https://github.com/DanBloomberg/leptonica/releases/download/1.80.0/leptonica-1.80.0.tar.gz>
   ```
   
2. 下载完成后，解压压缩包：

   ```bash
   tar -xzvf leptonica-1.80.0.tar.gz
   ```
   
3. 进入解压后的目录：

   ```bash
   cd leptonica-1.80.0
   ```
   
4. 接下来，执行以下命令编译和安装 Leptonica：

   ```bash
   ./configure
   make
   sudo make install
   ```
   
   这将会编译源代码并将 Leptonica 安装到你的系统中。
   
5. 当安装完成后，需要配置环境变量。编辑 `~/.bashrc` 文件：

   ```bash
   vi ~/.bashrc
   ```
   
6. 在文件的末尾添加以下行：

   ```bash
   export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
   ```
   
   这将告诉系统在编译时在 `/usr/local/lib/pkgconfig` 目录中查找 Leptonica。
   
7. 保存并关闭文件。然后执行以下命令使修改生效：

   ```bash
   source ~/.bashrc
   ```
   

环境变量将被加载到当前终端会话中，到此为止已经成功安装了 Leptonica 并配置了

#### 2.3.2 安装gcc-8

1. 使用yum安装gcc

   ```bash
   yum install -y centos-release-scl
   yum install devtoolset-8-gcc*
   ```

2. 当默认gcc环境设置当前安装的版本

   ```bash
   scl enable devtoolset-8 bash
   ```

#### 2.3.2 安装tesseract

1. 下载tesseract-ocr 5.3.1的源码

   ```bash
   wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.3.1.tar.gz
   ```

2. 配置编译并安装tesseract，一条执行完再执行下一条

   ```bash
   ./autogen.sh 
   ./configure 
   make&make install 
   ldconfig
   ```

#### 2.3.3 添加Tessdata训练数据

1. 去https://github.com/tesseract-ocr/tessdata下载Tesssdata训练数据，如下载较慢可以网上搜索通过其他渠道下载

   ![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/91abd832-d440-4d50-96c3-a4d3d1d05180)


2. 将下载的数据文件放置在正确的目录中。使用以下命令将数据文件从下载位置 (`DOWNLOAD_PATH`) 移动到 `/usr/local/share/tessdata/` 目录：

   ```bash
   mv DOWNLOAD_PATH/chi_sim.traineddata /usr/local/share/tessdata/
   ```

​		请确保替换 `DOWNLOAD_PATH` 为下载数据文件所在的实际路径

3. 最后，在终端中设置 `TESSDATA_PREFIX` 环境变量，指向包含语言数据文件的目录,可以使用以下命令设置环境变量：

   ```bash
   export TESSDATA_PREFIX=/usr/local/share/tessdata/
   ```

4. 永久配置环境变量。编辑 `~/.bashrc` 文件：

   ```bash
   vi ~/.bashrc
   ```

5. 在文件的末尾添加以下行：

   ```bash
   export TESSDATA_PREFIX=/usr/local/share/tessdata/
   ```

6. 保存并关闭文件。然后执行以下命令使修改生效：

   ```bash
   source ~/.bashrc
   ```

## 2.4 创建定时执行程序计划

#### 2.4.1 打开终端并输入以下命令以编辑Cron表

```bash
crontab -e
```

#### 2.4.2 在编辑器中，添加以下行来设置Cron任务

文件头添加以下内容：

```bash
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOME=/root
```

文件尾部添加以下内容：

```bash
0 0 * * * python3.9 /path/to/cacti_data_push_to_dingtalk.py
```

- 这将在每天的0点（午夜）执行`cacti_data_push_to_dingtalk.py`脚本

- 请将`/path/to/cacti_data_push_to_dingtalk.py`替换为实际脚本的路径

#### 2.4.3 保存退出并给脚本添加可执行权限

- 按ESC后输入`:wq!`
- 给脚本赋予可执行权限`Chmod +x /path/to/cacti_data_push_to_dingtalk.py`

# 三、后期维护与数据更新

## 3.1 一般流程

1. 找到cacti_data_push_to_dingtalk.py这个python脚本的工作目录，使用vim编辑器进行编辑

   `vi config.json`

2. 在打开的代码中修改基础数据维护部分的数据，具体说明见3.2

3. 修改完成后按ESC后输入`:wq!`保存退出即可

## 3.2 配置文件（config.json）

​		在config.json这个配置文件存储了主程序顺利运行所需要的配置数据，主要包含了cacti_login_info、dingtalk_api和cacti_graph_info这三块内容，具体内容如下：

```python
{
    "cacti_login_info": {
        "ip": "123.123.123.123",
        "username": "admin",
        "password": "admin"
    },
    "dingtalk_api": {
        "webhook": "https://oapi.dingtalk.com/robot/send?access_token=345678",
        "app_key": "ertyuqwwFDFG",
        "app_secret": "ZZpQ7KfQunygd8eNw5LG89vBsdiFxflwLISk",
        "workbook_id": "1GXn4X9xePp4",
        "operator_id": "dOaiiROp6uNP",
        "range_address": "A1:D5000",
        "sheet_id": "st-3276e9bf-894213"
    },
    "cacti_graph_info": {
        "1": {
            "name": "武汉电信",
            "bandwidth": "100G",
            "threshold": "75G",
            "graph_id": 2664,
            "low_threshold_counts": 1
        },
        "2": {
            "name": "武汉移动",
            "bandwidth": "100G",
            "threshold": "75G",
            "graph_id": 5350,
            "low_threshold_counts": 0
        },
        "3": {
            "name": "武汉铁通",
            "bandwidth": "40G",
            "threshold": "30G",
            "graph_id": 5385,
            "low_threshold_counts": 1
        },
        "4": {
            "name": "武汉联通",
            "bandwidth": "20G",
            "threshold": "15G",
            "graph_id": 5306,
            "low_threshold_counts": 0
        }
    }
}
```

- **cacti_login_info**

  这个里面存储了cacti登录所需信息，无需过多介绍

- **dingtalk_api**

  - webhook：钉钉机器人webhook地址的获取见第四章

  - app_key和app_secret：钉钉开放平台后台，找到“应用信息”

    ![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/bf7978f6-df7e-4a39-b044-e8740708d94d)
  
  - workbook_id：打开钉钉文档，点击左上角“表格”，然后点击“文档信息”
  
    ![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/b728967b-ba6e-4d6b-bacd-e98f06daeb61)
  
  - operator_id：操作者id根据AppKey和AppSecret便可以获取到，示例代码如下：
  
    ```python
    import requests
    
    app_key = "Your_App_Key"
    app_secret = "Your_App_Secret"
    access_token_url = "https://oapi.dingtalk.com/gettoken?appkey={}&appsecret={}".format(app_key, app_secret)
    user_detail_url = "https://oapi.dingtalk.com/topapi/v2/user/get"
    # 获取access_token
    response = requests.get(access_token_url)
    access_token = response.json()["access_token"]
    # 获取用户详情
    user_id = "Your_User_ID"  # 可以是手机号或钉钉ID
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(access_token)
    }
    data = {
        "userid": user_id
    }
    response = requests.post(user_detail_url, headers=headers, json=data)
    user_detail = response.json()
    # 提取operator_id
    operator_id = user_detail["result"]["userid"]
    print(operator_id)
    ```
    
  - range_address：指定一个单元格区域，横坐标根据自己内容宽度而定，纵坐标保证区域纵向区域够大就行
  
  - sheet_id：可以根据以下代码去获取工作表id，access_token的获取参照上面的代码
  
    ```python
    import requests
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
        print(sheet_id)
    ```

- **cacti_graph_info**

​	这段代码中就是后期我们需要更新或者删减的维护部分，我们需要注意一下几点：

- 编号`1`到`n`这个编号排序是连贯且唯一的，如果删除中间某一个序号下的整行条目，那么后面的条目需要依次向前移动一位，变成`1`到`n-1`。

- 其中每个编号对应了一组键值对，包含程序执行所必须的数据字段，具体包括以下：

  - 节点名称（name）：节点名称

  - 带宽（bandwidth）：为客户在该节点的带宽总量

  - 阈值（threshold）：这个阈值这里设置为为总带宽量的75%，具体根据自己需求而定

  - 图形ID（graph_id）：图形id获取方法如下

    - 在需要统计的图名称的位置右键”复制图片地址“

      ![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/12d65fd3-7d82-4ec4-8583-569fdadacabf)

    - 如获取到的地址为：http://212.123.77.78/cacti/graph_image.php?local_graph_id=17014&rra_id=0&graph_height=120&graph_width=500&title_font_size=10&view_type=tree&graph_start=1690878720&graph_end=1690965120，可以看到其中graph_id=17014，将17014填入对应字典中的字段即可

  - 月低于阈值次数统计（low_threshold_counts）：记录当月低于阈值的次数，主程序会在每月2号进行统计时对上月数据进行清零

# 四、关于钉钉机器人设置
## 4.1 创建机器人

1. 点开“群设置”，找到“机器人”选项

![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/7470cb30-6b46-4e47-b7c2-7d44950bfb22)

2. 选择“添加机器人”

![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/ba1d8a9e-07a5-4373-8fb9-08c0fa3d6b1b)

3. 选择“自定义”

![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/fce46efd-62e4-4a70-afaf-3798aec29e0c)


4. 输入机器人名称，在安全设置处勾选“IP地址（段）”，输入部署程序的服务器IP，然后点击“完成”即可

![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/7405e3d1-601a-4465-bb95-8a8218a7a136)

## 4.2 修改程序源码
1. 钉钉机器人创建完成后会给出webhook地址，复制这段地址

   ![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/1a588903-81ae-478b-85a6-7cee8e71cbdc)

   2. 将配置文件config.json中定义的webhook地址修改成新添加的这个机器人的webhook地址

   ![image](https://github.com/yuanzigsa/CactiTrafficStatisticsPushToDingtalk/assets/30451380/c2dd705d-7b43-4b9f-a45c-b75482f1e1d9)


