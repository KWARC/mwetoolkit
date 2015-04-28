import wx
from MWEFrame import *

if __name__ == '__main__':
	app = wx.App(redirect=False)
	frame = MWEFrame(None, title='MWE pattern designer', size=(800, 600))
	frame.Center()
	frame.Show()
	app.MainLoop()