import wx

class TreeControl(wx.TreeCtrl):
	'''docstring for TreeControl'''
	def __init__(self, *args, **kwargs):
		'''Create the TreeControl.'''
		wx.TreeCtrl.__init__(self, *args, **kwargs)
		self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnShowPopup)
		

	def OnShowPopup(self, event):
		self.selectedItem = self.GetItemText(event.GetItem())
		options = []		
		if self.selectedItem == 'word':
			options = ['Delete']
		elif self.selectedItem == 'sequence':
			options = ['Add sequence pattern', 'Add either pattern', 'Add word pattern', 'Delete']
		elif self.selectedItem == 'either':
			options = ['Add sequence pattern', 'Delete']
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
		 if itemSelect == 'Add sequence':
			self.AppendItem(self.GetSelection(),'sequence')
			self.ExpandAll()
		 elif itemSelect == 'Delete':
			self.Delete(self.GetSelection())
		 elif itemSelect == 'Add either pattern':
			self.AppendItem(self.GetSelection(),'either')
		 elif itemSelect == 'Add word pattern':
			self.AppendItem(self.GetSelection(),'word')
		 elif itemSelect == 'Add sequence pattern':
			self.AppendItem(self.GetSelection(),'sequence')

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


	def addRoot(self, text):
		return self.treeControl.AddRoot(text)

	def addItem(self, parent, text):
		return self.treeControl.AppendItem(parent, text)
