import requests
import os

def get_yaml():
    print("开始获取clsah订阅")
    urls = ["https://api.dler.io//sub?target=clash&url=https://raw.githubusercontent.com/v2clash/Autoproxy/main/Long_term_subscription_num&insert=false&config=https://raw.githubusercontent.com/zwrt/Toolbox/main/config/ACL4SSR.ini&emoji=true"]
    n = 1
    for i in urls:
        response = requests.get(i)
        #print(response.text)
        file_L = open("output.yaml", 'w', encoding='utf-8')
        file_L.write(response.text)
        file_L.close()
        n += 1
    print("clash订阅获取完成！")

get_yaml()
