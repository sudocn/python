
#
# Generate html file
#
import html

html_start="""\
<html>
  <head>
    <title>Mail</title>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
  </head>
  <body style="background-color:#FFFFFF; color:#000000; font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 10pt; margin: 6px 4px;">
  <p>Hi, All,</p>
  
  <center><H3>Mantis status daily update</H3></center>
"""
html_end="""\
    <p>
    --<br>
    Regards,<br>
    cpeng
    </p>
  </body>
</html>
"""
bgcolors = {"new":"#fcbdbd", 
            "feedback":"#e3b7eb",
            "acknowledged":"#ffcd85",
            "confirmed":"#fff494",
            "assigned":"#c2dfff", 
            "resolved":"#d2f5b0",
            "verified":"#ACE7AE",
            "suspended":"#e8e8e8",
            "closed":"#c9ccc4"}

class HtmlReport():
    def __init__(self, fp):
        #file.__init__(self, name, mode)
        #self._status = ""
        self._fp = fp
        self._open_html()

    def close(self):
        self._close_html()
        #file.close(self)
        
    def _open_html(self):
        self._fp.write(html_start)

    def _close_html(self):
        self._fp.write(html_end)
        
    def table_open(self):
        self._fp.write('    <table id="buglist" style="width: 100%; " cellspacing="1">\r\n') #border: solid 1px #000000;
#        self._fp.write('      <tbody>\r\n')

    def table_close(self):
#        self._fp.write('      </tbody>\r\n')
        self._fp.write('    </table>\r\n')

    def table_create_row(self, row):
        self._fp.write('        <tr style="font-family: Verdana, Arial, Helvetica, sans-serif; font-size: 10pt; padding: 4px; text-align: left;" border="1" bgcolor="%s">\r\n'%bgcolors[row[4]])
        self._fp.write('  <td><a href="http://10.1.8.23/mantis/view.php?id={0}">{0}</a></td>\r\n'.format(row[0]))
        self._fp.write('  <td align="center">{}</td>\r\n'.format(row[1]))
        self._fp.write('  <td align="center">{}</td>\r\n'.format(html.escape(row[2])))
        self._fp.write('  <td align="left">{}</td>\r\n'.format(html.escape(row[3])))
        self._fp.write('  <td align="left">{}</td>'.format(html.escape(row[4])))
        self._fp.write('        </tr>\r\n')
        
    def write_text(self, line='', bold=False):
        if bold: self._fp.write('<b>')
        line = html.escape(line)
        line = line.replace('\n', "<br>")
        self._fp.write(line)
        if bold: self._fp.write('</b>')
        self._fp.write('\r\n')
    
    def wirte_bug_list(self, bugs):
        for i,v in enumerate(bugs):
            if i != 0: self._fp.write(',')
            self._fp.write('    <a href="http://10.1.8.23/mantis/view.php?id={0}">{0}</a>\r\n'.format(v))
    
    def spliter(self):
        self._fp.write('<hr align=left width=35% size=1 noshade />\r\n')

		
