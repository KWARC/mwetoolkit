import wx
import data

from TreePanel import *
from WordPanel import *
from SequencePanel import *

from libs.Patterns import *
from libs.EitherPattern import *
from libs.SequencePattern import *
from libs.WordPattern import *

class MWEFrame(wx.Frame):
	'''docstring for MWEFrame'''
	def __init__(self, *args, **kwargs):
		'''Create the MWEFrame.'''
		wx.Frame.__init__(self, *args, **kwargs)

		data.treePanel = [1,2,3]
		data.sequencePanel = [3,4,5]
		data.wordPanel = [6,7,8]

		# #####
		# SIZER
		# #####
		sizer = wx.BoxSizer(wx.HORIZONTAL)

		# #######
		# MENUBAR
		# #######
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()

		fileMenuItemSaveAsXML = wx.MenuItem(fileMenu, wx.ID_ANY, '&Save as XML\tCtrl+S')
		fileMenuItemQuit = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')

		fileMenu.AppendItem(fileMenuItemSaveAsXML)
		fileMenu.AppendItem(fileMenuItemQuit)

		menubar.Append(fileMenu, '&File')
		self.SetMenuBar(menubar)

		# Create three panels (tree, word edit and sequence edit pattern)
		data.treePanel = TreePanel(self)
		data.wordPanel = WordPanel(self)
		data.sequencePanel = SequencePanel(self)
		self.emptyPanel = wx.Panel(self)
		# We first hide the two edit panels
		data.wordPanel.Hide()
		data.sequencePanel.Hide()
		self.emptyPanel.Show()

		tree = data.treePanel.treeControl

		# Add a root the tree control
		root = tree.AddRoot('patterns', data=wx.TreeItemData(Patterns()))
		# Add a sequence to the root
		sequence = tree.AppendItem(root, 'pattern', data=wx.TreeItemData(SequencePattern(1)))
		either = tree.AppendItem(sequence, 'either', data=wx.TreeItemData(EitherPattern()))
		# Add 3 word pattern to the sequence pattern
		word1 = tree.AppendItem(sequence, 'word', data=wx.TreeItemData(WordPattern(1, positive = {'lemma': ['a']})))
		word2 = tree.AppendItem(sequence, 'word', data=wx.TreeItemData(WordPattern(2, positive = {'lemma': ['b']})))
		word3 = tree.AppendItem(sequence, 'word', data=wx.TreeItemData(WordPattern(3, positive = {'lemma': ['c']})))
		# Add a word pattern to the root
		word4 = tree.AppendItem(root, 'word', data=wx.TreeItemData(WordPattern(4, positive = {'lemma': ['d']})))

		tree.ExpandAll()

		# Add the two panels to the sizer
		sizer.Add(data.treePanel, proportion=1, flag=wx.EXPAND)
		sizer.Add(data.wordPanel, proportion=1, flag=wx.EXPAND)
		sizer.Add(data.sequencePanel, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.emptyPanel, proportion=1, flag=wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(sizer)
		self.Layout()

		# ######
		# EVENTS
		# ######
		# This event is used to switch between panels (WordPanel/SequencePanel)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectedTreeItem, data.treePanel.treeControl)
		self.Bind(wx.EVT_MENU, self.OnQuit, fileMenuItemQuit)
		self.Bind(wx.EVT_MENU, self.OnGenerateXML, fileMenuItemSaveAsXML)

	def OnSelectedTreeItem(self, event):
		tree = data.treePanel.treeControl
		selectedItemData = tree.GetItemData(event.GetItem())
		obj = selectedItemData.GetData()

		if isinstance(obj, WordPattern):
			data.sequencePanel.Hide()
			self.emptyPanel.Hide()
			# Get values from the object and print them on the panel

			data.wordPanel.Show()
		elif isinstance(obj, SequencePattern):
			data.wordPanel.Hide()
			self.emptyPanel.Hide()

			# Get values from the object and print them on the panel
			data.sequencePanel.idTextControl.SetValue(str(obj.id))
			if obj.repeat is None:
				data.sequencePanel.repeatComboBox.SetStringSelection('')
			else:
				data.sequencePanel.repeatComboBox.SetStringSelection(obj.repeat)

			if obj.ignore:
				data.sequencePanel.ignoreTrueRadioButton.SetValue(True)
			else:
				data.sequencePanel.ignoreFalseRadioButton.SetValue(True)

			data.sequencePanel.Show()
		elif isinstance(obj, EitherPattern) or isinstance(obj, Patterns):
			data.wordPanel.Hide()
			data.sequencePanel.Hide()
			self.emptyPanel.Show()
		self.Layout()

	def OnQuit(self, event):
		self.Close()

	def OnGenerateXML(self, event):
		saveFileDialog = wx.FileDialog(self, 'Save XML file', '~', 'pattern.xml', 'XML files (*.xml)|*.xml', wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

		if saveFileDialog.ShowModal() == wx.ID_CANCEL:
			return

		# Save the current contents in the file
		# this can be done with e.g. wxPython output streams:
		output_stream = wx.FileOutputStream(saveFileDialog.GetPath())

		if not output_stream.IsOk():
			wx.LogError("Cannot save current contents in file '%s'."%saveFileDialog.GetPath())
			return