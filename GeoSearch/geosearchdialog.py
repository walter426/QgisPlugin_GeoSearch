# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoSearchDialog
                                 A QGIS plugin
 Search location by words like google map
                             -------------------
        begin                : 2013-07-10
        copyright            : (C) 2013 by Walter Tsui
        email                : waltertech426@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from ui_geosearch import Ui_GeoSearch

# create the dialog for zoom to point
# Make sure geopy is imported from current path, and then remove the path after imported
import sys, os


class GeoSearchDialog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_GeoSearch()
        self.ui.setupUi(self)
        
        self.iface = iface
        
        #mapCanvas setup
        self.mapCanvas = self.iface.mapCanvas()
        self.RubberBand = QgsRubberBand(self.mapCanvas, False)
        
        
        #Search By Address Setup
        #self.ui.Geocoder_Addr_comboBox.addItems(["GoogleV3", "Yahoo!", "geocoder.us", "GeoNames", "MediaWiki", "Semantic MediaWiki", "Bing", "OpenMapQuest", "MapQuest"])
        self.ui.Geocoder_Addr_comboBox.addItems(["GoogleV3", "geocoder.us", "GeoNames", "MediaWiki", "Semantic MediaWiki", "OpenMapQuest", "MapQuest"])
        self.ui.Geocoder_Addr_comboBox.setCurrentIndex(0)
        
        self.ui.Addr_lineEdit.setFocus()
        self.connect(self.ui.SearchByAddr_pushButton, SIGNAL("clicked()"), self.SearchByAddr_ButtonHandler)
        
        
        #Search By Point Setup
        self.ui.Geocoder_Pt_comboBox.addItems(["GoogleV3"])
        self.ui.Geocoder_Pt_comboBox.setCurrentIndex(0)
        
        self.connect(self.ui.SearchByPt_pushButton, SIGNAL("clicked()"), self.SearchByPt_ButtonHandler)
        
        #Emit Point Tool
        self.QMT_EmitPt = QgsMapToolEmitPoint(self.mapCanvas)
        self.connect(self.ui.GoToGetCoordinateFromMapCanvasMode_pushButton, SIGNAL("clicked()"), self.GoToGetCoordinateFromMapCanvasMode)
        self.connect(self.QMT_EmitPt, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.GetCoordinateFromMapCanvas)

        
        #Result List View Setup
        self.connect(self.ui.Result_listWidget, SIGNAL("itemDoubleClicked (QListWidgetItem *)"), self.ZoomToResultItem)

    
    def __del__(self):
        self.closeEvent(None)
        
    def closeEvent(self, event):  
        self.RubberBand.reset(False)
        self.mapCanvas.clear()
        self.mapCanvas.refresh()
        self.close()
        
        
    def GoToGetCoordinateFromMapCanvasMode(self):
        self.hide()
        self.mapCanvas.setMapTool(self.QMT_EmitPt)
   
   
    def GetCoordinateFromMapCanvas(self, pt, mButton):
        self.mapCanvas.unsetMapTool(self.QMT_EmitPt)
        pt_WGS84 = pointToWGS84(pt, self.mapCanvas.mapRenderer().destinationCrs())
        
        self.show()
        self.ui.Latitude_lineEdit.setText(str(pt_WGS84.y()))
        self.ui.Longitude_lineEdit.setText(str(pt_WGS84.x()))
        self.SearchByPt_ButtonHandler()
        
   
    def SearchByAddr_ButtonHandler(self):
        self.ui.SearchStatus_label.setText("Searching......")
        result = self.SearchByAddr(unicode(self.ui.Addr_lineEdit.text()), self.ui.Geocoder_Addr_comboBox.currentText(), self.ui.ExactOneResult_checkBox.isChecked())
        self.ui.SearchStatus_label.setText("Result")
        
        self.UpdateSearchResult(result)
        
        
    def SearchByAddr(self, Addr, geocoder_type, exactly_one = True):
        if len(Addr) <= 0:
            return

        
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        from GeoSearch.geopy import geocoders
        sys.path.remove(os.path.dirname(os.path.realpath(__file__)))        
            
            
        #Search location info
        if geocoder_type == "GoogleV3":
            geocoder = geocoders.GoogleV3()

        #elif geocoder_type == "Yahoo!":
        #    geocoder = geocoders.Yahoo('YOUR_APP_ID_HERE')
 
        elif geocoder_type == "geocoder.us":
            geocoder = geocoders.GeocoderDotUS()  
            
        elif geocoder_type == "GeoNames":
            geocoder = geocoders.GeoNames()  
            
        elif geocoder_type == "MediaWiki":
            geocoder = geocoders.MediaWiki("http://wiki.case.edu/%s")  
        
        elif geocoder_type == "Semantic MediaWiki":
            geocoder = geocoders.SemanticMediaWiki("http://wiki.case.edu/%s", attributes=['Coordinates'], relations=['Located in'])  
        
        #elif geocoder_type == "Bing":
        #    geocoder = geocoders.Bing('YOUR_APP_ID_HERE')  
            
        elif geocoder_type == "OpenMapQuest":
            geocoder = geocoders.OpenMapQuest()  
        
        elif geocoder_type == "MapQuest":
            geocoder = geocoders.MapQuest()  
        
        else:
            return
        

        result = []
       
        try:
            result = geocoder.geocode(Addr, exactly_one = exactly_one)
            
        except:
            if len(result) == 0:
                return
        
 
        if isinstance(result, (list, tuple)) == False:
            return
            
        if isinstance(result[0], (list, tuple)) == False:
            result = [result]
        
        
        self.CreateVectorLayerGeoSearch(result)
        
        return result
    
    
    
    def SearchByPt_ButtonHandler(self):
        self.ui.SearchStatus_label.setText("Searching......")
        result = self.SearchByPt(str(self.ui.Latitude_lineEdit.text()), str(self.ui.Longitude_lineEdit.text()), self.ui.Geocoder_Pt_comboBox.currentText(), self.ui.ExactOneResult_checkBox.isChecked())
        self.ui.SearchStatus_label.setText("Result")
        
        self.UpdateSearchResult(result)
        
        
    def SearchByPt(self, lat, lnt, geocoder_type, exactly_one):
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        from GeoSearch.geopy import geocoders
        sys.path.remove(os.path.dirname(os.path.realpath(__file__)))
            
            
        if geocoder_type == "GoogleV3":
            geocoder = geocoders.GoogleV3()

        else:
            return
       
       
        result = []
       
        try:
            point = lat + "," + lnt
            result = geocoder.reverse(point, exactly_one = exactly_one)
            
        except:
            if len(result) == 0:
                return
        
        
        if isinstance(result, (list, tuple)) == False:
            return
            
        if isinstance(result[0], (list, tuple)) == False:
            result = [result]
        
        
        self.CreateVectorLayerGeoSearch(result)
        
        return result
        
        
    def CreateVectorLayerGeoSearch(self, result):
        #Create the vector layer of the result
        mapLayers = QgsMapLayerRegistry.instance().mapLayers()
        
        for (name,layer) in mapLayers.iteritems():
            if layer.type() != QgsVectorLayer.VectorLayer:
                continue
                
            if layer.name() == "GeoSearch":
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
                break
                
        
        Vl_Gs = QgsVectorLayer("Point?crs=epsg:4326&field=Place:string(50)&index=yes", "GeoSearch", "memory")
        dP_Gs = Vl_Gs.dataProvider()
        #Vl_Gs.setCrs(self.mapCanvas.mapRenderer().destinationCrs())
        QgsMapLayerRegistry.instance().addMapLayer(Vl_Gs)
        
        
        # add fields
        #dP_Gs.addAttributes([QgsField(QString("Place"), QVariant.String)])

        #Enable Label
        label = Vl_Gs.label()
        label.setLabelField(QgsLabel.Text, 0)
        Vl_Gs.enableLabels(True)
        
        # add a feature
        FetIdList = []
        
        for LocaInfo in result: 
            place, (lat, lng) = LocaInfo

            Fet_Gs = QgsFeature()
            QgsPoint_F = QgsPoint(float(lng),float(lat))
            Fet_Gs.setGeometry(QgsGeometry.fromPoint(QgsPoint_F))
            #Fet_Gs.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(lng), float(lat))))
            Fet_Gs.setAttributeMap({0:QVariant(place)})
            #Vl_Gs.addFeatures([Fet_Gs])
            dP_Gs.addFeatures([Fet_Gs])
            #QMessageBox.information(None, "Error", str(Fet_Gs.geometry().asPoint()))
        
        Vl_Gs.updateExtents()
        
        
        #Get the feature id of the vector layer
        feat = QgsFeature()
        Vl_Gs.select(dP_Gs.attributeIndexes())

        while Vl_Gs.nextFeature(feat):
            FetIdList.append(feat.id())

        #QMessageBox.information(None, "Error", str(feat.id()))

        #Refresh the MapCanvas
        self.mapCanvas.refresh()
        
        
        #Zoom to Search Results
        #Vl_Gs.removeSelection(False)
        Vl_Gs.setSelectedFeatures(FetIdList)
        self.mapCanvas.zoomToSelected(Vl_Gs)
        #self.mapCanvas.zoomOut()
        
        
    def UpdateSearchResult(self, result):
        self.ui.Result_textEdit.clear()
        self.ui.Result_listWidget.clear()
        
        if isinstance(result, (list, tuple)) == False:
            return
        
        if isinstance(result[0], (list, tuple)) == False:
            result = [result]
        

        for LocaInfo in result:
            self.ui.Result_textEdit.append(str(LocaInfo))
            self.ui.Result_listWidget.addItems([str(LocaInfo)])
            
            
    def ZoomToResultItem(self, item):
        mapLayers = QgsMapLayerRegistry.instance().mapLayers()
        
        DoesVl_GsExist = False
        
        for (name,layer) in mapLayers.iteritems():
            if layer.type() != QgsVectorLayer.VectorLayer:
                continue
                
            if layer.name() == "GeoSearch":
                Vl_Gs = layer
                DoesVl_GsExist = True
                break
                
                
        if DoesVl_GsExist == False:
            return
            
        Vl_Gs.removeSelection(False)
        Vl_Gs.setSelectedFeatures([self.ui.Result_listWidget.currentRow() + 1])
        self.mapCanvas.zoomToSelected(Vl_Gs)   
        
        #QMessageBox.information(None, "Error", str(Type(Vl_Gs)))
        #QMessageBox.information(None, "Error", str(self.ui.Result_listWidget.currentRow()))
        #QMessageBox.information(None, "Error", str(item.text()))


#Modified from GeoCoding\Utils.py
def pointToWGS84(point, crs_src):
    crs_WGS84 = QgsCoordinateReferenceSystem()
    crs_WGS84.createFromSrid(4326)

    transformer = QgsCoordinateTransform(crs_src, crs_WGS84)
    pt = transformer.transform(point)
    
    return pt

def pointFromWGS84(point, crs_des):
    crs_WGS84 = QgsCoordinateReferenceSystem()
    crs_WGS84.createFromSrid(4326)

    transformer = QgsCoordinateTransform(crs_WGS84, crs_des)
    pt = transformer.transform(point)
    
    return pt