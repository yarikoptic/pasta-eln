""" widget that shows the table of the items """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel   # pylint: disable=no-name-in-module
from PySide6.QtCore import Slot               # pylint: disable=no-name-in-module

class Table(QWidget):
  """ widget that shows the table of the items """
  def __init__(self, comm):
    """
    Initialization

    Args:
      comm (Communicate): communication channel
    """
    super().__init__()
    self.comm = comm
    comm.changeTable.connect(self.changeTable)
    self.data = []

    # GUI stuff
    mainL = QVBoxLayout()
    headerW = QWidget()
    headerL = QHBoxLayout(headerW)
    self.headline = QLabel()  #TODO could become style
    self.headline.setStyleSheet('font-size: 14pt')
    headerL.addWidget(self.headline)
    mainL.addWidget(headerW)
    self.table = QTableWidget(self)
    self.table.cellClicked.connect(self.cellClicked)
    self.table.setSortingEnabled(True)
    self.table.setAlternatingRowColors(True)
    mainL.addWidget(self.table)
    self.setLayout(mainL)


  @Slot(str)
  def changeTable(self, docType, projID):
    """
    What happens when the table should change should change

    Args:
      docType (str): document type
      projID (str): id of project
    """
    if projID=='':
      self.data = self.comm.backend.db.getView('viewDocType/'+docType)
    else:
      self.data = self.comm.backend.db.getView('viewDocType/'+docType, preciseKey=projID)
    if len(self.data)==0:
      self.table.hide()
      return
    self.headline.setText(self.comm.backend.dataLabels[docType])
    nrows, ncols = len(self.data), len(self.data[0]['value'])
    self.table.setColumnCount(ncols)
    header = self.comm.backend.db.ontology[docType]
    header = [i['name'][1:] if i['name'][0]=='-' else i['name'] for i in header]
    self.table.setHorizontalHeaderLabels(header)
    self.table.verticalHeader().hide()
    self.table.setRowCount(nrows)
    for i in range(nrows):
      for j in range(ncols):
        item = QTableWidgetItem(str(self.data[i]['value'][j]))
        self.table.setItem(i, j, item)
    self.table.show()
    return


  def cellClicked(self, row, column):
    """
    What happens when user clicks cell in table

    Args:
      row (int): row number
      column (int): column number
    """
    # print("Row, column", row, column)
    #change details
    # if column==0:
    self.comm.changeDetails.emit(self.data[row]['id'])
    return
