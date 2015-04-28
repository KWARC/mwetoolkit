import wx

from libs.Patterns import *
from libs.EitherPattern import *
from libs.SequencePattern import *
from libs.WordPattern import *

class TreeControl(wx.TreeCtrl):
	'''docstring for TreeControl'''
	def __init__(self, *args, **kwargs):
		'''Create the TreeControl.'''
		wx.TreeCtrl.__init__(self, *args, **kwargs)
		self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnShowPopup)

	def OnShowPopup(self, event):
		selectedItemData = self.GetItemData(event.GetItem())
		obj = selectedItemData.GetData()
		options = []

		if isinstance(obj, WordPattern):
			options = ['Delete']
		elif isinstance(obj, SequencePattern):
			options = ['Add sequence pattern', 'Add either pattern', 'Add word pattern', 'Delete']
		elif isinstance(obj, EitherPattern):
			options = ['Add sequence pattern', 'Delete']
		elif isinstance(obj, Patterns):
			options = ['Add sequence pattern']
		elif self.selectedItem == 'patterns':
			options = ['Add sequence']

		self.popupmenu = wx.Menu()

		for option in options:
			item = self.popupmenu.Append(-1, option)
			self.Bind(wx.EVT_MENU, self.OnSelectContext)

		self.PopupMenu(self.popupmenu, event.GetPoint())
		self.popupmenu.Destroy()

	def OnSelectContext(self, event):
		 idselect = event.GetId()
		 itemSelect = self.popupmenu.GetLabelText(idselect)
		 selection = self.GetSelection()

		 if itemSelect == 'Add sequence':
			self.AppendItem(selection, 'pattern', data=wx.TreeItemData(SequencePattern(1)))
		 elif itemSelect == 'Delete':
			self.Delete(selection)
		 elif itemSelect == 'Add either pattern':
			self.AppendItem(selection, 'either', data=wx.TreeItemData(EitherPattern()))
		 elif itemSelect == 'Add word pattern':
			self.AppendItem(selection, 'word', data=wx.TreeItemData(WordPattern(1)))
		 elif itemSelect == 'Add sequence pattern':
			self.AppendItem(selection, 'pattern', data=wx.TreeItemData(SequencePattern(1)))

	def CreateContextMenu(self, menu):
		item = self._menu.Append(wx.ID_ADD)
		self.Bind(wx.EVT_MENU, self.OnSelectContext, item)
		item = self._menu.Append(wx.ID_DELETE)
		self.Bind(wx.EVT_MENU, self.OnSelectContext, item)
		item = self._menu.Append(wx.ID_EDIT)
		self.Bind(wx.EVT_MENU, self.OnSelectContext, item)

class TreePanel(wx.Panel):
	'''docstring for TreePanel'''
	def __init__(self, *args, **kwargs):
		'''Create the TreePanel.'''
		wx.Panel.__init__(self, *args, **kwargs)

		# #####
		# SIZER
		# #####
		sizer = wx.BoxSizer(wx.VERTICAL)

		# ########
		# CONTROLS
		# ########
		self.treeControl = TreeControl(self, 1, style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)

		sizer.Add(self.treeControl, proportion=1,flag=wx.EXPAND)

		self.SetSizer(sizer)