import wx
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
		elementsLabel = wx.StaticText(self, label='elements')
		emptyLabel = wx.StaticText(self, label='')

		# ########
		# CONTROLS
		# ########
		# List box containing values
		listBox = wx.ListBox(self, style=wx.LB_SINGLE)
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
			(elementsLabel), (listBox, 1, wx.ALL|wx.EXPAND),
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
		wordEditDialog = WordEditDialog(None)
		wordEditDialog.ShowModal()
		wordEditDialog.Destroy()

	def OnValid(self, event):
		print event