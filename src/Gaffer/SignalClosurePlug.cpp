//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/SignalClosurePlug.h"

#include <limits>

using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( SignalClosurePlug );

size_t SignalClosurePlug::g_firstPlugIndex = 0;

SignalClosurePlug::SignalClosurePlug(
	const std::string &name,
	Direction direction,
	float defaultAlphaWeight,
	float defaultConfidence,
	float defaultHalfLife,
	float defaultMaxImpactFrac,
	const std::string &defaultRegimeCondition,
	bool defaultSideBet,
	unsigned flags
)
	:	ValuePlug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	const float lo = std::numeric_limits<float>::lowest();
	const float hi = std::numeric_limits<float>::max();

	addChild( new FloatPlug( "alphaWeight", direction, defaultAlphaWeight, lo, hi, flags ) );
	addChild( new FloatPlug( "confidence", direction, defaultConfidence, lo, hi, flags ) );
	addChild( new FloatPlug( "halfLife", direction, defaultHalfLife, lo, hi, flags ) );
	addChild( new FloatPlug( "maxImpactFrac", direction, defaultMaxImpactFrac, lo, hi, flags ) );
	addChild( new StringPlug( "regimeCondition", direction, defaultRegimeCondition, flags ) );
	addChild( new BoolPlug( "sideBet", direction, defaultSideBet, flags ) );
}

SignalClosurePlug::~SignalClosurePlug()
{
}

bool SignalClosurePlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 6;
}

PlugPtr SignalClosurePlug::createCounterpart( const std::string &n, Direction direction ) const
{
	return new SignalClosurePlug(
		n, direction,
		alphaWeightPlug()->defaultValue(),
		confidencePlug()->defaultValue(),
		halfLifePlug()->defaultValue(),
		maxImpactFracPlug()->defaultValue(),
		regimeConditionPlug()->defaultValue(),
		sideBetPlug()->defaultValue(),
		getFlags()
	);
}

FloatPlug *SignalClosurePlug::alphaWeightPlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex );
}

const FloatPlug *SignalClosurePlug::alphaWeightPlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex );
}

FloatPlug *SignalClosurePlug::confidencePlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex + 1 );
}

const FloatPlug *SignalClosurePlug::confidencePlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex + 1 );
}

FloatPlug *SignalClosurePlug::halfLifePlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex + 2 );
}

const FloatPlug *SignalClosurePlug::halfLifePlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex + 2 );
}

FloatPlug *SignalClosurePlug::maxImpactFracPlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex + 3 );
}

const FloatPlug *SignalClosurePlug::maxImpactFracPlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex + 3 );
}

StringPlug *SignalClosurePlug::regimeConditionPlug()
{
	return getChild<StringPlug>( g_firstPlugIndex + 4 );
}

const StringPlug *SignalClosurePlug::regimeConditionPlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex + 4 );
}

BoolPlug *SignalClosurePlug::sideBetPlug()
{
	return getChild<BoolPlug>( g_firstPlugIndex + 5 );
}

const BoolPlug *SignalClosurePlug::sideBetPlug() const
{
	return getChild<BoolPlug>( g_firstPlugIndex + 5 );
}
