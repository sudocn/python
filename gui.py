import wx, gps_log
class MyApp(wx.App):
    def OnInit(self):
        frame = wx.Frame(None, -1, "Hello from wxPython")

        id=wx.NewId()
        self.list=wx.ListCtrl(frame,id,style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list.Show(True)

        self.list.InsertColumn(0,"Fix")
        self.list.InsertColumn(1,"Time")
        self.list.InsertColumn(2,"Sat. cnt")
        self.list.InsertColumn(3,"Longitude")
        self.list.InsertColumn(4,"Latitude")
        self.list.InsertColumn(5,"Satellites")

        frame.Show(True)
        self.SetTopWindow(frame)
        return True

    def InsertItem(self):
        # 0 will insert at the start of the list
        pos = self.list.InsertStringItem(0,"hello")
        # add values in the other columns on the same row
        self.list.SetStringItem(pos,1,"world")
        self.list.SetStringItem(pos,2,"!")
    def InsertLog(self, *args):
        self.list.Append(args)
        #pos = self.list.InsertStringItem(0, fix)
        # add values in the other columns on the same row
        #for i in range(len(args)):
        #    self.list.SetStringItem(pos,i+1,args[i])

app = MyApp(0)
gps_log.main(app.InsertLog)
app.InsertItem()
app.MainLoop()
