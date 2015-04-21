import wx

from TreePanel import *
from WordPanel import *
from SequencePanel import *

class MWEFrame(wx.Frame):
	'''docstring for MWEFrame'''
	def __init__(self, *args, **kwargs):
		'''Create the MWEFrame.'''
		wx.Frame.__init__(self, *args, **kwargs)

		# #####
		# SIZER
		# #####
		sizer = wx.BoxSizer(wx.HORIZONTAL)

		# Create three panels (tree, word edit and sequence edit pattern)
		self.treePanel = TreePanel(self)
		self.wordPanel = WordPanel(self)
		self.sequencePanel = SequencePanel(self)
		# We first hide the two edit panels
		self.wordPanel.Hide()
		self.sequencePanel.Hide()

		# Add a root the tree control
		root = self.treePanel.treeControl.AddRoot('patterns')
		# Add a sequence to the root
		sequence = self.treePanel.treeControl.AppendItem(root, 'sequence')
		either = self.treePanel.treeControl.AppendItem(sequence, 'either')
		# Add 3 word pattern to the sequence pattern
		word1 = self.treePanel.treeControl.AppendItem(sequence, 'word')
		word2 = self.treePanel.treeControl.AppendItem(sequence, 'word')
		word3 = self.treePanel.treeControl.AppendItem(sequence, 'word')
		# Add a word pattern to the root
		word4 = self.treePanel.treeControl.AppendItem(root, 'word')

		self.treePanel.treeControl.ExpandAll()

		# Add the two panels to the sizer
		sizer.Add(self.treePanel, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.wordPanel, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.sequencePanel, proportion=1, flag=wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(sizer)
		self.Layout()

		# ######
		# EVENTS
		# ######
		# This event is used to switch between panels (WordPanel/SequencePanel)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectedTreeItem, self.treePanel.treeControl)

	def OnSelectedTreeItem(self, event):
		selectedItem = self.treePanel.treeControl.GetItemText(event.GetItem())
		if selectedItem == 'word':
			self.sequencePanel.Hide()
			self.wordPanel.Show()
		elif selectedItem == 'sequence':
			self.wordPanel.Hide()
			self.sequencePanel.Show()
		elif selectedItem == 'either':
			self.wordPanel.Hide()
			self.sequencePanel.Hide()
		self.Layout()