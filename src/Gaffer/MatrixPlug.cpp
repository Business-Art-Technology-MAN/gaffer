//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/MatrixPlug.h"

#include "IECore/VectorTypedData.h"

#include <limits>

using namespace IECore;
using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( MatrixPlug );

size_t MatrixPlug::g_firstPlugIndex = 0;

MatrixPlug::MatrixPlug(
	const std::string &name,
	Direction direction,
	ConstInt64VectorDataPtr defaultRowTimes,
	ConstFloatVectorDataPtr defaultValuesRowMajor,
	int defaultNumColumns,
	unsigned flags
)
	:	ValuePlug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	Int64VectorDataPtr rowTimesDefaultData = new Int64VectorData;
	if( defaultRowTimes )
	{
		rowTimesDefaultData->writable() = defaultRowTimes->readable();
	}

	FloatVectorDataPtr valuesDefaultData = new FloatVectorData;
	if( defaultValuesRowMajor )
	{
		valuesDefaultData->writable() = defaultValuesRowMajor->readable();
	}

	addChild(
		new Int64VectorDataPlug(
			"rowTimes",
			direction,
			rowTimesDefaultData,
			flags
		)
	);

	addChild(
		new FloatVectorDataPlug(
			"valuesRowMajor",
			direction,
			valuesDefaultData,
			flags
		)
	);

	addChild(
		new IntPlug(
			"numColumns",
			direction,
			defaultNumColumns,
			0,
			std::numeric_limits<int>::max(),
			flags
		)
	);
}

MatrixPlug::MatrixPlug( const std::string &name, Direction direction, unsigned flags )
	:	MatrixPlug( name, direction, nullptr, nullptr, 0, flags )
{
}

MatrixPlug::~MatrixPlug()
{
}

bool MatrixPlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 3;
}

PlugPtr MatrixPlug::createCounterpart( const std::string &n, Direction direction ) const
{
	Int64VectorDataPtr td = new Int64VectorData;
	td->writable() = rowTimesPlug()->defaultValue()->readable();
	FloatVectorDataPtr vd = new FloatVectorData;
	vd->writable() = valuesRowMajorPlug()->defaultValue()->readable();
	return new MatrixPlug(
		n, direction,
		td, vd,
		numColumnsPlug()->defaultValue(),
		getFlags()
	);
}

Int64VectorDataPlug *MatrixPlug::rowTimesPlug()
{
	return getChild<Int64VectorDataPlug>( g_firstPlugIndex );
}

const Int64VectorDataPlug *MatrixPlug::rowTimesPlug() const
{
	return getChild<Int64VectorDataPlug>( g_firstPlugIndex );
}

FloatVectorDataPlug *MatrixPlug::valuesRowMajorPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 1 );
}

const FloatVectorDataPlug *MatrixPlug::valuesRowMajorPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 1 );
}

IntPlug *MatrixPlug::numColumnsPlug()
{
	return getChild<IntPlug>( g_firstPlugIndex + 2 );
}

const IntPlug *MatrixPlug::numColumnsPlug() const
{
	return getChild<IntPlug>( g_firstPlugIndex + 2 );
}
