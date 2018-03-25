import urllib2
import os 
import re
import json
from bs4 import BeautifulSoup
from collections import namedtuple
from pprint import pprint
from subprocess import *
from subprocess import STARTUPINFO # for python2, we need to import STARTUPINFO

class ProxyData:
    def __init__(self):
        self.Name = ''
        self.IPAddress = ''
        self.Port = ''
        self.Password = ''
        self.Method = ''

url = "https://global.ishadowx.net/"
url = "http://ss.ishadowx.com/"
config_file = "gui-config.json"

response = urllib2.urlopen(url)
html_doc = response.read()
soup = BeautifulSoup(html_doc, 'html.parser')
proxies = []

def get_proxy(class_def_name):
    print
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

        # if the Port is empty, we need to set a default value such as '12345'
        # otherwise, the SSR gui will prompt error dialog
        if not proxy.Port:
            proxy.Port = '12345'
        proxies.append(proxy)
        pprint("{:10}{:20}{:10}{:15}{:10}".format(proxy.Name, proxy.IPAddress, proxy.Port, proxy.Password, proxy.Method))

def parse_config(file_name):
    # ssget folder will be put under the shadowsocksR
    # so, here we need to goto its parent folder and pick up config file

    dir_path = os.path.dirname(os.path.realpath(__file__))
    parent_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    path_file_name = os.path.join(parent_path, file_name)

    print
    print("Found the config file {}.".format(path_file_name))

    with open(path_file_name) as jsonFile:
        json_data = json.load(jsonFile)

    # ShadowsocksR 4.5.2 proxy config [name:value]
    # 
    # "remarks" : "ipjpa",
    # "id" : "48DDEE23895592D434103B3083CFBE51",
    # "server" : "a.jpip.pro",
    # "server_port" : 443,
    # "server_udp_port" : 0,
    # "password" : "80918835",
    # "method" : "aes-256-cfb",
    # "protocol" : "origin",
    # "protocolparam" : "",
    # "obfs" : "plain",
    # "obfsparam" : "",
    # "remarks_base64" : "aXBqcGE",
    # "group" : "FreeSSR-public",
    # "enable" : true,
    # "udp_over_tcp" : false

    configs = []
    Metro = namedtuple('configs',
        'remarks, id, server, server_port, server_udp_port, password, method, protocol, protocolparam, obfs, obfsparam, remarks_base64, group, enable, udp_over_tcp')
    metros = [Metro(**kk) for kk in json_data['configs']]
    for p in proxies:
        metro = Metro(
            remarks = p.Name,
            id = "",
            server = p.IPAddress,
            server_port = p.Port,
            server_udp_port = 0,
            password = p.Password,
            method = p.Method,
            protocol = "origin",
            protocolparam = "",
            obfs = "",
            obfsparam = "",
            remarks_base64 = "",
            group = "iShadowX",
            enable = True,
            udp_over_tcp = False
        )
        configs.append(metro._asdict())

    # do *not* keep the existing proxies, will use the newly proxies to replace old ones.
    #
    # for m in metros:
    #     configs.append(m._asdict())

    # Write back the proxies data to config file
    json_data['configs'] = configs
    with open(path_file_name, 'w') as jsonFile:
        ss = json.dumps(json_data, sort_keys = True, indent = 4, separators = (',', ': '), encoding = "utf-8", ensure_ascii = True)
        jsonFile.write(ss)

    return True

def launch_ssr():
    startupinfo = STARTUPINFO()
    startupinfo.dwFlags |=  STARTF_USESHOWWINDOW
    startupinfo.wShowWindow =  SW_HIDE
    Popen("..\ShadowsocksR.exe",stdin = PIPE, stdout = PIPE,stderr=PIPE,startupinfo=startupinfo)

    return True

if __name__ == "__main__":
    get_proxy("col-sm-6 col-md-4 col-lg-4 us")
    get_proxy("col-sm-6 col-md-4 col-lg-4 jp")
    get_proxy("col-sm-6 col-md-4 col-lg-4 sg")

    print
    print("Found {} shadowsocks proxy servers.".format(len(proxies)))

    if (parse_config(config_file)):
        launch_ssr()
