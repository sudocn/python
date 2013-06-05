# Get bug list from mantis server
# Author: cpeng, 2012

import os, sys
import webget, mailer
import csv
import datetime
from report import HtmlReport
from io import StringIO 

fy = ('yfeng','lixia','jiahuaili','zhangsong','weiweiyu','zoulu','luoweizhang', \
        'panyiwen','wangxiaohong','lqian','faquirmxg','sence_zhang','chenxuesong', \
        'wanglibo','guoguangyi','liuyong','dingshengdong')
wl = ('wuliang','gaoyinghui','xuchenyu')
dl = ('liuyisheng')
mm = ('xiehongbiao','denglei','juweiming','guozhengqin','zouhuangfei')
gb = ('zhangguobin','jinhui','chenhengyi','majun')
ge = ('yangrong','panlifeng')
ril = ('cpeng','wfmao','zhaoyanjun','wangziyi','houxianlong')

team_all = (fy, wl, dl, mm, gb, ge, ril)
table_header = []
mantis_all = []
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

def team_bug_list(mlist, team):

    print('total ', len(mlist))
    
    idx = col('Status')
    assigned = [x for x in mlist if x[idx] == 'assigned']
    print ('assigned ', len(assigned))
    
    idx = col('Assigned To')
    pld = [x for x in assigned if x[idx] in team]
    print(team[0], 'team', len(pld))
    return pld
 
def team_high_bug_list(mlist, team):
     idx = col('Priority')
     return [x for x in team_bug_list(mlist, team) if x[idx] in ('high', 'urgent', 'immediate')]

def team_normal_bug_list(mlist, team):
     idx = col('Priority')
     return [x for x in team_bug_list(mlist, team) if x[idx] not in ('high', 'urgent', 'immediate')]

'''    
def field2index(hdr, fields):
    ids=[]
    for f in fields:
        if f not in hdr: raise ValueError("fields error "," fields not in header list")
        ids.append(hdr.index(f))
    return ids
'''

def find_bug_by_id(mlist, id):
    for bug in mlist:
        if bug[0] == id:
            return bug
    
def sort_by_platform(mlist):
    idx = col('Project') 
    
    eva = [x[0] for x in mlist if 'Eva' in x[idx] or 'EVA' in x[idx]]
    gbread = [x[0] for x in mlist if 'gingerbread' in x[idx] or '2.3.7' in x[idx]]
    t11_ics = [x[0] for x in mlist if 'T11' in x[idx]]
    g01_ics = [x[0] for x in mlist if 'ICS' in x[idx]]
    
    total = [x[0] for x in mlist]
    others = set(total) - set(eva) - set(gbread) - set(t11_ics) - set(g01_ics)
    others = list(others)
    print(len(total), len(eva), len(gbread), len(t11_ics), len(g01_ics), len(others))
    
    return ['EVA',eva], ['Android 2.3.7',gbread], ['T11 4.0',t11_ics],\
         ['G01 4.0',g01_ics], ['Others',others]

def sort_by_user(mlist):
    idx = col('Assigned To')
    users = set([x[idx] for x in mlist])
    result = []
    for u in users:
        bug = [x[0] for x in mlist if u == x[idx]]
        if len(bug) > 0:
            result.append((u,bug))            
    return sorted(result, key = lambda x: len(x[1]), reverse = True)

def sort_resolved_by_user(orig_owners):
    users = set([x[1] for x in orig_owners])
    result = []
    for u in users:
        bug = [x[0] for x in orig_owners if x[1] == u]
        result.append((u,bug))
    return result

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

def report_platform_txt(mlist, sorted_id, report):
    for plat in sorted_id:
        title, bugs = plat
        if len(title) > 0:
            print('\n' + title + ' (%d)' % len(plat[1]))
            for id in bugs:
                line = find_bug_by_id(mlist, id)
                d = dict(zip(table_header, line))
                print("%05d %8s %12s %s" % (d['Id'], d['Priority'], d['Assigned To'], d['Status']))

def format_html_row(buginfo, report):
    #header=['Id', 'Assigned To', 'Summary', 'Project']
    #ids = field2index(table_header, header)

#    if line == None:
#        pass
    d = dict(zip(table_header, buginfo))
    report.table_create_row((d['Assigned To'], d['Priority'], d['Status'], d['Id'], d['Summary']))

def format_html_table(mlist, ids, report):
    report.table_open()
    for id in ids:
        buginfo = find_bug_by_id(mlist, id)
        format_html_row(buginfo, report)
    report.table_close()

def report_platform_html(mlist, sorted_id, report):
    for plat in sorted_id:
        if len(plat[1]) > 0:
            report.write_text('\n' + plat[0] + ' (%d)' % len(plat[1]))
            format_html_table(mlist, plat[1], report)
               
