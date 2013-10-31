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
        
        #Feature - Point Setup
        #{
        #Geocoder Setup
        self.AppId_Yahoo = 'xAlMKR7V34F7nB3NRrV4sb3KAh8CvdnjCmigr.5.NhU3vAmynIIUzI_fxef7kJLbG3jEGQ'
        
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
        self.QMT_PtTarget = ""
        self.QMT_EmitPt = QgsMapToolEmitPoint(self.mapCanvas)
        self.connect(self.ui.GoToGetCoorFromMapCanvasMode_pushButton, SIGNAL("clicked()"), self.Pt_GoToGetCoorFromMapCanvasMode)
        self.connect(self.QMT_EmitPt, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.GetCoorFromMapCanvas)
        
        #Result List View Setup
        self.connect(self.ui.Result_listWidget, SIGNAL("itemDoubleClicked (QListWidgetItem *)"), self.ZoomToResultItem)
        
        #}
        
        #Feature - Distance Setup
        #DistFomula_comboBox
        self.ui.DistFomula_comboBox.addItems(["Great Circle", "Vincenty"])
        self.ui.DistFomula_comboBox.setCurrentIndex(0)
        
        #VctElliModel_comboBox
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        from GeoSearch.geopy import distance
        sys.path.remove(os.path.dirname(os.path.realpath(__file__)))        
        
        self.VctElliModelNameList = []
        DefaultVEM_CbIdx = 0
        
        for key, content in distance.ELLIPSOIDS.iteritems():
            self.VctElliModelNameList.append(key)
            
            if key == "WGS-84":
                DefaultVEM_CbIdx = len(self.VctElliModelNameList) - 1
        
        self.ui.VctElliModel_comboBox.addItems(self.VctElliModelNameList)
        self.ui.VctElliModel_comboBox.setCurrentIndex(DefaultVEM_CbIdx)
        
        
        #Pt A & B: Emit Point Tool
        self.connect(self.ui.Dist_PtA_GoToGetCoorFromMapCanvasMode_pushButton, SIGNAL("clicked()"), self.Dist_PtA_GoToGetCoorFromMapCanvasMode)
        self.connect(self.ui.Dist_PtB_GoToGetCoorFromMapCanvasMode_pushButton, SIGNAL("clicked()"), self.Dist_PtB_GoToGetCoorFromMapCanvasMode)

        
        #DistUnit_comboBox
        self.ui.DistUnit_comboBox.addItems(["kilometers", "meters", "miles", "feet", "nautical"])
        self.ui.DistUnit_comboBox.setCurrentIndex(0)
        
        self.connect(self.ui.DistUnit_comboBox, SIGNAL("currentIndexChanged (int)"), self.DistUnit_cB_CurrIdxChanged)
        
        #Calculate button
        self.connect(self.ui.CalculateDist_pushButton, SIGNAL("clicked()"), self.CalculateDist_ButtonHandler)
        
        
    def __del__(self):
        self.closeEvent(None)
        
        
    def closeEvent(self, event):  
        self.RubberBand.reset(False)
        self.mapCanvas.clear()
        self.mapCanvas.refresh()
        self.close()
        
   
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
        #    geocoder = geocoders.Yahoo(self.AppId_Yahoo)
 
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
        result = geocoder.geocode(Addr, exactly_one = exactly_one)
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
    
    
    def Pt_GoToGetCoorFromMapCanvasMode(self):
        self.GoToGetCoorFromMapCanvasMode("Pt")
    
    
    def GoToGetCoorFromMapCanvasMode(self, QMT_PtTarget):
        self.QMT_PtTarget = QMT_PtTarget
        self.hide()
        self.mapCanvas.setMapTool(self.QMT_EmitPt)
   
        
    def GetCoorFromMapCanvas(self, pt, mButton):
        self.mapCanvas.unsetMapTool(self.QMT_EmitPt)
        pt_WGS84 = pointToWGS84(pt, self.mapCanvas.mapRenderer().destinationCrs())
        
        self.show()
        
        if self.QMT_PtTarget == "Pt":
            self.Pt_GetCoorFromMapCanvas(pt_WGS84)
        
        elif self.QMT_PtTarget == "Dist_PtA":
            self.Dist_PtA_GetCoorFromMapCanvas(pt_WGS84)
            
        elif self.QMT_PtTarget == "Dist_PtB":
            self.Dist_PtB_GetCoorFromMapCanvas(pt_WGS84)
        
    
    def Pt_GetCoorFromMapCanvas(self, pt_WGS84):
        self.ui.Latitude_lineEdit.setText(str(pt_WGS84.y()))
        self.ui.Longitude_lineEdit.setText(str(pt_WGS84.x()))
        self.SearchByPt_ButtonHandler()
        
    
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
		
        #elif geocoder_type == "Yahoo!":
        #    geocoder = geocoders.Yahoo(self.AppId_Yahoo)
        
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
            Fet_Gs.setAttributes([place])

            #Vl_Gs.addFeatures([Fet_Gs])
            dP_Gs.addFeatures([Fet_Gs])
            #QMessageBox.information(None, "Error", str(Fet_Gs.geometry().asPoint()))
        
        Vl_Gs.updateExtents()
        
        
        #Get the feature id of the vector layer
        FetSet = Vl_Gs.getFeatures()

        for feat in FetSet:
            FetIdList.append(feat.id())

        #QMessageBox.information(None, "Error", str(feat.id()))

        #Refresh the MapCanvas
        self.mapCanvas.refresh()
        
        
        #Zoom to Search Results
        #Vl_Gs.removeSelection()
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
            
        Vl_Gs.removeSelection()
        Vl_Gs.setSelectedFeatures([self.ui.Result_listWidget.currentRow() + 1])
        self.mapCanvas.zoomToSelected(Vl_Gs)   
        
        #QMessageBox.information(None, "Error", str(item.text()))
   
   
    #Distance
    def Dist_PtA_GoToGetCoorFromMapCanvasMode(self):
        self.GoToGetCoorFromMapCanvasMode("Dist_PtA")
        
        
    def Dist_PtA_GetCoorFromMapCanvas(self, pt_WGS84):
        self.ui.Dist_PtA_Latitude_lineEdit.setText(str(pt_WGS84.y()))
        self.ui.Dist_PtA_Longitude_lineEdit.setText(str(pt_WGS84.x()))
    
    
    def Dist_PtB_GoToGetCoorFromMapCanvasMode(self):
        self.GoToGetCoorFromMapCanvasMode("Dist_PtB")
        
        
    def Dist_PtB_GetCoorFromMapCanvas(self, pt_WGS84):
        self.ui.Dist_PtB_Latitude_lineEdit.setText(str(pt_WGS84.y()))
        self.ui.Dist_PtB_Longitude_lineEdit.setText(str(pt_WGS84.x()))
        
        
    def CalculateDist_ButtonHandler(self):
        PtA = (str(self.ui.Dist_PtA_Latitude_lineEdit.text()), str(self.ui.Dist_PtA_Longitude_lineEdit.text()))
        PtB = (str(self.ui.Dist_PtB_Latitude_lineEdit.text()), str(self.ui.Dist_PtB_Longitude_lineEdit.text()))
        
        self.PtA = PtA
        self.PtB = PtB
        
        self.Dist = self.CalculateDist(PtA, PtB, self.ui.DistFomula_comboBox.currentText(), self.ui.VctElliModel_comboBox.currentText())
        self.UpdateDistAtDistUnit(self.Dist)
        
    
    def CalculateDist(self, PtA, PtB, DistFormula, VctElliModel):
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        from GeoSearch.geopy import distance
        sys.path.remove(os.path.dirname(os.path.realpath(__file__)))
        
        
        #Set Distance Formula
        if DistFormula == "Great Circle":
            distance.distance = distance.GreatCircleDistance  
		
        elif DistFormula == "Vincenty":
            distance.distance = distance.VincentyDistance
            distance.VincentyDistance.ELLIPSOID = str(VctElliModel)
            
        else:
            return
            
        #Calculate distance
        return distance.distance(PtA, PtB)
    
    
    def UpdateDistAtDistUnit(self, objDist):
        try:
            Dist = str(self.GetDistAtDistUnit(objDist, self.ui.DistUnit_comboBox.currentText()))
            self.ui.Dist_lineEdit.setText(Dist)
            self.CreateVectorLayerGeoSearch_Dist(self.PtA, self.PtB, Dist, self.ui.DistUnit_comboBox.currentText())
            
        except:
            return

        
    def GetDistAtDistUnit(self, Dist, DistUnit):
        if DistUnit == "kilometers":
            return Dist.kilometers
		
        elif DistUnit == "meters":
            return Dist.meters
        
        elif DistUnit == "miles":
            return Dist.miles
        
        elif DistUnit == "feet":
            return Dist.feet        
        
        elif DistUnit == "nautical":
            return Dist.nautical
        
        else:
            return
            
            
    def CreateVectorLayerGeoSearch_Dist(self, PtA, PtB, Dist, DistUnit):
        #Create the vector layer of the result
        mapLayers = QgsMapLayerRegistry.instance().mapLayers()
        
        for (name,layer) in mapLayers.iteritems():
            if layer.type() != QgsVectorLayer.VectorLayer:
                continue
                
            if layer.name() == "GeoSearch_Dist":
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
                break
                
        
        Vl_Gs = QgsVectorLayer("Linestring?crs=epsg:4326&field=Dist:string(50)&index=yes", "GeoSearch_Dist", "memory")
        dP_Gs = Vl_Gs.dataProvider()
        #Vl_Gs.setCrs(self.mapCanvas.mapRenderer().destinationCrs())
        QgsMapLayerRegistry.instance().addMapLayer(Vl_Gs)
        
        #Enable Label
        label = Vl_Gs.label()
        label.setLabelField(QgsLabel.Text, 0)
        Vl_Gs.enableLabels(True)

        #Add the feature
        Fet_Gs = QgsFeature()
        QgsPoint_A = QgsPoint(float(PtA[1]),float(PtA[0]))
        QgsPoint_B = QgsPoint(float(PtB[1]),float(PtB[0]))
        Fet_Gs.setGeometry(QgsGeometry.fromMultiPolyline([[QgsPoint_A, QgsPoint_B]]))
        Fet_Gs.setAttributeMap({0:QVariant(Dist + " " + DistUnit)})
        dP_Gs.addFeatures([Fet_Gs])
        
        Vl_Gs.updateExtents()
        
        #Get the feature id of the vector layer
        FetIdList = []
        feat = QgsFeature()
        Vl_Gs.select(dP_Gs.attributeIndexes())

        while Vl_Gs.nextFeature(feat):
            FetIdList.append(feat.id())

        #QMessageBox.information(None, "Error", str(feat.id()))

        #Symbol Setup
        #{
        SymLyrReg = QgsSymbolLayerV2Registry.instance()
        MarkerLineMeta = SymLyrReg.symbolLayerMetadata("MarkerLine")
        #SymLyr_ML = MarkerLineMeta.createSymbolLayer({'width': '0.26', 'color': '255,0,0', 'interval': '3', 'rotate': '1', 'placement': 'interval', 'offset': '-1.0'})
        SymLyr_ML = MarkerLineMeta.createSymbolLayer({})
        ML_Symbol = QgsSymbolV2.defaultSymbol(Vl_Gs.geometryType())
        ML_Symbol.setColor(QColor(255, 0, 0)) #red
        
        #SubSymbol Setup
        #{
        ML_SubSym = SymLyr_ML.subSymbol()
        ML_SubSym.deleteSymbolLayer(0)
        #SymLyr_F_AH = SymLyrReg.symbolLayerMetadata("SimpleMarker").createSymbolLayer({'name': 'filled_arrowhead', 'color': '255,0,0', 'color_border': '0,0,0', 'offset': '0,0', 'size': '1.5', 'angle': '0'})
        SymLyr_F_AH = SymLyrReg.symbolLayerMetadata("SimpleMarker").createSymbolLayer({'name': 'filled_arrowhead'})
        ML_SubSym.appendSymbolLayer(SymLyr_F_AH)
        ML_SubSym.setColor(QColor(255, 0, 0)) #red
        #}
        
        ML_Symbol.deleteSymbolLayer(0)
        ML_Symbol.appendSymbolLayer(SymLyr_ML)
        
        ML_SymRdrr = QgsSingleSymbolRendererV2(ML_Symbol)
        Vl_Gs.setRendererV2(ML_SymRdrr)
        #}
        
        
        #Refresh the MapCanvas
        self.mapCanvas.refresh()
        
        #Zoom to Search Results
        #Vl_Gs.removeSelection()
        Vl_Gs.setSelectedFeatures(FetIdList)
        self.mapCanvas.zoomToSelected(Vl_Gs)
        self.mapCanvas.zoomOut()
    
    
    def DistUnit_cB_CurrIdxChanged(self, CurrIdx):
        try:
            self.UpdateDistAtDistUnit(self.Dist)
       
        except:
            return
            
    
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