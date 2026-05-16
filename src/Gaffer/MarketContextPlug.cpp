//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/MarketContextPlug.h"

#include <limits>

using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( MarketContextPlug );

size_t MarketContextPlug::g_firstPlugIndex = 0;

MarketContextPlug::MarketContextPlug(
	const std::string &name,
	Direction direction,
	const std::string &defaultTimeNanoseconds,
	const std::string &defaultMacroRegime,
	float defaultVixLevel,
	float defaultTermSpread,
	float defaultCreditSpread,
	unsigned flags
)
	:	ValuePlug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	const float lo = std::numeric_limits<float>::lowest();
	const float hi = std::numeric_limits<float>::max();

	addChild( new StringPlug( "timeNanoseconds", direction, defaultTimeNanoseconds, flags ) );
	addChild( new StringPlug( "macroRegime", direction, defaultMacroRegime, flags ) );
	addChild( new FloatPlug( "vixLevel", direction, defaultVixLevel, lo, hi, flags ) );
	addChild( new FloatPlug( "termSpread", direction, defaultTermSpread, lo, hi, flags ) );
	addChild( new FloatPlug( "creditSpread", direction, defaultCreditSpread, lo, hi, flags ) );
}

MarketContextPlug::~MarketContextPlug()
{
}

bool MarketContextPlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 5;
}

PlugPtr MarketContextPlug::createCounterpart( const std::string &n, Direction direction ) const
{
	return new MarketContextPlug(
		n, direction,
		timeNanosecondsPlug()->defaultValue(),
		macroRegimePlug()->defaultValue(),
		vixLevelPlug()->defaultValue(),
		termSpreadPlug()->defaultValue(),
		creditSpreadPlug()->defaultValue(),
		getFlags()
	);
}

StringPlug *MarketContextPlug::timeNanosecondsPlug()
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

const StringPlug *MarketContextPlug::timeNanosecondsPlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

StringPlug *MarketContextPlug::macroRegimePlug()
{
	return getChild<StringPlug>( g_firstPlugIndex + 1 );
}

const StringPlug *MarketContextPlug::macroRegimePlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex + 1 );
}

FloatPlug *MarketContextPlug::vixLevelPlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex + 2 );
}

const FloatPlug *MarketContextPlug::vixLevelPlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex + 2 );
}

FloatPlug *MarketContextPlug::termSpreadPlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex + 3 );
}

const FloatPlug *MarketContextPlug::termSpreadPlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex + 3 );
}

FloatPlug *MarketContextPlug::creditSpreadPlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex + 4 );
}

const FloatPlug *MarketContextPlug::creditSpreadPlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex + 4 );
}
