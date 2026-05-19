//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/RegimePlug.h"

using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( RegimePlug );

size_t RegimePlug::g_firstPlugIndex = 0;

RegimePlug::RegimePlug(
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

RegimePlug::RegimePlug( const std::string &name, Direction direction, unsigned flags )
	:	RegimePlug( name, direction, "ANY", flags )
{
}

RegimePlug::~RegimePlug()
{
}

bool RegimePlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 1;
}

PlugPtr RegimePlug::createCounterpart( const std::string &n, Direction direction ) const
{
	return new RegimePlug( n, direction, valuePlug()->defaultValue(), getFlags() );
}

StringPlug *RegimePlug::valuePlug()
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

const StringPlug *RegimePlug::valuePlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex );
}
