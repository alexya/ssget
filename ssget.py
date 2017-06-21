import urllib2
import os 
import re
import json
from bs4 import BeautifulSoup

class ProxyData:
    def __init__(self):
        self.Name = ''
        self.IPAddress = ''
        self.Port = ''
        self.Password = ''
        self.Method = ''

url = "http://ss.ishadowx.com/"
config_file = "gui-config.json"

response = urllib2.urlopen(url)
html_doc = response.read()
soup = BeautifulSoup(html_doc, 'html.parser')
proxies = []

def get_proxy(class_def_name):
    for link in soup.find_all("div",class_=class_def_name):
        proxy = ProxyData()

        x = link.find('span')
        if (type(x) == type(link)):
            proxy.Name = x['id']

        hh = link.find_all("h4")
        proxy.IPAddress = re.split(":|\xef\xbc\x9a", hh[0].text.encode('UTF-8'))[1].strip()
        proxy.Port = re.split(":|\xef\xbc\x9a", hh[1].text.encode('UTF-8'))[1].strip()
        proxy.Password = re.split(":|\xef\xbc\x9a", hh[2].text.encode('UTF-8'))[1].strip()
        proxy.Method = re.split(":|\xef\xbc\x9a", hh[3].text.encode('UTF-8'))[1].strip()
        proxies.append(proxy)

def parse_config(file_name):
    # ssget folder will be put under the shadowsocksR 
    # so, here we need to goto its parent folder and pick up config file

    dir_path = os.path.dirname(os.path.realpath(__file__))
    parent_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    path_file_name = os.path.join(parent_path, file_name)
    print(path_file_name)

    with open(path_file_name) as jsonFile:
        json_data = json.load(jsonFile)

    configs = []
    for p in proxies:
        data = {}
        data['remarks'] = p.Name
        data['server'] = p.IPAddress
        data['server_port'] = int(p.Port)
        data['password'] = p.Password
        data['method'] = p.Method
        data['auth'] = False
        configs.append(data)
    json_data['configs'] = configs

    with open(path_file_name, 'w') as jsonFile:
        ss = json.dumps(json_data, sort_keys = True, indent = 4, separators = (',', ': '), encoding = "utf-8", ensure_ascii = True)
        jsonFile.write(ss)

if __name__ == "__main__":
    get_proxy("col-sm-6 col-md-4 col-lg-4 us")
    get_proxy("col-sm-6 col-md-4 col-lg-4 jp")
    get_proxy("col-sm-6 col-md-4 col-lg-4 ssr")

    print("The ss proxy account is {}".format(len(proxies)))

    parse_config(config_file)
