import pytesseract
import cv2
import re

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

# 测试结果输出
image_paths = ['../data_fetcher/graph/0.png', '../data_fetcher/graph/1.png', '../data_fetcher/graph/2.png', '../data_fetcher/graph/3.png','../data_fetcher/graph/4.png','../data_fetcher/graph/5.png','../data_fetcher/graph/6.png','../data_fetcher/graph/7.png','../data_fetcher/graph/8.png', '../data_fetcher/graph/9.png', '../data_fetcher/graph/10.png']

max_values = get_max_values(image_paths)
formatted_max_values = ["{:.2f}G".format(value) for value in max_values]

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

print("【今日节点流量统计】")
for image_path, max_value in zip(image_paths, formatted_max_values):
    image_name = image_path.split('/')[-1]
    print(image_info[image_name]['name'], max_value)

print("【流量低于报警值】")
for image_path, max_value in zip(image_paths, max_values):
    image_name = image_path.split('/')[-1]
    if max_value < image_info[image_name]['value'] * 0.75:
        print(image_info[image_name]['name'])
