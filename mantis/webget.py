# Strip web content from HTTP server
# Author: cpeng, 2012

import urllib
import http.cookiejar
import copy

LOGIN_URL=r'http://10.1.8.23/mantis/login.php'
#BUG_URL=r"http://10.1.8.23/mantis/search.php?project_id=0&status_id%5B%5D=10&status_id%5B%5D=20&status_id%5B%5D=30&status_id%5B%5D=40&status_id%5B%5D=50&handler_id%5B%5D=105&handler_id%5B%5D=18&handler_id%5B%5D=216&handler_id%5B%5D=217&handler_id%5B%5D=199&handler_id%5B%5D=195&handler_id%5B%5D=229&handler_id%5B%5D=64&handler_id%5B%5D=41&handler_id%5B%5D=57&handler_id%5B%5D=20&handler_id%5B%5D=74&handler_id%5B%5D=167&handler_id%5B%5D=86&handler_id%5B%5D=50&priority_id%5B%5D=40&priority_id%5B%5D=50&priority_id%5B%5D=60&sticky_issues=on&sortby=status&dir=DESC&hide_status_id=-2"
#BUG_URL=r"http://10.1.8.23/mantis/search.php?status_id=50&sticky_issues=1&sortby=last_updated&dir=DESC&hide_status_id=90"
#BUG_URL=r"http://10.1.8.23/mantis/search.php?project_id=0&status_id=50&priority_id%5B%5D=40&priority_id%5B%5D=50&priority_id%5B%5D=60&sticky_issues=on&sortby=status&dir=DESC&hide_status_id=-2"
BUG_URL=r'http://10.1.8.23/mantis/view_all_set.php?type=3&source_query_id=1751'
CSV_URL=r"http://10.1.8.23/mantis/csv_export.php"

''' hacks for Mantis server
    The permalink create by Mantis server did not get all the bug lists
    Need add some cookie contents
'''
def add_cookie(ckjar):
    a = ckjar._cookies["10.1.8.23"]["/"]
    ck1 = copy.deepcopy(a["MANTIS_STRING_COOKIE"])
    ck1.name = "MANTIS_VIEW_SETTINGS"
    ck1.value = "255"
    ck2 = copy.deepcopy(ck1)
    ck2.name = "MANTIS_PROJECT_COOKIE"
    ck2.value = "0"
    ck3 = copy.deepcopy(ck1)
    ck3.name = "MANTIS_VIEW_ALL_COOKIE"
    ck3.value = "94"
    ck4 = copy.deepcopy(ck1)
    ck4.name = "MANTIS_BUG_LIST_COOKIE"
    ck4.value = r"7935%2C9709%2C5435%2C9634%2C5218%2C9795%2C9794%2C9793%2C9792%2C9791%2C9790%2C9402%2C8249%2C9788%2C9789%2C9685%2C9722%2C9787%2C9783%2C8255%2C9786%2C9554%2C9785%2C8254%2C9784%2C9184%2C9782%2C9781%2C9473%2C9726%2C9780%2C8719%2C9684%2C9178%2C9779%2C9778%2C8728%2C9696%2C9627%2C9527%2C9671%2C9040%2C9777%2C9723%2C9731%2C8759%2C9694%2C9573%2C9771%2C8533"
 
    ckjar.set_cookie(ck1)
    ckjar.set_cookie(ck2) 
    ckjar.set_cookie(ck3)
    ckjar.set_cookie(ck4) 
    #a["MANTIS_VIEW_SETTINGS"] = ck1 #255
    #a["MANTIS_PROJECT_COOKIE"] = 0
    #a["MANTIS_VIEW_ALL_COOKIE"] = 94
    #a["MANTIS_BUG_LIST_COOKIE"] = r"7935%2C9709%2C5435%2C9634%2C5218%2C9795%2C9794%2C9793%2C9792%2C9791%2C9790%2C9402%2C8249%2C9788%2C9789%2C9685%2C9722%2C9787%2C9783%2C8255%2C9786%2C9554%2C9785%2C8254%2C9784%2C9184%2C9782%2C9781%2C9473%2C9726%2C9780%2C8719%2C9684%2C9178%2C9779%2C9778%2C8728%2C9696%2C9627%2C9527%2C9671%2C9040%2C9777%2C9723%2C9731%2C8759%2C9694%2C9573%2C9771%2C8533"
       
def wget2():
    post={'username':'cpeng', 'password':'lInux!@#'}
    
    #cookie = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    ckjar = http.cookiejar.CookieJar()
    cookie = urllib.request.HTTPCookieProcessor(ckjar)
    proxy = urllib.request.ProxyHandler({}) # bypass auto detected proxies
    opener = urllib.request.build_opener(urllib.request.HTTPHandler, proxy, cookie)   
    #opener.add_handlers = ['User-Agent', 'Mozilla/5.0']
    
    urllib.request.install_opener(opener)
    req = urllib.request.Request(LOGIN_URL)
    responser = opener.open(req, urllib.parse.urlencode(post).encode())
#    params = urllib.parse.urlencode(post).encode()
#    responser = urllib.request.urlopen(LOGIN_URL, params)
    
    data = responser.read()
    print(data)
    
    # Modify the cookies
    add_cookie(ckjar)
    
    r2 = urllib.request.urlopen(BUG_URL)
    data = r2.read().decode()
    print(data)

    r3 = urllib.request.urlopen(CSV_URL)
    csv = r3.read().decode()
    
    urllib.request.urlcleanup()
    return csv
    
if __name__ == "__main__":
    r = wget2()
    print(r)
    