def report_user_html(mlist, sorted_id, orig_status, report):
    report.table_open()
    sum_list = []
    for user,bugs in sorted_id:
        if len(bugs) == 0:
            continue
        #report.write_text('\n' + user + ' (%d)' % len(bugs))
        # current issues
        for id in bugs: 
            buginfo = find_bug_by_id(mlist, id)
            format_html_row(buginfo, report)
        
        # resolved issues
        for ou, obs in orig_status:
            if ou == user:
                for id in obs:
                    buginfo = find_bug_by_id(mantis_all, id)
                    if buginfo[col("Assigned To")] != ou: # TODO: may transfered to team members
                        continue # TODO: transfered issues, should be recorded
                    format_html_row(buginfo, report)

    for ou, obs in orig_status:
        if ou not in [x[0] for x in sorted_id]:
            for id in obs:
                buginfo = find_bug_by_id(mantis_all, id)
                if buginfo[col("Assigned To")] != ou:
                    continue # TODO: transfered issues, should be recorded
                format_html_row(buginfo, report)
    
        
    report.table_close()

def get_diff(now, prev):
    now_set = set([x[0] for x in now])
    prev_set = set([x[0] for x in prev])
    
    new = now_set - prev_set
    solved = prev_set - now_set
    
    print('changes',new,solved)
    return new,solved

def report_diff_txt(mlist, diff, report):
    if diff is None: return
    new, removed = diff
    if len(new):
        report_platform_txt(mlist, [('New issues added into list', new)], report)
    if len(removed):
        report_platform_txt(mantis_all, [('Issues removed from list',removed)], report)

def report_diff_html(mlist, diff, report):
    if diff is None:
        return
    new, removed = diff
    #report.write_text("New issues: %d\n" % (len(new)))
    if len(new):
        report_platform_html(mantis_all, [('New issues', new)], report)
    if len(removed):
        report_platform_html(mantis_all, [('Issues removed (fixed, feedback, transfered)', removed)], report)
    
def gen_report(mlist, diff, orig_owners, html=True):
    sio = StringIO()
    if html:
        report = HtmlReport(sio)
    else:
        report = None
    
    if html:
        report.write_text("\nSummary", True)
        report.spliter()
        
    if html:
        report_diff_html(mlist, diff, report)
    else:
        report_diff_txt(mlist, diff, report)            

    '''
    #
    p = sort_by_platform(mlist)
    if html:
        report.write_text("\nIssues by platform", True)
        report.spliter()
        report_platform_html(mlist, p, report)
    else:
        report_platform_txt(mlist, p, report)
    '''
    #
    u = sort_by_user(mlist)
    ru = sort_resolved_by_user(orig_owners)
    if html:
        report.write_text("\nIssues per engineer \n" , True)
        #report.write_text("\n\nIssues by owner", True)
        report.spliter()
        report_user_html(mlist, u, ru, report)
    else:
        report_platform_txt(mlist, u, report)
        
    '''
    #    
    t = sort_by_time(mlist)
    if html:
        report.write_text('')
        report.write_text("\n\nIssues by age", True)
        report.spliter()
        report_platform_html(mlist, t, report)
    else:
        report_platform_txt(mlist, t, report)        
    '''
        
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
    if not os.path.exists(yesterday):
        yesterday = ""
    return today,yesterday

def anaylse_by_team(team, mantis_prev):
    # 2. Analyze maintis status      
    high = team_high_bug_list(mantis_all, team)
    total = team_bug_list(mantis_all, team)

    diff = {}
    orig_owners = []
    if len(mantis_prev) > 0: # previous status
        high_prev = team_high_bug_list(mantis_prev, team)
        total_prev = team_bug_list(mantis_prev, team)
        diff = get_diff(total, total_prev)
        new, resolved = diff

        idx = col('Assigned To')
        orig_owners = [(x[0], x[idx]) for x in total_prev if x[0] in resolved]

    # 3. Generate report
    sum = gen_report(high, diff, orig_owners)
    with open(r"d:\report_%s.html" % team[0], "w", encoding='utf-8') as f:
        print(sum, file=f)

    # 4. Send Mail
    mailer.set_team(team[0])
    #mailer.send_html(sum)
        
def main():
    global mantis_all
    print("hello")
    today, yesterday = get_file_names() 

    # 1. Retrieve data from mantis web
    live = True # True
    if live:
        csv = webget.wget2()
        with open(today, "w", encoding='utf-8') as f:
            f.write(csv)
    else:
        today = r"D:\mantis\buglist1228.csv"
        yesterday = r"D:\mantis\buglist1222.csv"

    mantis_all = parse_csv(today)
    mantis_prev = []    
    if len(yesterday) > 0: # previous status
        mantis_prev = parse_csv(yesterday)

    for team in mm,:#team_all:
        anaylse_by_team(team, mantis_prev)
    
if __name__ == '__main__':
    main()
