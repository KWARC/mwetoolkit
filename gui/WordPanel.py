import wx
import sys
from WordEditDialog import *

class WordPanel(wx.Panel):
	'''docstring for WordPanel'''
	def __init__(self, *args, **kwargs):
		'''Create the WordPanel.'''
		wx.Panel.__init__(self, *args, **kwargs)

		# #####
		# SIZER
		# #####
		sizer = wx.BoxSizer(wx.VERTICAL)
		flexGridSizer = wx.FlexGridSizer(3, 2, 16, 32)
		addremoveButtonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		# ######
		# LABELS
		# ######
		idLabel = wx.StaticText(self, label='id')
		elementsLabel = wx.StaticText(self, label='elements')
		emptyLabel = wx.StaticText(self, label='')

		# ########
		# CONTROLS
		# ########
		# Id element
		idTextControl = wx.TextCtrl(self)
		# List box containing values
		self.listBox = wx.ListCtrl(self, style=wx.LB_SINGLE)
		self.listBox.InsertColumn(0, 'attribute', width=80)
		self.listBox.InsertColumn(1, 'value', width=120)
		self.listBox.InsertColumn(2, 'negation', wx.LIST_FORMAT_RIGHT,50)
		# + (add) button
		addButton = wx.Button(self, label='+')
		# - (remove) button
		removeButton = wx.Button(self, label='-')
		# By default, the remove button is disabled
		removeButton.Disable()
		# OK button
		okButton = wx.Button(self, id=wx.ID_OK)

		# ######
		#
		# ######
		addremoveButtonsSizer.Add(addButton)
		addremoveButtonsSizer.Add(removeButton)
		flexGridSizer.AddMany([
		(idLabel), (idTextControl, 1, wx.EXPAND),
			(elementsLabel), (self.listBox, 1, wx.ALL|wx.EXPAND),
			(emptyLabel), (addremoveButtonsSizer, 1, wx.EXPAND),
			(emptyLabel), (okButton, 1, wx.ALL)
		])

		flexGridSizer.AddGrowableRow(2, 1)
		flexGridSizer.AddGrowableCol(1, 1)
		
		
		
		sizer.Add(flexGridSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

		# ######
		# EVENTS
		# ######
		addButton.Bind(wx.EVT_BUTTON, self.OnAdd)
		okButton.Bind(wx.EVT_BUTTON, self.OnValid)

		self.SetSizer(sizer)
		
		
	def OnAdd(self, event):	
		wordEditDialog = WordEditDialog(self)
		res = wordEditDialog.ShowModal()
		if res == wx.ID_OK:
			a= wordEditDialog.listBox.GetString(wordEditDialog.listBox.GetSelection())
			b= wordEditDialog.textControl.GetValue()
			index = self.listBox.InsertStringItem(sys.maxint,a)
			self.listBox.SetStringItem(index, 1,b)
			self.listBox.SetStringItem(index, 2,str(wordEditDialog.checkBox.GetValue()))
		wordEditDialog.Destroy()

	def OnValid(self, event):
		print event

