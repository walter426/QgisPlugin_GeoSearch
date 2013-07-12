# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui_geosearch.ui'
#
# Created: Fri Jul 12 10:17:04 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_GeoSearch(object):
    def setupUi(self, GeoSearch):
        GeoSearch.setObjectName(_fromUtf8("GeoSearch"))
        GeoSearch.resize(512, 413)
        self.Latitude_lineEdit = QtGui.QLineEdit(GeoSearch)
        self.Latitude_lineEdit.setGeometry(QtCore.QRect(170, 90, 113, 20))
        self.Latitude_lineEdit.setObjectName(_fromUtf8("Latitude_lineEdit"))
        self.latitude_label = QtGui.QLabel(GeoSearch)
        self.latitude_label.setGeometry(QtCore.QRect(200, 70, 46, 13))
        self.latitude_label.setObjectName(_fromUtf8("latitude_label"))
        self.Longitude_lineEdit = QtGui.QLineEdit(GeoSearch)
        self.Longitude_lineEdit.setGeometry(QtCore.QRect(290, 90, 113, 20))
        self.Longitude_lineEdit.setObjectName(_fromUtf8("Longitude_lineEdit"))
        self.Longitude_label = QtGui.QLabel(GeoSearch)
        self.Longitude_label.setGeometry(QtCore.QRect(320, 70, 46, 13))
        self.Longitude_label.setObjectName(_fromUtf8("Longitude_label"))
        self.Addr_lineEdit = QtGui.QLineEdit(GeoSearch)
        self.Addr_lineEdit.setGeometry(QtCore.QRect(172, 40, 231, 20))
        self.Addr_lineEdit.setObjectName(_fromUtf8("Addr_lineEdit"))
        self.Address_label = QtGui.QLabel(GeoSearch)
        self.Address_label.setGeometry(QtCore.QRect(260, 20, 46, 13))
        self.Address_label.setObjectName(_fromUtf8("Address_label"))
        self.SearchByAddr_pushButton = QtGui.QPushButton(GeoSearch)
        self.SearchByAddr_pushButton.setGeometry(QtCore.QRect(420, 40, 75, 23))
        self.SearchByAddr_pushButton.setObjectName(_fromUtf8("SearchByAddr_pushButton"))
        self.SearchByPt_pushButton = QtGui.QPushButton(GeoSearch)
        self.SearchByPt_pushButton.setGeometry(QtCore.QRect(420, 90, 75, 23))
        self.SearchByPt_pushButton.setObjectName(_fromUtf8("SearchByPt_pushButton"))
        self.Geocoder_Addr_comboBox = QtGui.QComboBox(GeoSearch)
        self.Geocoder_Addr_comboBox.setGeometry(QtCore.QRect(20, 40, 141, 22))
        self.Geocoder_Addr_comboBox.setObjectName(_fromUtf8("Geocoder_Addr_comboBox"))
        self.Geocoder_Addr_label = QtGui.QLabel(GeoSearch)
        self.Geocoder_Addr_label.setGeometry(QtCore.QRect(60, 20, 46, 13))
        self.Geocoder_Addr_label.setObjectName(_fromUtf8("Geocoder_Addr_label"))
        self.Geocoder_Addr_label_2 = QtGui.QLabel(GeoSearch)
        self.Geocoder_Addr_label_2.setGeometry(QtCore.QRect(60, 70, 46, 13))
        self.Geocoder_Addr_label_2.setObjectName(_fromUtf8("Geocoder_Addr_label_2"))
        self.Geocoder_Pt_comboBox = QtGui.QComboBox(GeoSearch)
        self.Geocoder_Pt_comboBox.setGeometry(QtCore.QRect(20, 90, 141, 22))
        self.Geocoder_Pt_comboBox.setObjectName(_fromUtf8("Geocoder_Pt_comboBox"))
        self.ExactOneResult_checkBox = QtGui.QCheckBox(GeoSearch)
        self.ExactOneResult_checkBox.setGeometry(QtCore.QRect(380, 120, 111, 17))
        self.ExactOneResult_checkBox.setChecked(True)
        self.ExactOneResult_checkBox.setObjectName(_fromUtf8("ExactOneResult_checkBox"))
        self.Result_tabWidget = QtGui.QTabWidget(GeoSearch)
        self.Result_tabWidget.setGeometry(QtCore.QRect(20, 130, 471, 261))
        self.Result_tabWidget.setObjectName(_fromUtf8("Result_tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.Result_List_label = QtGui.QLabel(self.tab)
        self.Result_List_label.setGeometry(QtCore.QRect(10, 20, 171, 16))
        self.Result_List_label.setObjectName(_fromUtf8("Result_List_label"))
        self.Result_listWidget = QtGui.QListWidget(self.tab)
        self.Result_listWidget.setGeometry(QtCore.QRect(10, 40, 441, 192))
        self.Result_listWidget.setObjectName(_fromUtf8("Result_listWidget"))
        self.Result_tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.Result_textEdit = QtGui.QTextEdit(self.tab_2)
        self.Result_textEdit.setGeometry(QtCore.QRect(10, 30, 441, 191))
        self.Result_textEdit.setObjectName(_fromUtf8("Result_textEdit"))
        self.Result_List_label_2 = QtGui.QLabel(self.tab_2)
        self.Result_List_label_2.setGeometry(QtCore.QRect(10, 10, 141, 16))
        self.Result_List_label_2.setObjectName(_fromUtf8("Result_List_label_2"))
        self.Result_tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.SearchStatus_label = QtGui.QLabel(GeoSearch)
        self.SearchStatus_label.setGeometry(QtCore.QRect(220, 120, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.SearchStatus_label.setFont(font)
        self.SearchStatus_label.setObjectName(_fromUtf8("SearchStatus_label"))

        self.retranslateUi(GeoSearch)
        self.Result_tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GeoSearch)

    def retranslateUi(self, GeoSearch):
        GeoSearch.setWindowTitle(QtGui.QApplication.translate("GeoSearch", "GeoSearch", None, QtGui.QApplication.UnicodeUTF8))
        self.latitude_label.setText(QtGui.QApplication.translate("GeoSearch", "Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.Longitude_label.setText(QtGui.QApplication.translate("GeoSearch", "Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.Address_label.setText(QtGui.QApplication.translate("GeoSearch", "Address", None, QtGui.QApplication.UnicodeUTF8))
        self.SearchByAddr_pushButton.setText(QtGui.QApplication.translate("GeoSearch", "Search ", None, QtGui.QApplication.UnicodeUTF8))
        self.SearchByPt_pushButton.setText(QtGui.QApplication.translate("GeoSearch", "Search ", None, QtGui.QApplication.UnicodeUTF8))
        self.Geocoder_Addr_label.setText(QtGui.QApplication.translate("GeoSearch", "Geocoder", None, QtGui.QApplication.UnicodeUTF8))
        self.Geocoder_Addr_label_2.setText(QtGui.QApplication.translate("GeoSearch", "Geocoder", None, QtGui.QApplication.UnicodeUTF8))
        self.ExactOneResult_checkBox.setText(QtGui.QApplication.translate("GeoSearch", "Exact One Result", None, QtGui.QApplication.UnicodeUTF8))
        self.Result_List_label.setText(QtGui.QApplication.translate("GeoSearch", "Double Click below items to zoom in", None, QtGui.QApplication.UnicodeUTF8))
        self.Result_tabWidget.setTabText(self.Result_tabWidget.indexOf(self.tab), QtGui.QApplication.translate("GeoSearch", "List", None, QtGui.QApplication.UnicodeUTF8))
        self.Result_List_label_2.setText(QtGui.QApplication.translate("GeoSearch", "For direct copy", None, QtGui.QApplication.UnicodeUTF8))
        self.Result_tabWidget.setTabText(self.Result_tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("GeoSearch", "Text", None, QtGui.QApplication.UnicodeUTF8))
        self.SearchStatus_label.setText(QtGui.QApplication.translate("GeoSearch", "Result", None, QtGui.QApplication.UnicodeUTF8))

