##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""
Class-level Metadata for MarketLab OTL compound plugs (node graph nodules).
"""

import Gaffer

__compoundClasses = (
	Gaffer.SeriesPlug,
	Gaffer.SignalClosurePlug,
	Gaffer.WeightVectorPlug,
	Gaffer.MarketContextPlug,
)

for _plugType in __compoundClasses :

	# Compound nodule on the parent; leaf plugs use standard nodules for wiring.
	Gaffer.Metadata.registerValue( _plugType, "nodule:type", "GafferUI::CompoundNodule" )
	Gaffer.Metadata.registerValue( _plugType, "*", "nodule:type", "GafferUI::StandardNodule" )
