import wx

class SequencePanel(wx.Panel):
	'''docstring for SequencePanel'''
	def __init__(self, *args, **kwargs):
		'''Create the SequencePanel.'''
		wx.Panel.__init__(self, *args, **kwargs)

		# #####
		# SIZER
		# #####
		sizer = wx.BoxSizer(wx.VERTICAL)
		flexGridSizer = wx.FlexGridSizer(4, 2, 16, 32)

		# ######
		# LABELS
		# ######
		idLabel = wx.StaticText(self, label='id')
		repeatLabel = wx.StaticText(self, label='repeat')
		ignoreLabel = wx.StaticText(self, label='ignore')
		emptyLabel = wx.StaticText(self, label='')

		# ########
		# CONTROLS
		# ########
		# Id element
		idTextControl = wx.TextCtrl(self)
		# Repeat element (+, *, ? , custom)
		repeatListBox = wx.ListBox(self)
		# Ignore element (radio button) yes/no
		# Create a sizer for the radio buttons
		ignoreRadioButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
		ignoreTrueRadioButton = wx.RadioButton(self, -1, 'True', (10, 10), style=wx.RB_GROUP)
		ignoreFalseRadioButton = wx.RadioButton(self, -1, 'False', (10, 30))
		# Create the radio buttons to the sizer
		ignoreRadioButtonSizer.Add(ignoreTrueRadioButton)
		ignoreRadioButtonSizer.Add(ignoreFalseRadioButton)
		# OK button
		okButton = wx.Button(self, id=wx.ID_OK)

		# Add widgets to the grid
		flexGridSizer.AddMany([
			(idLabel), (idTextControl, 1, wx.EXPAND),
			(repeatLabel), (repeatListBox, 1, wx.EXPAND),
			(ignoreLabel), (ignoreRadioButtonSizer, 1, wx.ALL|wx.EXPAND),
			(emptyLabel), (okButton, 1, wx.ALL)
		])

		flexGridSizer.AddGrowableRow(2, 1)
		flexGridSizer.AddGrowableCol(1, 1)

		sizer.Add(flexGridSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

		# ######
		# EVENTS
		# ######
		okButton.Bind(wx.EVT_BUTTON, self.OnValid)

		self.SetSizer(sizer)

	def OnValid(self, event):
		print 'SequencePanel.OnValid'