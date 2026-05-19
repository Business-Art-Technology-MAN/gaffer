//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/SurfacePlug.h"

#include "IECore/VectorTypedData.h"

using namespace IECore;
using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( SurfacePlug );

size_t SurfacePlug::g_firstPlugIndex = 0;

SurfacePlug::SurfacePlug(
	const std::string &name,
	Direction direction,
	const std::string &defaultAsOfTime,
	ConstFloatVectorDataPtr defaultStrikes,
	ConstFloatVectorDataPtr defaultExpiries,
	ConstFloatVectorDataPtr defaultIvsRowMajor,
	unsigned flags
)
	:	ValuePlug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	FloatVectorDataPtr strikesDefaultData = new FloatVectorData;
	if( defaultStrikes )
	{
		strikesDefaultData->writable() = defaultStrikes->readable();
	}

	FloatVectorDataPtr expiriesDefaultData = new FloatVectorData;
	if( defaultExpiries )
	{
		expiriesDefaultData->writable() = defaultExpiries->readable();
	}

	FloatVectorDataPtr ivsDefaultData = new FloatVectorData;
	if( defaultIvsRowMajor )
	{
		ivsDefaultData->writable() = defaultIvsRowMajor->readable();
	}

	addChild( new StringPlug( "asOfTime", direction, defaultAsOfTime, flags ) );
	addChild( new FloatVectorDataPlug( "strikes", direction, strikesDefaultData, flags ) );
	addChild( new FloatVectorDataPlug( "expiries", direction, expiriesDefaultData, flags ) );
	addChild( new FloatVectorDataPlug( "ivsRowMajor", direction, ivsDefaultData, flags ) );
}

SurfacePlug::SurfacePlug( const std::string &name, Direction direction, unsigned flags )
	:	SurfacePlug( name, direction, std::string(), nullptr, nullptr, nullptr, flags )
{
}

SurfacePlug::~SurfacePlug()
{
}

bool SurfacePlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 4;
}

PlugPtr SurfacePlug::createCounterpart( const std::string &n, Direction direction ) const
{
	FloatVectorDataPtr sd = new FloatVectorData;
	sd->writable() = strikesPlug()->defaultValue()->readable();
	FloatVectorDataPtr ed = new FloatVectorData;
	ed->writable() = expiriesPlug()->defaultValue()->readable();
	FloatVectorDataPtr id = new FloatVectorData;
	id->writable() = ivsRowMajorPlug()->defaultValue()->readable();

	return new SurfacePlug(
		n, direction,
		asOfTimePlug()->defaultValue(),
		sd, ed, id,
		getFlags()
	);
}

StringPlug *SurfacePlug::asOfTimePlug()
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

const StringPlug *SurfacePlug::asOfTimePlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

FloatVectorDataPlug *SurfacePlug::strikesPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 1 );
}

const FloatVectorDataPlug *SurfacePlug::strikesPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 1 );
}

FloatVectorDataPlug *SurfacePlug::expiriesPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 2 );
}

const FloatVectorDataPlug *SurfacePlug::expiriesPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 2 );
}

FloatVectorDataPlug *SurfacePlug::ivsRowMajorPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 3 );
}

const FloatVectorDataPlug *SurfacePlug::ivsRowMajorPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 3 );
}
