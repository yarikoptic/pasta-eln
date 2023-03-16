""" Custom tree view on data model """
from PySide6.QtWidgets import QTreeView, QAbstractItemView, QMenu # pylint: disable=no-name-in-module
from PySide6.QtGui import QAction                                 # pylint: disable=no-name-in-module
from .widgetProjectLeafRenderer import ProjectLeafRenderer
from .style import Action

class TreeView(QTreeView):
  """ Custom tree view on data model """
  def __init__(self, parent, comm, model):
    super().__init__(parent)
    self.comm = comm
    self.setModel(model)
    self.setHeaderHidden(True)
    self.setStyleSheet('QTreeView::branch {border-image: none;}')
    self.renderer = ProjectLeafRenderer()
    self.renderer.setCommunication(self.comm)
    self.setItemDelegate(self.renderer)
    self.setDragDropMode(QAbstractItemView.InternalMove)
    self.doubleClicked.connect(self.treeDoubleClicked)

  def contextMenuEvent(self, e):
    """
    create context menu

    Args:
      e (QEvent): event
    """
    context = QMenu(self)
    Action("Add child folder", self.addChild, context, self)
    Action("Add sibling folder", self.addSibling, context, self)
    Action("Remove this", self.remove, context, self)
    context.addSeparator()
    Action("Fold / Unfold", self.fold, context, self)
    Action("Hide", self.hide, context, self)
    context.exec(e.globalPos())

  def treeDoubleClicked(self):
    """ after double-click on tree leaf: open form """
    docID = self.currentIndex().data()
    self.comm.formDoc.emit(self.comm.backend.db.getDoc(docID))
    return

  def addChild(self):
    """ after selecting add child from context menu """
    docID = self.currentIndex().data()
    print('clicked context menu addChild', docID )

  def addSibling(self):
    """ after selecting add sibling from context menu """
    docID = self.currentIndex().data()
    print('clicked context menu addSibling', docID)

  def remove(self):
    """ after selecting remove from context menu """
    docID = self.currentIndex().data()
    print('clicked context menu remove', docID)

  def fold(self):
    """ after selecting fold from context menu """
    docID = self.currentIndex().data()
    print('clicked context menu fold', docID)

  def hide(self):
    """ after selecting hide from context menu """
    docID = self.currentIndex().data()
    print('clicked context menu hide', docID)
