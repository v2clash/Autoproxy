import base64
import requests
import re
import time
import os
import random
import datetime
import threading
from tqdm import tqdm

# 文件路径
update_path = "./sub/"
# 所有的clash订阅链接
end_list_clash = []
# 所有的v2ray订阅链接
end_list_v2ray = []
# 所有的节点明文信息
end_bas64 = []
# 获得格式化后的链接
new_list = []

# 永久订阅链接（包含GitHub链接）
e_sub = [
    'https://raw.githubusercontent.com/LonUp/NodeList/main/Clash/Node/Latest.yaml',
    'https://bitbucket.org/huwo1/proxy_nodes/raw/f31ca9ec67b84071515729ff45b011b6b09c10f2/proxy.md',
    'https://raw.githubusercontent.com/SnapdragonLee/SystemProxy/master/dist/clash_config.yaml',
    'https://raw.githubusercontent.com/SnapdragonLee/SystemProxy/master/dist/clash_config_extra_US.yaml'
]

# 对bs64解密
def jiemi_base64(data):
    decoded_bytes = base64.b64decode(data)
    encodings = ['utf-8', 'utf-16', 'utf-32', 'iso-8859-1', 'latin1']
    for encoding in encodings:
        try:
            decoded_str = decoded_bytes.decode(encoding)
            return decoded_str
        except (UnicodeDecodeError, ValueError):
            continue
    raise ValueError("Unable to decode base64 data with known encodings")

# 获取 GitHub 链接内容
def get_github_links():
    for url in e_sub:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text
                # 根据文件内容格式解析链接
                if url.endswith('.yaml') or url.endswith('.yml'):
                    # 直接使用 YAML 内容
                    end_bas64.extend(content.splitlines())
                elif url.endswith('.md'):
                    # 解析 markdown 格式
                    md_links = re.findall(r'\[.*?\]\((http[s]?://[^\s]+)\)', content)
                    end_bas64.extend(md_links)
                print(f"从 {url} 添加链接成功")
            else:
                print(f"无法访问 {url}")
        except Exception as e:
            print(f"获取 {url} 内容失败: {e}")

# 判断是否为订阅链接
def get_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            url_lst = re.findall(r'http[s]?://[^\s]+', response.text)
            for i in url_lst:
                result = i.replace("\\", "").replace('"', "")
                if result not in new_list:
                    if "t" not in result[8]:
                        if "p" not in result[-2]:
                            new_list.append(result)

            for o in new_list:
                for attempt in range(3):  # 尝试三次
                    try:
                        res = requests.get(o)
                        try:
                            skuid = re.findall('proxies:', res.text)[0]
                            if skuid == "proxies:":
                                end_list_clash.append(o)
                        except:
                            try:
                                peoxy = jiemi_base64(res.text)
                                end_list_v2ray.append(o)
                                end_bas64.extend(peoxy.splitlines())
                            except Exception as e:
                                print(f"Error decoding base64: {e}")
                        break
                    except Exception as e:
                        print(f"Attempt {attempt + 1} failed for {o}: {e}")
                        time.sleep(1)  # 等待1秒再试
        else:
            print(f"无法访问 {url}")
    except Exception as e:
        print(f"获取 {url} 内容失败: {e}")

# 写入文件
def write_document():
    if not e_sub:
        print("订阅为空请检查！")
        return

    # 永久订阅
    random.shuffle(e_sub)
    proxy_counts = {}  # 用于存储每个订阅链接的节点数量
    for e in e_sub:
        try:
            res = requests.get(e)
            if e.endswith('.yaml') or e.endswith('.yml'):
                proxys = res.text
                nodes = proxys.splitlines()
                end_bas64.extend(nodes)
                proxy_counts[e] = len(nodes)
            else:
                proxys = jiemi_base64(res.text)
                nodes = proxys.splitlines()
                end_bas64.extend(nodes)
                proxy_counts[e] = len(nodes)
        except Exception as e:
            print(e, "永久订阅出现错误❌跳过", f"Error: {e}")
    print('永久订阅更新完毕')

    # 打印每个订阅链接的节点数量
    for url, count in proxy_counts.items():
        print(f"订阅链接 {url} 包含 {count} 个节点")

    # 永久订阅去重
    end_bas64_A = list(set(end_bas64))
    print("去重完毕！！去除", len(end_bas64) - len(end_bas64_A), "个重复节点")

    # 打印去重后的节点数量
    print(f"Total number of unique nodes: {len(end_bas64_A)}")

    # 获取时间，给文档命名用
    t = time.localtime()
    date = time.strftime('%y%m', t)
    date_day = time.strftime('%y%m%d', t)

    # 创建文件路径
    os.makedirs(f'{update_path}{date}', exist_ok=True)
    txt_dir = f'{update_path}{date}/{date_day}.txt'

    # 写入订阅
    with open(txt_dir, 'w', encoding='utf-8') as file:
        file.write('\n'.join(end_bas64_A))
    print(f"写入 {txt_dir} 完成")

    # 确认 Long_term_subscription_num 内容
    num_nodes = len(end_bas64_A)
    print(f"Number of nodes to write in Long_term_subscription_num: {num_nodes}")

    # 编码为 base64 格式
    base64_content = base64.b64encode('\n'.join(end_bas64_A).encode('utf-8')).decode('utf-8')

    # 写入总长期订阅
    with open("Long_term_subscription_num", 'w', encoding='utf-8') as file_L_num:
        file_L_num.write(base64_content)
    print(f"写入 Long_term_subscription_num 完成")

    # 更新 README
    with open("README.md", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    TimeDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for index in range(len(lines)):
        try:
            if lines[index].startswith('`https://raw.githubusercontent.com/v2clash/Autoproxy/main/Long_term_subscription_num'):
                lines[index + 1] = f'`Total number of merge nodes: {num_nodes}`\n'
        except Exception as e:
            print(f"更新 README 失败: {e}")

    with open("README.md", 'w', encoding='utf-8') as f:
        f.write(''.join(lines))

    print("合并完成✅")
    try:
        numbers = sum(1 for _ in open(txt_dir))
        print("共获取到", numbers, "节点")
    except Exception as e:
        print(f"计算节点数量时出现错误: {e}")

    return

# 获取clash订阅
def get_yaml():
    print("开始获取clash订阅")
    urls = [
        "https://api.dler.io//sub?target=clash&url=https://raw.githubusercontent.com/v2clash/Autoproxy/main/Long_term_subscription_num&insert=false&config=https://raw.githubusercontent.com/zwrt/Toolbox/main/config/ACL4SSR.ini&emoji=true"
    ]
    for i in urls:
        response = requests.get(i)
        with open("Long_term_subscription.yaml", 'w', encoding='utf-8') as file_L_yaml:
            file_L_yaml.write(response.text)
    print("clash订阅获取完成！")

if __name__ == '__main__':
    threads = []
    for url in e_sub:
        thread = threading.Thread(target=get_content, args=(url,))
        thread.start()
        threads.append(thread)
    # 等待线程结束
    for t in tqdm(threads):
        t.join()
    print("========== 开始获取 GitHub 订阅链接 ==========")
    get_github_links()
    print("========== 获取 GitHub 订阅链接完成 ==========")
    print("========== 准备写入订阅 ==========")
    write_document()
    print("========== 写入完成任务结束 ==========")
    get_yaml()
