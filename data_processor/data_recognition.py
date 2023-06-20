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
    # 使用图像处理库来检测文本区域
    # 这里使用了一些图像处理的技术，如边缘检测和轮廓检测
    # 你可以根据具体情况选择适合的方法
    # 这里只是一个示例，可能需要根据实际情况进行调整
    edges = cv2.Canny(image, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 提取文本区域
    text_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 100 and h > 10:  # 根据实际情况调整文本区域的大小阈值
            text_regions.append((x, y, w, h))

    return text_regions

# 提取Max:后的数据
def extract_max_value(image, text_regions):
    max_values = []
    for region in text_regions:
        x, y, w, h = region
        text_image = image[y:y+h, x:x+w]

        # 对小数部分进行预处理，例如模糊处理或裁剪
        # 这里使用了图像裁剪的方法，将小数部分的数字从图像中裁剪掉
        text_image = text_image[:, :-140]  # 裁剪掉右侧的小数部分

        # 使用文本处理库来提取Max:后的数据
        # 这里使用了正则表达式来匹配Max:后的数据
        # 你可以根据具体情况选择适合的方法
        # 这里只是一个示例，可能需要根据实际情况进行调整
        text = pytesseract.image_to_string(text_image)
        match = re.search(r'Max:\s*([\d.]+)', text)
        if match:
            max_value = float(match.group(1))
            max_values.append(max_value)

    return max_values

# 返回每张图片中的最大值
def get_max_values(image_paths):
    max_values = []
    for image_path in image_paths:
        image = read_image(image_path)
        text_regions = detect_text(image)
        max_values.extend(extract_max_value(image, text_regions))

    return max_values

# 测试代码
image_paths = ['../data_fetcher/graph/1.png','../data_fetcher/graph/2.png', '../data_fetcher/graph/3.png','../data_fetcher/graph/4.png',]
max_values = get_max_values(image_paths)
formatted_max_values = ["{:.2f}".format(value) for value in max_values]
print(formatted_max_values)
