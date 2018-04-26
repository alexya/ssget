from __future__ import print_function
import urllib2
import os 
import re
import json
import time
from bs4 import BeautifulSoup
from collections import namedtuple
from pprint import pprint

from subprocess import *
from subprocess import STARTUPINFO # for python2, we need to import STARTUPINFO

import psutil
from psutil import NoSuchProcess

import requests
from requests.exceptions import ConnectionError

class ProxyData:
    def __init__(self):
        self.Name = ''
        self.IPAddress = ''
        self.Port = ''
        self.Password = ''
        self.Method = ''

config_file = "gui-config.json"

# We need the absolute path to find the root of SSR, then to kill the process tree
ssr_path = "C:\\Tools\\ShadowsocksR\\ShadowsocksR.exe"

urls = ["http://ss.ishadowx.com/",
        "https://global.ishadowx.net/",
        "https://get.ishadowx.net/"
        ]

headers = {
    'User-agent': "Mozilla 5.10",
    'cache-control': "no-cache",
    'postman-token': "110d2989-c941-fea3-874f-f5c3c028db49"
    }

soup = None
proxies = []

def request_ishadowx_html(URLs):
    for url in URLs:
        try:
            # solution 1: urlopen
            #response = urllib2.urlopen(url)

            # solution 2: request
            # we have to simulate user-agent to a browser, otherwise, the server will return 403
            print("Connecting to: {url}".format(url=url))
            response = requests.request("GET", url, headers=headers)
            html_doc = response.text
            global soup
            soup = BeautifulSoup(html_doc, 'html.parser')
            print("Data is fetched from: {url}".format(url=url))
            return True

        except ConnectionError as e:
            print(e)
            print
            continue

    return False

def get_proxy(class_def_name):
    print
    for link in soup.find_all("div",class_=class_def_name):
        proxy = ProxyData()

        x = link.find('span')
        if (type(x) == type(link)):
            proxy.Name = x['id']

        # use HTML to parse and get the proxy directly
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
        pprint("{:10}{:20}{:10}{:30}{:10}".format(proxy.Name, proxy.IPAddress, proxy.Port, proxy.Password, proxy.Method))

def parse_config(file_name):
    # ssget folder will be put under the shadowsocksR
    # so, here we need to goto its parent folder and pick up config file

    dir_path = os.path.dirname(os.path.realpath(__file__))
    parent_path = os.path.abspath(os.path.join(dir_path, os.pardir))
    path_file_name = os.path.join(parent_path, file_name)

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

    print
    print("Updated the config file {} successfully.".format(path_file_name))

    return True

def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    gone, still_alive = psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)

    return True

def launch_ssr():
    # if the ShadowsocksR exists, then kill it first.
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
        except NoSuchProcess as e:
            # failed to find the process, go to next pid
            continue

        if (p.name() == "ShadowsocksR.exe") and p.exe() == ssr_path:
            print("The process ShadowsocksR.exe: {id} is found.".format(id=pid))
            if (kill_proc_tree(pid) == True):
                print("The process ShadowsocksR.exe: {id} is terminated successfully.".format(id=pid))
            break

    newproc = psutil.Popen([ssr_path], stdin = PIPE, stdout = PIPE, stderr = PIPE)
    if (newproc != None):
        print("The process ShadowsocksR.exe: {id} is restarted successfully.".format(id=newproc.pid))

    return True

def count_down_sample():
    lineLength = 20
    delaySeconds = 0.05
    frontSymbol = '='
    frontSymbol2= ["-", "\\", "|", "/"]
    backSymbol = ' '
    for i in range(10):
        lineTmpla = "{:%s<%s} {} {:<2}"%(backSymbol, lineLength)
        for j in range(lineLength):
            tmpSymbol = frontSymbol2[j%(len(frontSymbol2))]
            linestr = "\r" + lineTmpla.format(frontSymbol * j, tmpSymbol, j)
            print(linestr, end="")
            time.sleep(delaySeconds)
    print

def count_down(sec):
    count = 0
    while (count < sec):
        n = sec - count
        count += 1
        linestr = "\rThe program will exit in {}s".format(n)
        print(linestr, end='')
        time.sleep(1)
    print

if __name__ == "__main__":
    if not request_ishadowx_html(urls):
        print("Failed to connect to ishadowx server and get data.")

    pprint("{:10}{:20}{:10}{:30}{:10}".format("Name","IP Address","Port","Password","Method"))
    # parse U.S, Japan, and Singapore servers.
    get_proxy("col-sm-6 col-md-4 col-lg-4 us")
    get_proxy("col-sm-6 col-md-4 col-lg-4 jp")
    get_proxy("col-sm-6 col-md-4 col-lg-4 sg")

    print
    print("Found {} shadowsocks proxy servers.".format(len(proxies)))

    if (parse_config(config_file)):
        launch_ssr()

        # sleep for a while, let user check the status and then exit
        count_down(5)
