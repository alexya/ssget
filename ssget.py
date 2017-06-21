import urllib2
import re
from bs4 import BeautifulSoup


class ProxyData:
    def __init__(self):
        self.Name = ''
        self.IPAddress = ''
        self.Port = ''
        self.Password = ''
        self.Method = ''

#url = "http://python.org"
url = "http://ss.ishadowx.com/"

response = urllib2.urlopen(url)
html_doc = response.read()
soup = BeautifulSoup(html_doc, 'html.parser')
proxies = []

# col-sm-6 col-md-4 col-lg-4 us
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

        print(proxy.Name)
        print(proxy.IPAddress)
        print(proxy.Port)
        print(proxy.Method)

        proxies.append(proxy)

        print

# for link in soup.find_all("div",class_="col-sm-6 col-md-4 col-lg-4 jp"):
#     #print link
#     print

# for link in soup.find_all("div",class_="col-sm-6 col-md-4 col-lg-4 ssr"):
#     #print link
#     print

if __name__ == "__main__":
    get_proxy("col-sm-6 col-md-4 col-lg-4 us")
    get_proxy("col-sm-6 col-md-4 col-lg-4 jp")
    get_proxy("col-sm-6 col-md-4 col-lg-4 ssr")

    print("The objects account is {}".format(len(proxies)))
