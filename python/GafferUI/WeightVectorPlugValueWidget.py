##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import Gaffer
import GafferUI

from Qt import QtWidgets


## Read-only **WeightVectorPlug** table for Phase 5 portfolio inspection.
class WeightVectorPlugValueWidget( GafferUI.PlugValueWidget ) :

	def __init__( self, plug, **kw ) :

		self.__table = QtWidgets.QTableWidget( 0, 4 )
		self.__table.setHorizontalHeaderLabels( [ "Instrument", "Weight", "Confidence", "Half-life" ] )
		self.__table.verticalHeader().setVisible( False )
		self.__table.setEditTriggers( QtWidgets.QAbstractItemView.NoEditTriggers )
		self.__table.setSelectionMode( QtWidgets.QAbstractItemView.NoSelection )
		self.__summary = QtWidgets.QLabel()

		w = QtWidgets.QWidget()
		lay = QtWidgets.QVBoxLayout()
		lay.addWidget( self.__table )
		lay.addWidget( self.__summary )
		w.setLayout( lay )

		GafferUI.PlugValueWidget.__init__( self, w, plug, **kw )

	def _updateFromValues( self, values, exception ) :

		p = self.getPlug()
		if p is None or exception is not None :
			return

		ids = list( p.instrumentIdsPlug().getValue() )
		wts = list( p.targetWeightsPlug().getValue() )
		cfs = list( p.confidencesPlug().getValue() )
		hfs = list( p.halfLivesPlug().getValue() )
		n = max( len( ids ), len( wts ), len( cfs ), len( hfs ) )
		self.__table.setRowCount( n )

		for i in range( n ) :
			idv = str( ids[i] ) if i < len( ids ) else ""
			wv = float( wts[i] ) if i < len( wts ) else 0.0
			cv = float( cfs[i] ) if i < len( cfs ) else 0.0
			hv = float( hfs[i] ) if i < len( hfs ) else 0.0
			self.__table.setItem( i, 0, QtWidgets.QTableWidgetItem( idv ) )
			self.__table.setItem( i, 1, QtWidgets.QTableWidgetItem( "{:.6g}".format( wv ) ) )
			self.__table.setItem( i, 2, QtWidgets.QTableWidgetItem( "{:.6g}".format( cv ) ) )
			self.__table.setItem( i, 3, QtWidgets.QTableWidgetItem( "{:.6g}".format( hv ) ) )

		g = float( p.grossExposurePlug().getValue() )
		ne = float( p.netExposurePlug().getValue() )
		self.__summary.setText(
			"Gross exposure: {:.6g}   Net exposure: {:.6g}".format( g, ne )
		)


GafferUI.PlugValueWidget.registerType( Gaffer.WeightVectorPlug, WeightVectorPlugValueWidget )
