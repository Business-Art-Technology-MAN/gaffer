//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/VectorPlug.h"

#include "IECore/VectorTypedData.h"

using namespace IECore;
using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( VectorPlug );

size_t VectorPlug::g_firstPlugIndex = 0;

VectorPlug::VectorPlug(
	const std::string &name,
	Direction direction,
	ConstFloatVectorDataPtr defaultValues,
	unsigned flags
)
	:	ValuePlug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	FloatVectorDataPtr valuesDefaultData = new FloatVectorData;
	if( defaultValues )
	{
		valuesDefaultData->writable() = defaultValues->readable();
	}

	addChild(
		new FloatVectorDataPlug(
			"values",
			direction,
			valuesDefaultData,
			flags
		)
	);
}

VectorPlug::VectorPlug( const std::string &name, Direction direction, unsigned flags )
	:	VectorPlug( name, direction, nullptr, flags )
{
}

VectorPlug::~VectorPlug()
{
}

bool VectorPlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 1;
}

PlugPtr VectorPlug::createCounterpart( const std::string &n, Direction direction ) const
{
	FloatVectorDataPtr vd = new FloatVectorData;
	vd->writable() = valuesPlug()->defaultValue()->readable();
	return new VectorPlug( n, direction, vd, getFlags() );
}

FloatVectorDataPlug *VectorPlug::valuesPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex );
}

const FloatVectorDataPlug *VectorPlug::valuesPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex );
}
