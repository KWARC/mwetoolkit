import wx

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
		idLabel = wx.StaticText(self, label='id')
		repeatLabel = wx.StaticText(self, label='repeat')
		ignoreLabel = wx.StaticText(self, label='ignore')

		# ########
		# CONTROLS
		# ########
		# List box (surface, lemma, part of speech, syn)
		attributes = ['surface', 'lemma', 'pos', 'syn']
		listBox = wx.ListBox(self, -1, choices=attributes, style=wx.LB_SINGLE)
		listBox.SetSelection(0)
		# Text control
		textControl = wx.TextCtrl(self)
		# Check box (negative/positive)
		checkBox = wx.CheckBox(self, label='Negative')
		# OK button
		okButton = wx.Button(self, id=wx.ID_OK)

		# Add widgets to the grid
		flexGridSizer.AddMany([
			(idLabel), (listBox, 1, wx.EXPAND),
			(repeatLabel), (textControl, 1, wx.EXPAND),
			(ignoreLabel, 1, wx.EXPAND), (checkBox, 1, wx.ALL)
		])

		flexGridSizer.AddGrowableRow(2, 1)
		flexGridSizer.AddGrowableCol(1, 1)

		border = 15
		sizer.Add(flexGridSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=border)
		sizer.Add(okButton, 0, wx.ALL, border=border)

		# ######
		# EVENTS
		# ######
		okButton.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)

		self.SetSizer(sizer)

	def onOK(self, event):
		self.Destroy()

	def onCancel(self, event):
		self.Destroy()