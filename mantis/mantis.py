# Get bug list from mantis server
# Author: cpeng, 2012

import os, sys
import webget, mailer
import csv
import datetime
from report import HtmlReport
from io import StringIO 

users = ('cpeng','wfmao','zhaoyanjun','wangziyi','houxianlong',\
         'zhangguobin','jinhui','chenhengyi','majun',\
         'wuliang','gaoyinghui','xuchenyu',\
         'mjoang','huangchang_songwensheng','huangchang_liangyanli')

table_header = []
prefix="""\
Hi, all

Today's critical issue list, owners please focus on those issues.

"""

def parse_csv(filename):
    global table_header
    mantis_list = []
#    with open(filename, newline='', encoding='utf-8') as f:
    with open(filename, newline='\n', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            mantis_list.append(row)
            
        table_header = mantis_list[0]
        
    m = mantis_list[1:]
    for i in m: 
        i[0] = int(i[0])
    return m 

def col(title):
    return table_header.index(title)

def pld_bug_list(mlist):

    print('total ', len(mlist))
    
    idx = col('Status')
    assigned = [x for x in mlist if x[idx] == 'assigned']
    print ('assigned ', len(assigned))
    
    idx = col('Assigned To')
    pld = [x for x in assigned if x[idx] in users]
    print('pld ', len(pld))
    return pld
 
def pld_high_bug_list(mlist):
     idx = col('Priority')
     return [x for x in pld_bug_list(mlist) if x[idx] in ('high', 'urgent', 'immediate')]
    
def field2index(hdr, fields):
    ids=[]
    for f in fields:
        if f not in hdr: raise ValueError("fields error "," fields not in header list")
        ids.append(hdr.index(f))
    return ids
        
def format_text_summary(mlist):
    header=['Id', 'Assigned To', 'Summary']
    ids = field2index(table_header, header)
    text = ""
    for line in mlist:
        text += "%s: %-15s %s\r\n" % (line[ids[0]], line[ids[1]], line[ids[2]])
    return text
    
def gen_text_summary(mlist):
    text = ""
    idx = table_header.index('Project') 

    selected = [x for x in mlist if x[idx].startswith('ATgingerbread')]
    text += "\r\nAndroid 2.3.7 (%d)\r\n" % len(selected)
    text += format_summary(selected)

    selected = [x for x in mlist if x[idx].startswith('T11')]
    text += "\r\nT11 4.0 (%d)\r\n" % len(selected)
    text += format_summary(selected)
    
    selected = [x for x in mlist if x[idx].startswith('ICS')]
    text += "\r\nG01 4.0 (%d)\r\n" % len(selected)
    text += format_summary(selected)
    
    print(text)
    return text

def find_bug_by_id(mlist, id):
    for bug in mlist:
        if bug[0] == id:
            return bug
    
def format_html_row(mlist, id, report):
    header=['Id', 'Assigned To', 'Summary', 'Project']
    ids = field2index(table_header, header)
    line = find_bug_by_id(mlist, id)
    report.table_create_row((line[ids[0]], line[ids[1]], line[ids[2]], line[ids[3]].replace('_',' ')))

def format_html_table(mlist, ids, report):
    report.table_open()
    for id in ids:
        format_html_row(mlist, id, report)
    report.table_close()

def report_platform_html(mlist, sorted_id, report):
    for plat in sorted_id:
        if len(plat[1]) > 0:
            report.write_text('\n' + plat[0] + ' (%d)' % len(plat[1]))
            format_html_table(mlist, plat[1], report)
               
def sort_by_platform(mlist):
    idx = col('Project') 
    
    showstp = [x[0] for x in mlist if 'howstopper' in x[idx]]
    gbread = [x[0] for x in mlist if x[idx].startswith('ATgingerbread') or '2.3.7' in x[idx]]
    t11_ics = [x[0] for x in mlist if 'T11' in x[idx]]
    g01_ics = [x[0] for x in mlist if 'ICS' in x[idx]]
    
    total = [x[0] for x in mlist]
    others = set(total) - set(showstp) - set(gbread) - set(t11_ics) - set(g01_ics)
    others = list(others)
    print(len(total), len(showstp), len(gbread), len(t11_ics), len(g01_ics), len(others))
    
    return ['Show stoppers',showstp], ['Android 2.3.7',gbread], ['T11 4.0',t11_ics],\
         ['G01 4.0',g01_ics], ['Others',others]

def sort_by_user(mlist):
    idx = col('Assigned To')
    result = []
    for u in users:
        bug = [x[0] for x in mlist if u == x[idx]]
        if len(bug) > 0:
            result.append((u,bug))            
    return sorted(result, key = lambda x: len(x[1]), reverse = True)

def sort_by_time(mlist):
    idx = col('Date Submitted')
    now = datetime.datetime.now().date()
    
    datelist = [[x[0], datetime.datetime.strptime(x[idx], "%Y-%m-%d").date()] for x in mlist]
        
    ot90 = []
    ot30 = []
    ot14 = []
    newly = []
    
    for i in datelist:
        if (now - i[1]).days > 90: ot90.append(i[0])
        elif (now - i[1]).days > 30: ot30.append(i[0])
        elif (now - i[1]).days > 14: ot14.append(i[0])
        else: newly.append(i[0])
    
    return ['> 3 months',ot90], ['> 1 month',ot30], ['> 2 weeks',ot14], ['< 2 weeks',newly]

def get_diff(now, prev):
    now_set = set([x[0] for x in now])
    prev_set = set([x[0] for x in prev])
    
    new = now_set - prev_set
    solved = prev_set - now_set
    
    print(new,solved)
    return new,solved

def gen_report(mlist, diff, html=True):
    sio = StringIO()
    if html: report = HtmlReport(sio)
    
    if html:
        report.write_text("\nSummary", True)
        report.spliter()
        report.write_text("\n%d high priority issues\n" % (len(mlist)), True)
        new, removed = diff
        #report.write_text("New issues: %d\n" % (len(new)))
        if len(removed):
            report_platform_html(mlist, [('New issues added into list', new)], report)
        report.write_text("\nIssues removed from list (fixed, feedback, transfered): %d\n" % (len(removed)))
        if len(removed):
            print(','.join([str(x) for x in removed]))
            report.wirte_bug_list(removed)
        report.write_text("\n")
            
        #report_platform_html(mlist, p, report)

    #
    p = sort_by_platform(mlist)
    if html:
        report.write_text("\nIssues by platform", True)
        report.spliter()
        report_platform_html(mlist, p, report)
    else:
        pass
    #
    u = sort_by_user(mlist)
    if html:
        report.write_text('')
        report.write_text("\n\nIssues by owner", True)
        report.spliter()
        report_platform_html(mlist, u, report)
        
    t = sort_by_time(mlist)
    if html:
        report.write_text('')
        report.write_text("\n\nIssues by age", True)
        report.spliter()
        report_platform_html(mlist, t, report)
        
    
    if html: report.close()
    sio.seek(0)
    return sio.read()   

def get_file_names():
    path = 'D:\\mantis\\'
    
    now = datetime.datetime.now()
    today = path + "buglist%02d%02d.csv" % (now.month, now.day)
    
    for i in range(10):  # trace back for 10 days
        now -= datetime.timedelta(days=1)
        yesterday = path + "buglist%02d%02d.csv" % (now.month, now.day)
        if (os.path.exists(yesterday)):
            break
    return today,yesterday
    
def main():
    print("hello")
    today, yesterday = get_file_names() 
    live = True # True
    # retrieve data from web
    if live:
        csv = webget.wget2()
        
    else:
        with open(r"D:\cpeng\Download\cpeng.csv", encoding='utf-8') as f:
            csv = f.read()

    # save csv file
    with open(today, "w", encoding='utf-8') as f:
        f.write(csv)
          
    mantis = parse_csv(today)
    mantis_prev = parse_csv(yesterday)
    
    high = pld_high_bug_list(mantis)
    high_prev = pld_high_bug_list(mantis_prev)
    
    diff = get_diff(high, high_prev)
    sum = gen_report(high, diff)
    
    print(sum)
    mailer.send_html(sum)
    
if __name__ == '__main__':
    main()
