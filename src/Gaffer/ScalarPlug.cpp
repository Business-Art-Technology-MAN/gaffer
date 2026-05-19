//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/ScalarPlug.h"

#include <limits>

using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( ScalarPlug );

ScalarPlug::ScalarPlug(
	const std::string &name,
	Direction direction,
	float defaultValue,
	float minValue,
	float maxValue,
	unsigned flags
)
	:	FloatPlug( name, direction, defaultValue, minValue, maxValue, flags )
{
}

ScalarPlug::~ScalarPlug()
{
}

PlugPtr ScalarPlug::createCounterpart( const std::string &n, Direction direction ) const
{
	return new ScalarPlug(
		n, direction,
		defaultValue(), minValue(), maxValue(),
		getFlags()
	);
}
