import wx
import data

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
		self.idTextControl = wx.TextCtrl(self)
		# Repeat element (+, *, ? , custom)
		element  = ['*', '+', '?','']
		self.repeatComboBox = wx.ComboBox(self,-1,"", (15, 30), wx.DefaultSize,element)
		# Ignore element (radio button) yes/no
		# Create a sizer for the radio buttons
		ignoreRadioButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.ignoreFalseRadioButton = wx.RadioButton(self, -1, 'false', (10, 30), style=wx.RB_GROUP)
		self.ignoreTrueRadioButton = wx.RadioButton(self, -1, 'true', (10, 10))
		# Create the radio buttons to the sizer
		ignoreRadioButtonSizer.Add(self.ignoreFalseRadioButton)
		ignoreRadioButtonSizer.Add(self.ignoreTrueRadioButton)
		# OK button
		okButton = wx.Button(self, id=wx.ID_OK)

		# Add widgets to the grid
		flexGridSizer.AddMany([
			(idLabel), (self.idTextControl, 1, wx.EXPAND),
			(repeatLabel), (self.repeatComboBox, 1, wx.EXPAND),
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
		
		self.repeatComboBox.Bind(wx.EVT_COMBOBOX, self.OnPhaseSelection)
		self.SetSizer(sizer)

	def OnValid(self, event):
		print 'SequencePanel.OnValid'
		selectedTreeItem = data.treePanel.treeControl.GetSelection()
		itemData = data.treePanel.treeControl.GetItemData(selectedTreeItem)

		# Set values to the object
		obj = itemData.GetData()
		obj.id = self.idTextControl.GetValue()
		obj.repeat = self.repeatComboBox.GetValue()
		if self.ignoreTrueRadioButton.GetValue():
			obj.ignore = True
		else:
			obj.ignore = False

		# Set the object back to the tree control
		data.treePanel.treeControl.SetItemData(selectedTreeItem, wx.TreeItemData(obj))
			
	def OnPhaseSelection(self, event):
		el = self.repeatComboBox.GetValue()

		if el == '+':
			self.repeatComboBox.SetEditable(False)
		elif el == '*':
			self.repeatComboBox.SetEditable(False)
		elif el == '?':
			self.repeatComboBox.SetEditable(False)
		elif el == '':
			self.repeatComboBox.SetEditable(True)