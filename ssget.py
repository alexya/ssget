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
        proxy.IPAddress = re.split(":|\xef\xbc\x9a", hh[0].text.encode('UTF-8'))[1]
        proxy.Port = re.split(":|\xef\xbc\x9a", hh[1].text.encode('UTF-8'))[1]
        proxy.Password = re.split(":|\xef\xbc\x9a", hh[2].text.encode('UTF-8'))[1]
        proxy.Method = re.split(":|\xef\xbc\x9a", hh[3].text.encode('UTF-8'))[1]
        proxies.append(proxy)

        # print(proxy.Name)
        # print(proxy.IPAddress)
        # print(proxy.Port)
        # print(proxy.Method)

def parse_config(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path_file_name = os.path.join(dir_path, file_name)
    print(file_name)
    print(path_file_name)

    with open(path_file_name) as jsonFile:
        old_data = json.load(jsonFile)

    print(old_data)
    # old_data = json.loads(open(path_file_name, 'r').read())
    # # print(old_data['configs'][0]['remarks'])
    # # print(old_data['configs'][0]['server'])
    # # print(old_data['configs'][0]['server_port'])
    # # print(old_data['configs'][0]['password'])
    # # print(old_data['configs'][0]['method'])

    configs = []
    for p in proxies:
        data = {}
        data['remarks'] = p.Name
        data['server'] = p.IPAddress
        data['server_port'] = p.Port
        data['password'] = p.Password
        data['method'] = p.Method
        data['auth'] = False
        configs.append(data)

    config_json_data = json.dumps(configs)
    print(config_json_data)

    old_data['configs'] = config_json_data
    #print(old_data)

    with open('tt.json', 'w') as jsonFile:
        json.dump(old_data, jsonFile)

if __name__ == "__main__":
    get_proxy("col-sm-6 col-md-4 col-lg-4 us")
    get_proxy("col-sm-6 col-md-4 col-lg-4 jp")
    get_proxy("col-sm-6 col-md-4 col-lg-4 ssr")

    print("The ss proxy account is {}".format(len(proxies)))

    parse_config(config_file)
