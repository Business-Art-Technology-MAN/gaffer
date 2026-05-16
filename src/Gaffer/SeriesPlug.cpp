//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/SeriesPlug.h"

#include "IECore/VectorTypedData.h"

using namespace IECore;
using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( SeriesPlug );

size_t SeriesPlug::g_firstPlugIndex = 0;

SeriesPlug::SeriesPlug(
	const std::string &name,
	Direction direction,
	ConstInt64VectorDataPtr defaultTimes,
	ConstFloatVectorDataPtr defaultValues,
	unsigned flags
)
	:	ValuePlug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	Int64VectorDataPtr timesDefaultData = new Int64VectorData;
	if( defaultTimes )
	{
		timesDefaultData->writable() = defaultTimes->readable();
	}

	FloatVectorDataPtr valuesDefaultData = new FloatVectorData;
	if( defaultValues )
	{
		valuesDefaultData->writable() = defaultValues->readable();
	}

	addChild(
		new Int64VectorDataPlug(
			"times",
			direction,
			timesDefaultData,
			flags
		)
	);

	addChild(
		new FloatVectorDataPlug(
			"values",
			direction,
			valuesDefaultData,
			flags
		)
	);
}

SeriesPlug::SeriesPlug( const std::string &name, Direction direction, unsigned flags )
	:	SeriesPlug( name, direction, nullptr, nullptr, flags )
{
}

SeriesPlug::~SeriesPlug()
{
}

bool SeriesPlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 2;
}

PlugPtr SeriesPlug::createCounterpart( const std::string &n, Direction direction ) const
{
	Int64VectorDataPtr td = new Int64VectorData;
	td->writable() = timesPlug()->defaultValue()->readable();
	FloatVectorDataPtr vd = new FloatVectorData;
	vd->writable() = valuesPlug()->defaultValue()->readable();
	return new SeriesPlug( n, direction, td, vd, getFlags() );
}

Int64VectorDataPlug *SeriesPlug::timesPlug()
{
	return getChild<Int64VectorDataPlug>( g_firstPlugIndex );
}

const Int64VectorDataPlug *SeriesPlug::timesPlug() const
{
	return getChild<Int64VectorDataPlug>( g_firstPlugIndex );
}

FloatVectorDataPlug *SeriesPlug::valuesPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 1 );
}

const FloatVectorDataPlug *SeriesPlug::valuesPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 1 );
}
