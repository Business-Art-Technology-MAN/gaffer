//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/ArraySignalPlug.h"

#include "Gaffer/SignalClosurePlug.h"

#include "IECore/VectorTypedData.h"

#include <limits>

using namespace IECore;
using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( ArraySignalPlug );

size_t ArraySignalPlug::g_firstPlugIndex = 0;

ArraySignalPlug::ArraySignalPlug( const std::string &name, Direction direction, unsigned flags )
	:	Plug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	StringVectorDataPtr ids = new StringVectorData;
	addChild( new StringVectorDataPlug( "instrumentIds", direction, ids, flags ) );

	ConstPlugPtr elementProto( new SignalClosurePlug(
		"signal",
		direction,
		0.0f,
		0.0f,
		0.0f,
		0.0f,
		std::string(),
		false,
		flags
	) );

	addChild( new ArrayPlug(
		"signals",
		direction,
		elementProto,
		0,
		std::numeric_limits<size_t>::max(),
		flags,
		true
	) );
}

ArraySignalPlug::~ArraySignalPlug() = default;

bool ArraySignalPlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 2;
}

PlugPtr ArraySignalPlug::createCounterpart( const std::string &n, Direction direction ) const
{
	return new ArraySignalPlug( n, direction, getFlags() );
}

StringVectorDataPlug *ArraySignalPlug::instrumentIdsPlug()
{
	return getChild<StringVectorDataPlug>( g_firstPlugIndex );
}

const StringVectorDataPlug *ArraySignalPlug::instrumentIdsPlug() const
{
	return getChild<StringVectorDataPlug>( g_firstPlugIndex );
}

ArrayPlug *ArraySignalPlug::signalsPlug()
{
	return getChild<ArrayPlug>( g_firstPlugIndex + 1 );
}

const ArrayPlug *ArraySignalPlug::signalsPlug() const
{
	return getChild<ArrayPlug>( g_firstPlugIndex + 1 );
}
