//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/VolRegimePlug.h"

using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( VolRegimePlug );

size_t VolRegimePlug::g_firstPlugIndex = 0;

VolRegimePlug::VolRegimePlug(
	const std::string &name,
	Direction direction,
	const std::string &defaultValue,
	unsigned flags
)
	:	ValuePlug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	addChild( new StringPlug( "value", direction, defaultValue, flags ) );
}

VolRegimePlug::VolRegimePlug( const std::string &name, Direction direction, unsigned flags )
	:	VolRegimePlug( name, direction, "VOL_NORMAL", flags )
{
}

VolRegimePlug::~VolRegimePlug()
{
}

bool VolRegimePlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 1;
}

PlugPtr VolRegimePlug::createCounterpart( const std::string &n, Direction direction ) const
{
	return new VolRegimePlug( n, direction, valuePlug()->defaultValue(), getFlags() );
}

StringPlug *VolRegimePlug::valuePlug()
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

const StringPlug *VolRegimePlug::valuePlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex );
}
