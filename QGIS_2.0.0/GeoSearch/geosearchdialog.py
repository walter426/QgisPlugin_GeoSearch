# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoSearchDialog
								 A QGIS plugin
 Search location by words like google map
							 -------------------
		begin				: 2013-07-10
		copyright			: (C) 2013 by Walter Tsui
		email				: waltertech426@gmail.com
 ***************************************************************************/

/***************************************************************************
 *																		 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or	 *
 *   (at your option) any later version.								   *
 *																		 *
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
import math


class GeoSearchDialog(QtGui.QDialog):
	def __init__(self, iface):
		QtGui.QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.ui = Ui_GeoSearch()
		self.ui.setupUi(self)
		
		self.iface = iface
		self.legend = self.iface.legendInterface()
		
		#mapCanvas setup
		self.mapCanvas = self.iface.mapCanvas()
		self.RubberBand = QgsRubberBand(self.mapCanvas, False)
		
		#Feature Setup - Point
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
		
		#Search Preference
		self.connect(self.ui.ObtainElevation_checkBox, SIGNAL("stateChanged (int)"), self.ObtainElevationStateUpdate)
		
		#Result List View Setup
		self.connect(self.ui.Result_listWidget, SIGNAL("itemDoubleClicked (QListWidgetItem *)"), self.ZoomToResultItem)
		
		#}
		
		#Feature Setup - Distance
		#{
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

		#Calculate button
		self.connect(self.ui.CalculateDist_pushButton, SIGNAL("clicked()"), self.CalculateDist_ButtonHandler)
		#}
		
		
		#DistUnit_comboBox
		self.ui.DistUnit_comboBox.addItems(["kilometers", "meters", "miles", "feet", "nautical"])
		self.ui.DistUnit_comboBox.setCurrentIndex(0)
		
		self.connect(self.ui.DistUnit_comboBox, SIGNAL("currentIndexChanged (int)"), self.DistUnit_cB_CurrIdxChanged)
		
		
		#BearingUnit_comboBox
		self.ui.BearingUnit_comboBox.addItems(["degree", "radian"])
		self.ui.BearingUnit_comboBox.setCurrentIndex(0)
		
		self.connect(self.ui.BearingUnit_comboBox, SIGNAL("currentIndexChanged (int)"), self.BearingUnit_cB_CurrIdxChanged)
		self.connect(self.ui.BearingIsPositiveOnly_checkBox, SIGNAL("clicked()"), self.BearingIsPositiveOnly_checkBox_clicked)

		
		#Feature Setup - Route
		#{
		self.ui.Route_TravelMode_comboBox.addItems(["driving", "walking", "bicycling", "transit"])
		self.ui.Route_Avoid_comboBox.addItems(["none", "tolls", "highways"])
		self.ui.Route_DistUnit_comboBox.addItems(["metric", "imperial"])
		
		self.connect(self.ui.Route_GoToGetCoorFromMapCanvasMode_pushButton, SIGNAL("clicked()"), self.Route_GoToGetCoorFromMapCanvasMode)
		self.connect(self.ui.SearchRoute_pushButton, SIGNAL("clicked()"), self.SearchRoute_ButtonHandler)

		#}
		
	def __del__(self):
		self.closeEvent(None)
		
		
	def closeEvent(self, event):  
		self.RubberBand.reset(False)
		self.mapCanvas.clear()
		self.mapCanvas.refresh()
		self.close()
	
	
	def ObtainElevationStateUpdate(self, state):
		if state == 2:
			self.ui.ResultFmt_label.setText("(Place, (Latitude, Longtitude), (Elevation, Resolution))")
		else:
			self.ui.ResultFmt_label.setText("(Place, (Latitude, Longtitude))")
		
   
	def SearchByAddr_ButtonHandler(self):
		self.ui.SearchStatus_label.setText("Searching......")
		result = self.SearchByAddr(unicode(self.ui.Addr_lineEdit.text()), self.ui.Geocoder_Addr_comboBox.currentText(), self.ui.ExactOneResult_checkBox.isChecked(), self.ui.SearchOnGoogleWebMap_checkBox.isChecked(), self.ui.ObtainElevation_checkBox.isChecked())
		self.ui.SearchStatus_label.setText("Result")
		
		self.UpdateSearchResult(result)
		
		
	def SearchByAddr(self, Addr, geocoder_type, exactly_one = True, SearchOnGoogleWebMap = False, ObtainElevation = False):
		if len(Addr) <= 0:
			return

		if SearchOnGoogleWebMap == True:
			import webbrowser
			webbrowser.open("https://www.google.com/maps/preview#!q=" + Addr)
		
		
		sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
		from GeoSearch.geopy import geocoders
		sys.path.remove(os.path.dirname(os.path.realpath(__file__)))		
			
			
		#Search location info
		if geocoder_type == "GoogleV3":
			#import GoogleMapsApi.geocode
			#geocoder = GoogleMapsApi.geocode.Geocoding()
			geocoder = geocoders.GoogleV3()

		#elif geocoder_type == "Yahoo!":
		#	geocoder = geocoders.Yahoo(self.AppId_Yahoo)
 
		elif geocoder_type == "geocoder.us":
			geocoder = geocoders.GeocoderDotUS()  
			
		elif geocoder_type == "GeoNames":
			geocoder = geocoders.GeoNames()  
			
		elif geocoder_type == "MediaWiki":
			geocoder = geocoders.MediaWiki("http://wiki.case.edu/%s")  
		
		elif geocoder_type == "Semantic MediaWiki":
			geocoder = geocoders.SemanticMediaWiki("http://wiki.case.edu/%s", attributes=['Coordinates'], relations=['Located in'])  
		
		#elif geocoder_type == "Bing":
		#	geocoder = geocoders.Bing('YOUR_APP_ID_HERE')  
			
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
		
		
		#Obtain Elevation
		if ObtainElevation == True:
			self.AppendElevationIntoGeocodeResult(result)
			
		#Create vectorlayer, GeoSearch
		self.CreateVectorLayerGeoSearch(result)
			
		return result
	
	
	def Pt_GoToGetCoorFromMapCanvasMode(self):
		self.GoToGetCoorFromMapCanvasMode("Pt")
	
	
	def GoToGetCoorFromMapCanvasMode(self, QMT_PtTarget):
		self.QMT_PtTarget = QMT_PtTarget
		self.hide()
		self.mapCanvas.setMapTool(self.QMT_EmitPt)
   
		
	def GetCoorFromMapCanvas(self, pt, mButton):
		if self.QMT_PtTarget == "Pt" or self.QMT_PtTarget == "Dist_PtA" or self.QMT_PtTarget == "Dist_PtB":
			pt_WGS84 = pointToWGS84(pt, self.mapCanvas.mapRenderer().destinationCrs())
			self.mapCanvas.unsetMapTool(self.QMT_EmitPt)
			self.show()
			
			if self.QMT_PtTarget == "Pt":
				self.Pt_GetCoorFromMapCanvas(pt_WGS84)
			
			elif self.QMT_PtTarget == "Dist_PtA":
				self.Dist_PtA_GetCoorFromMapCanvas(pt_WGS84)
				
			elif self.QMT_PtTarget == "Dist_PtB":
				self.Dist_PtB_GetCoorFromMapCanvas(pt_WGS84)
		
		
		elif self.QMT_PtTarget == "Route":
			if mButton == Qt.LeftButton:
				self.Route_GetCoorFromMapCanvas(pt)
		
			else:
				self.RubberBand.reset(False)
				self.mapCanvas.clear()
				self.mapCanvas.refresh()
				#del self.QGS_MPT_R
				
				self.mapCanvas.unsetMapTool(self.QMT_EmitPt)
				self.show()
			
		
	def Pt_GetCoorFromMapCanvas(self, pt_WGS84):
		self.ui.Latitude_lineEdit.setText(str(pt_WGS84.y()))
		self.ui.Longitude_lineEdit.setText(str(pt_WGS84.x()))
		self.SearchByPt_ButtonHandler()
		
	
	def SearchByPt_ButtonHandler(self):
		self.ui.SearchStatus_label.setText("Searching......")
		result = self.SearchByPt(str(self.ui.Latitude_lineEdit.text()), str(self.ui.Longitude_lineEdit.text()), self.ui.Geocoder_Pt_comboBox.currentText(), self.ui.ExactOneResult_checkBox.isChecked(), self.ui.SearchOnGoogleWebMap_checkBox.isChecked(), self.ui.ObtainElevation_checkBox.isChecked())
		self.ui.SearchStatus_label.setText("Result")
		
		self.UpdateSearchResult(result)
		
		
	def SearchByPt(self, lat, lnt, geocoder_type, exactly_one, SearchOnGoogleWebMap = False, ObtainElevation = False):
		if SearchOnGoogleWebMap == True:
			import webbrowser
			webbrowser.open("https://www.google.com/maps/@" + lat + "%2C" + lnt + ",15z")
	  
	
		sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
		from GeoSearch.geopy import geocoders
		sys.path.remove(os.path.dirname(os.path.realpath(__file__)))
			
			
		if geocoder_type == "GoogleV3":
			#import GoogleMapsApi.geocode
			#geocoder = GoogleMapsApi.geocode.Geocoding()
			geocoder = geocoders.GoogleV3()
			
		
		#elif geocoder_type == "Yahoo!":
		#	geocoder = geocoders.Yahoo(self.AppId_Yahoo)
		
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
		
		
		#Obtain Elevation
		if ObtainElevation == True:
			self.AppendElevationIntoGeocodeResult(result)
			
		#Create vectorlayer, GeoSearch
		self.CreateVectorLayerGeoSearch(result)
		
		return result
		
	
	def AppendElevationIntoGeocodeResult(self, result):
		LatLngSet = []
			
		for LocaInfo in result: 
			place, (lat, lng) = LocaInfo
			LatLngSet.append([lat, lng])
			
		#import elevation
		import GoogleMapsApi.elevation
		ElevationService = GoogleMapsApi.elevation.Elevation()
		ElevationResult = ElevationService.GetElevation(LatLngSet)
		
		if isinstance(ElevationResult, (list, tuple)) == True:
			for i in range(len(result)):
				place, (lat, lng) = result[i]
				elevation = ElevationResult[i]['elevation']
				resolution = ElevationResult[i]['resolution']
				result[i] = (place, (lat, lng), (elevation, resolution))
				
				
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
		
		if isinstance(result, (list, tuple)) == False:
			return
			
		str_FldSet = "field=Place:string(50)"
		
		if len(result[0]) >= 3:
			str_FldSet = str_FldSet + "&field=Elevation:double&field=Resolution:double"
		
		Vl_Gs = QgsVectorLayer("Point?crs=epsg:4326&" + str_FldSet + "&index=yes", "GeoSearch", "memory")
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
		for LocaInfo in result: 
			place = LocaInfo[0]
			(lat, lng) = LocaInfo[1]

			AttrSet = [place]
			
			if len(LocaInfo) >= 3:
				(elevation, resolution) = LocaInfo[2]
				AttrSet.append(elevation)
				AttrSet.append(resolution)
			
			Fet_Gs = QgsFeature()
			QgsPoint_F = QgsPoint(float(lng),float(lat))
			Fet_Gs.setGeometry(QgsGeometry.fromPoint(QgsPoint_F))
			Fet_Gs.setAttributes(AttrSet)

			#Vl_Gs.addFeatures([Fet_Gs])
			dP_Gs.addFeatures([Fet_Gs])
			#QMessageBox.information(None, "Error", str(Fet_Gs.geometry().asPoint()))
		
		Vl_Gs.updateExtents()
		
		
		#Get the feature id of the vector layer
		FetSet = Vl_Gs.getFeatures()
		FetIdList = []
		
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
		self.Bearing = Bearing(QgsPoint(float(PtA[1]), float(PtA[0])), QgsPoint(float(PtB[1]), float(PtB[0])), 4326)
		self.UpdateDistInfo(self.Dist, self.Bearing)
 
	
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
	
	
	def UpdateDistInfo(self, objDist, objBearing):
		try:
			Dist = str(self.GetDistAtDistUnit(objDist, self.ui.DistUnit_comboBox.currentText()))
			self.ui.Dist_lineEdit.setText(Dist)
			Bearing = str(self.GetBearingAtBearingUnit(objBearing, self.ui.BearingUnit_comboBox.currentText(), self.ui.BearingIsPositiveOnly_checkBox.isChecked()))
			self.ui.Bearing_lineEdit.setText(Bearing)
			self.CreateVectorLayerGeoSearch_Dist(self.PtA, self.PtB, Dist, self.ui.DistUnit_comboBox.currentText(), Bearing)
			
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
			
			
	def GetBearingAtBearingUnit(self, Bearing, BearingUnit, BearingIsPositiveOnly):
		if BearingUnit == "degree":
			angle = Bearing.degree

		elif BearingUnit == "radian":
			angle = Bearing.radian
		
		else:
			return
			
			
		if BearingIsPositiveOnly == True and angle < 0:
			if BearingUnit == "degree":
				angle = 360 + angle

			elif BearingUnit == "radian":
				from math import *
				angle = 2*pi + angle
		
		return angle
			
			
	def CreateVectorLayerGeoSearch_Dist(self, PtA, PtB, Dist, DistUnit, Bearing):
		#Create the vector layer of the result
		mapLayers = QgsMapLayerRegistry.instance().mapLayers()
		
		for (name,layer) in mapLayers.iteritems():
			if layer.type() != QgsVectorLayer.VectorLayer:
				continue
				
			if layer.name() == "GeoSearch_Dist":
				QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
				break
				
		
		Vl_Gs = QgsVectorLayer("Linestring?crs=epsg:4326&field=Dist:string(50)&field=Bearing:double&index=yes", "GeoSearch_Dist", "memory")
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
		#Fet_Gs.setAttributeMap({0:QVariant(Dist + " " + DistUnit)})
		Fet_Gs.setAttributes([Dist + " " + DistUnit, Bearing])
		dP_Gs.addFeatures([Fet_Gs])
		
		Vl_Gs.updateExtents()
		
		#Get the feature id of the vector layer
		FetSet = Vl_Gs.getFeatures()
		FetIdList = []
		
		for feat in FetSet:
			FetIdList.append(feat.id())

		#QMessageBox.information(None, "Error", str(feat.id()))

		#Symbol Setup
		#{  
		self.CreateSymbolRendererV2ForVectorLayerOfLineStr(Vl_Gs, "MarkerLine", "SimpleMarker", "filled_arrowhead", QColor(255, 0, 0))
		#}
		
		#Refresh the MapCanvas
		self.mapCanvas.refresh()
		
		#Zoom to Search Results
		#Vl_Gs.removeSelection()
		Vl_Gs.setSelectedFeatures(FetIdList)
		self.mapCanvas.zoomToSelected(Vl_Gs)
		self.mapCanvas.zoomOut()
	
	
	def CreateSymbolRendererV2ForVectorLayerOfLineStr(self, Vl, LineMeta, MakerMeta, MakerType, Color):
		SymLyrReg = QgsSymbolLayerV2Registry.instance()
		MarkerLineMeta = SymLyrReg.symbolLayerMetadata(LineMeta)
		SymLyr_ML = MarkerLineMeta.createSymbolLayer({})
		ML_Symbol = QgsSymbolV2.defaultSymbol(Vl.geometryType())
		ML_Symbol.setColor(Color) #red
		
		#SubSymbol Setup
		#{
		ML_SubSym = SymLyr_ML.subSymbol()
		ML_SubSym.deleteSymbolLayer(0)
		#SymLyr_F_AH = SymLyrReg.symbolLayerMetadata("SimpleMarker").createSymbolLayer({'name': 'filled_arrowhead', 'color': '255,0,0', 'color_border': '0,0,0', 'offset': '0,0', 'size': '1.5', 'angle': '0'})
		SymLyr_F_AH = SymLyrReg.symbolLayerMetadata(MakerMeta).createSymbolLayer({'name': MakerType})
		ML_SubSym.appendSymbolLayer(SymLyr_F_AH)
		ML_SubSym.setColor(Color) #red
		#}
		
		ML_Symbol.deleteSymbolLayer(0)
		ML_Symbol.appendSymbolLayer(SymLyr_ML)
		
		ML_SymRdrr = QgsSingleSymbolRendererV2(ML_Symbol)
		Vl.setRendererV2(ML_SymRdrr)
		
	
	def DistUnit_cB_CurrIdxChanged(self, CurrIdx):
		try:
			self.UpdateDistInfo(self.Dist, self.Bearing)
	   
		except:
			return
		
		
	def BearingUnit_cB_CurrIdxChanged(self, CurrIdx):
		try:
			self.UpdateDistInfo(self.Dist, self.Bearing)
	   
		except:
			return
			
	def BearingIsPositiveOnly_checkBox_clicked(self):
		try:
			self.UpdateDistInfo(self.Dist, self.Bearing)
	   
		except:
			return
	
	#Route
	def Route_GoToGetCoorFromMapCanvasMode(self):
		self.ui.RoutePoints_textEdit.clear()
		
		self.QGS_MPT_R = QgsGeometry().asMultiPoint()
		
		self.RubberBand.setColor(QColor(255, 0, 0)) #red
		self.RubberBand.setWidth(3)

		self.GoToGetCoorFromMapCanvasMode("Route")
		
	
	def Route_GetCoorFromMapCanvas(self, pt):
		self.QGS_MPT_R.append(QgsPoint(pt))
		self.RubberBand.reset(False)
		self.RubberBand.setToGeometry(QgsGeometry.fromMultiPoint(self.QGS_MPT_R), None)
		self.RubberBand.show()

		self.mapCanvas.clear()
		self.mapCanvas.refresh()
		
		pt_WGS84 = pointToWGS84(pt, self.mapCanvas.mapRenderer().destinationCrs())
		self.ui.RoutePoints_textEdit.append(str(pt_WGS84.y()) + ", " + str(pt_WGS84.x()))
		
	 
	def SearchRoute_ButtonHandler(self):
		#self.ui.Route_SearchStatus_label.setText("Searching......")
		
		RoutePtSet = str(self.ui.RoutePoints_textEdit.toPlainText()).split("\n")
		
		for i in range(len(RoutePtSet)):
			RoutePtSet[i] = RoutePtSet[i].split(",")
			
			for j in range(len(RoutePtSet[i])):
				RoutePtSet[i][j] = RoutePtSet[i][j].strip()
				
		try:		
			result = self.SearchRoute(RoutePtSet, self.ui.Route_TravelMode_comboBox.currentText(), self.ui.Route_Avoid_comboBox.currentText(), self.ui.Route_DistUnit_comboBox.currentText())
		except:
			pass
			
		#self.ui.Route_SearchStatus_label.setText("Result")
		
	
	def SearchRoute(self, RoutePtSet, TravelMode = 'driving', Avoid = None, DistUnit = 'metric'):
		import GoogleMapsApi.directions
		
		if len(RoutePtSet) < 2:
			return
		
		if Avoid == "None":
			Avoid = None
		
		origin = ",".join(RoutePtSet[0])
		destination = ",".join(RoutePtSet[-1])
		waypoints = None
		
		if len(RoutePtSet) >= 3:
			waypoints = []
			
			for i in range(1, len(RoutePtSet) - 1):
				waypoints.append(",".join(RoutePtSet[i]))
				
			waypoints = "|".join(waypoints)

		
		DirectionsService = GoogleMapsApi.directions.Directions()
		results = DirectionsService.GetDirections(origin, destination, mode = TravelMode, waypoints = waypoints, avoid = Avoid, units = DistUnit)
		self.CreateVectorLayerGeoSearch_Route(results)
		
	
	def CreateVectorLayerGeoSearch_Route(self, results):
		#Create the vector layer of the result
		mapLayers = QgsMapLayerRegistry.instance().mapLayers()
		
		for (name,layer) in mapLayers.iteritems():
			if layer.type() != QgsVectorLayer.VectorLayer:
				continue
				
			if layer.name() == "GeoSearch_Route_legs":
				QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

			elif layer.name() == "GeoSearch_Route_steps":
				QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
		
		
		if isinstance(results, (list, tuple)) == False:
			return
		  
		#Create, GeoSearch_Route_legs
		str_FldSet = "field=distance_text:string(50)&field=distance_value:double"
		str_FldSet = str_FldSet + "&field=duration_text:string(50)&field=duration_value:double"
		str_FldSet = str_FldSet + "&field=end_addr:string(50)&field=start_addr:string(50)"
		
		
		Vl_Gs = QgsVectorLayer("Linestring?crs=epsg:4326&" + str_FldSet + "&index=yes", "GeoSearch_Route_legs", "memory")
		dP_Gs = Vl_Gs.dataProvider()
		QgsMapLayerRegistry.instance().addMapLayer(Vl_Gs)
		self.legend.setLayerVisible(Vl_Gs, False)
		
		#Enable Label
		label = Vl_Gs.label()
		label.setLabelField(QgsLabel.Text, 0)
		Vl_Gs.enableLabels(True)
		
		
		#Create, GeoSearch_Route_steps
		str_FldSet = "field=distance_text:string(50)&field=distance_value:double"
		str_FldSet = str_FldSet + "&field=duration_text:string(50)&field=duration_value:double"
		str_FldSet = str_FldSet + "&field=travel_mode:string(50)"
		
		
		Vl_Gs_S = QgsVectorLayer("Linestring?crs=epsg:4326&" + str_FldSet + "&index=yes", "GeoSearch_Route_steps", "memory")
		dP_Gs_S = Vl_Gs_S.dataProvider()
		QgsMapLayerRegistry.instance().addMapLayer(Vl_Gs_S)

		#Enable Label
		label = Vl_Gs_S.label()
		label.setLabelField(QgsLabel.Text, 0)
		Vl_Gs_S.enableLabels(True)
		
		
		# add a feature
		for leg in results[0]['legs']:
			#Add feature of legs
			AttrSet = []
			AttrSet.append(leg['distance']['text'])
			AttrSet.append(leg['distance']['value'])
			AttrSet.append(leg['duration']['text'])
			AttrSet.append(leg['duration']['value'])
			AttrSet.append(leg['end_address'])
			AttrSet.append(leg['start_address'])
			
			Fet_Gs = QgsFeature()
			QgsPoint_A = QgsPoint(leg['start_location']['lng'], leg['start_location']['lat'])
			QgsPoint_B = QgsPoint(leg['end_location']['lng'], leg['end_location']['lat'])
			Fet_Gs.setGeometry(QgsGeometry.fromMultiPolyline([[QgsPoint_A, QgsPoint_B]]))
			Fet_Gs.setAttributes(AttrSet)

			dP_Gs.addFeatures([Fet_Gs])
			
			
			for step in leg['steps']:
				#Add feature of steps
				AttrSet = []
				AttrSet.append(step['distance']['text'])
				AttrSet.append(step['distance']['value'])
				AttrSet.append(step['duration']['text'])
				AttrSet.append(step['duration']['value'])
				AttrSet.append(step['travel_mode'])
				
				Fet_Gs = QgsFeature()
				QgsPoint_A = QgsPoint(step['start_location']['lng'], step['start_location']['lat'])
				QgsPoint_B = QgsPoint(step['end_location']['lng'], step['end_location']['lat'])
				Fet_Gs.setGeometry(QgsGeometry.fromMultiPolyline([[QgsPoint_A, QgsPoint_B]]))
				Fet_Gs.setAttributes(AttrSet)

				dP_Gs_S.addFeatures([Fet_Gs])
		
		
		Vl_Gs.updateExtents()
		Vl_Gs_S.updateExtents()
		
		
		#Get the feature id of the vector layer
		FetSet = Vl_Gs_S.getFeatures()
		FetIdList = []
		
		for feat in FetSet:
			FetIdList.append(feat.id())

		#QMessageBox.information(None, "Error", str(feat.id()))
		#Symbol Setup
		#{  
		self.CreateSymbolRendererV2ForVectorLayerOfLineStr(Vl_Gs, "MarkerLine", "SimpleMarker", "filled_arrowhead", QColor(255, 0, 0))
		self.CreateSymbolRendererV2ForVectorLayerOfLineStr(Vl_Gs_S, "MarkerLine", "SimpleMarker", "filled_arrowhead", QColor(255, 0, 0))
		#}
		
		#Refresh the MapCanvas
		self.mapCanvas.refresh()
		
		
		#Zoom to Search Results
		#Vl_Gs.removeSelection()
		Vl_Gs_S.setSelectedFeatures(FetIdList)
		self.mapCanvas.zoomToSelected(Vl_Gs_S)
		self.mapCanvas.zoomOut()
		
		
class Bearing():
	def __init__(self, QgsPt_A, QgsPt_B, srsid):
		'''
		20150502, walter_tsui
		Paul Stanley(pslat@eircom.net) reported the bearing calculated from QGIS API is wrong
		
		DA = QgsDistanceArea()
		DA.setSourceCrs(srsid)

		self.radian = DA.bearing(QgsPt_A, QgsPt_B)
		self.degree = math.degrees(initial_bearing)
		'''
		
		lat_A = math.radians(QgsPt_A.y())
		lat_B = math.radians(QgsPt_B.y())
 
		LonDiff = math.radians(QgsPt_A.x() - QgsPt_B.x())
	 
		x = math.sin(LonDiff) * math.cos(lat_B)
		y = math.cos(lat_A) * math.sin(lat_B) - (math.sin(lat_A) * math.cos(lat_B) * math.cos(LonDiff))
	 
		self.radian = math.atan2(x, y)
		self.degree = math.degrees(self.radian)
			
	
#Modified from GeoCoding\Utils.py
def CoorTransformByCrsId(point, crs_id_src, crs_id_des):
	crs_src = QgsCoordinateReferenceSystem()
	crs_src.createFromSrid(crs_id_src)

	crs_des = QgsCoordinateReferenceSystem()
	crs_des.createFromSrid(crs_id_des)

	transformer = QgsCoordinateTransform(crs_src, crs_des)
	pt = transformer.transform(point)
	
	return pt

#Coordinate Transform
def CoorTransform(point, crs_src, crs_des):
	transformer = QgsCoordinateTransform(crs_src, crs_des)
	pt = transformer.transform(point)
	
	return pt
	
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