
#
# Generate html file
#
import html

html_start="""\
<html>
  <head>
    <title>Mail</title>
    <meta content="text/html; charset=GB2312" http-equiv="Content-Type">
  </head>
  <body bgcolor="#FFFFFF" text="#000000">
  <p>Hi, All,</p>
  
  <center><H3>High priority issue list</H3></center>
"""
html_end="""\
  </body>
</html>
"""

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
        self._fp.write('    <table id="buglist" class="width100" cellspacing="1">\r\n')
        self._fp.write('      <tbody>\r\n')

    def table_close(self):
        self._fp.write('      </tbody>\r\n')
        self._fp.write('    </table>\r\n')

    def table_create_row(self, row):
        self._fp.write('        <tr border="1" bgcolor="#c8c8ff">\r\n')
        self._fp.write('  <td><a href="http://10.1.8.23/mantis/view.php?id={0}">{0}</a></td>\r\n'.format(row[0]))
        self._fp.write('  <td class="center">{}</td>\r\n'.format(row[1]))
        self._fp.write('  <td class="left">{}</td>\r\n'.format(html.escape(row[2])))
        self._fp.write('  <td>{}</td>'.format(html.escape(row[3])))
        self._fp.write('        </tr>\r\n')
        
    def write_text(self, line='', bold=False):
        if bold: self._fp.write('<b>')
        line = html.escape(line)
        line = line.replace('\n', "<br>")
        self._fp.write(line)
        if bold: self._fp.write('</b>')
        self._fp.write('\r\n')
    
    def wirte_bug_list(self, bugs):
        for b in bugs:
            self._fp.write('    <a href="http://10.1.8.23/mantis/view.php?id={0}">{0}</a>\r\n'.format(b))
    
    def spliter(self):
        self._fp.write('<hr/>')
