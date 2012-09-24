import smtplib
import datetime
from email.mime.text import MIMEText

fromaddr = 'cpeng@augustatek.com'
toaddrs  = 'cpeng@augustatek.com'
ccaddrs = 'cpeng@augustatek.com'

def gen_subject():
    dt = datetime.datetime.now()
    subj = "current critical issues summary of Phone - Mantis " + "%s/%s %s:%02d"%(dt.month, dt.day, dt.hour, dt.minute) + "\r\n"
    return  subj

def send_text(text):
    msg = MIMEText(text,'plain','gb2312')
    send(msg)
    
def send_html(html):
    msg = MIMEText(html, 'html', 'gb2312')
    send(msg)
    
def send(msg):
    msg['Subject']= gen_subject()
    msg['From'] = fromaddr
    msg['To'] = toaddrs
    #msg['Cc'] = ccaddrs
    
    server = smtplib.SMTP_SSL('mailbj.augustatek.com.cn')
    server.set_debuglevel(1)
    server.login('cpeng','lInux!@#')
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    msg = "hello"
    r = send_text(msg)
