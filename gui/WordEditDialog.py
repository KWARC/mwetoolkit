import wx
import data

class WordEditDialog(wx.Dialog):
	'''docstring for WordEditDialog'''
	def __init__(self, *args, **kwargs):
		'''Create the WordEditDialog.'''
		wx.Dialog.__init__(self, *args, **kwargs)

		# #####
		# SIZER
		# #####
		sizer = wx.BoxSizer(wx.VERTICAL)
		flexGridSizer = wx.FlexGridSizer(3, 2, 9, 25)
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

		# ######
		# LABELS
		# ######
		idLabel = wx.StaticText(self, label='attribute')
		repeatLabel = wx.StaticText(self, label='value')
		emptyLabel = wx.StaticText(self, label='')

		# ########
		# CONTROLS
		# ########
		# List box (surface, lemma, part of speech, syndep)
		attributes = ['surface', 'lemma', 'pos', 'syndep']
		self.listBox = wx.ListBox(self, -1, choices=attributes, style=wx.LB_SINGLE)
		self.listBox.SetSelection(0)
		# Text control
		self.textControl = wx.TextCtrl(self)
		# Check box (negative/positive)
		self.checkBox = wx.CheckBox(self, label='Negative')
		# OK button
		okButton = wx.Button(self, wx.ID_OK)

		# Add widgets to the grid
		flexGridSizer.AddMany([
			(idLabel), (self.listBox, 1, wx.EXPAND),
			(repeatLabel), (self.textControl, 1, wx.EXPAND),
			(emptyLabel, 1, wx.EXPAND), (self.checkBox, 1, wx.ALL)
		])

		flexGridSizer.AddGrowableRow(2, 1)
		flexGridSizer.AddGrowableCol(1, 1)

		border = 15
		sizer.Add(flexGridSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=border)
		sizer.Add(okButton, 0, wx.ALL, border=border)

		self.SetSizer(sizer)

	def OnCancel(self, event):
		print 'WordEditDialog.OnCancel'
		self.Destroy()