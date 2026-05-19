//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "Gaffer/WeightVectorPlug.h"

#include "IECore/VectorTypedData.h"

#include <limits>

using namespace IECore;
using namespace Gaffer;

GAFFER_PLUG_DEFINE_TYPE( WeightVectorPlug );

size_t WeightVectorPlug::g_firstPlugIndex = 0;

WeightVectorPlug::WeightVectorPlug(
	const std::string &name,
	Direction direction,
	ConstStringVectorDataPtr defaultInstrumentIds,
	ConstFloatVectorDataPtr defaultTargetWeights,
	ConstFloatVectorDataPtr defaultConfidences,
	ConstFloatVectorDataPtr defaultHalfLives,
	float defaultGrossExposure,
	float defaultNetExposure,
	const std::string &defaultActiveRegime,
	const std::string &defaultEvaluatedAt,
	unsigned flags
)
	:	ValuePlug( name, direction, flags )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	StringVectorDataPtr instruments = new StringVectorData;
	if( defaultInstrumentIds )
	{
		instruments->writable() = defaultInstrumentIds->readable();
	}

	FloatVectorDataPtr targets = new FloatVectorData;
	if( defaultTargetWeights )
	{
		targets->writable() = defaultTargetWeights->readable();
	}

	FloatVectorDataPtr confs = new FloatVectorData;
	if( defaultConfidences )
	{
		confs->writable() = defaultConfidences->readable();
	}

	FloatVectorDataPtr halfLives = new FloatVectorData;
	if( defaultHalfLives )
	{
		halfLives->writable() = defaultHalfLives->readable();
	}

	const float lo = std::numeric_limits<float>::lowest();
	const float hi = std::numeric_limits<float>::max();

	addChild( new StringVectorDataPlug( "instrumentIds", direction, instruments, flags ) );
	addChild( new FloatVectorDataPlug( "targetWeights", direction, targets, flags ) );
	addChild( new FloatVectorDataPlug( "confidences", direction, confs, flags ) );
	addChild( new FloatVectorDataPlug( "halfLives", direction, halfLives, flags ) );
	addChild( new FloatPlug( "grossExposure", direction, defaultGrossExposure, lo, hi, flags ) );
	addChild( new FloatPlug( "netExposure", direction, defaultNetExposure, lo, hi, flags ) );
	addChild( new StringPlug( "activeRegime", direction, defaultActiveRegime, flags ) );
	addChild( new StringPlug( "evaluatedAt", direction, defaultEvaluatedAt, flags ) );
}

WeightVectorPlug::WeightVectorPlug( const std::string &name, Direction direction, unsigned flags )
	:	WeightVectorPlug(
			name, direction,
			nullptr, nullptr, nullptr, nullptr,
			0.0f, 0.0f,
			std::string(), std::string(),
			flags
		)
{
}

WeightVectorPlug::~WeightVectorPlug()
{
}

bool WeightVectorPlug::acceptsChild( const GraphComponent *potentialChild ) const
{
	return children().size() != 8;
}

PlugPtr WeightVectorPlug::createCounterpart( const std::string &n, Direction direction ) const
{
	StringVectorDataPtr i = new StringVectorData;
	i->writable() = instrumentIdsPlug()->defaultValue()->readable();
	FloatVectorDataPtr t = new FloatVectorData;
	t->writable() = targetWeightsPlug()->defaultValue()->readable();
	FloatVectorDataPtr c = new FloatVectorData;
	c->writable() = confidencesPlug()->defaultValue()->readable();
	FloatVectorDataPtr h = new FloatVectorData;
	h->writable() = halfLivesPlug()->defaultValue()->readable();

	return new WeightVectorPlug(
		n, direction,
		i, t, c, h,
		grossExposurePlug()->defaultValue(),
		netExposurePlug()->defaultValue(),
		activeRegimePlug()->defaultValue(),
		evaluatedAtPlug()->defaultValue(),
		getFlags()
	);
}

StringVectorDataPlug *WeightVectorPlug::instrumentIdsPlug()
{
	return getChild<StringVectorDataPlug>( g_firstPlugIndex );
}

const StringVectorDataPlug *WeightVectorPlug::instrumentIdsPlug() const
{
	return getChild<StringVectorDataPlug>( g_firstPlugIndex );
}

FloatVectorDataPlug *WeightVectorPlug::targetWeightsPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 1 );
}

const FloatVectorDataPlug *WeightVectorPlug::targetWeightsPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 1 );
}

FloatVectorDataPlug *WeightVectorPlug::confidencesPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 2 );
}

const FloatVectorDataPlug *WeightVectorPlug::confidencesPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 2 );
}

FloatVectorDataPlug *WeightVectorPlug::halfLivesPlug()
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 3 );
}

const FloatVectorDataPlug *WeightVectorPlug::halfLivesPlug() const
{
	return getChild<FloatVectorDataPlug>( g_firstPlugIndex + 3 );
}

FloatPlug *WeightVectorPlug::grossExposurePlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex + 4 );
}

const FloatPlug *WeightVectorPlug::grossExposurePlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex + 4 );
}

FloatPlug *WeightVectorPlug::netExposurePlug()
{
	return getChild<FloatPlug>( g_firstPlugIndex + 5 );
}

const FloatPlug *WeightVectorPlug::netExposurePlug() const
{
	return getChild<FloatPlug>( g_firstPlugIndex + 5 );
}

StringPlug *WeightVectorPlug::activeRegimePlug()
{
	return getChild<StringPlug>( g_firstPlugIndex + 6 );
}

const StringPlug *WeightVectorPlug::activeRegimePlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex + 6 );
}

StringPlug *WeightVectorPlug::evaluatedAtPlug()
{
	return getChild<StringPlug>( g_firstPlugIndex + 7 );
}

const StringPlug *WeightVectorPlug::evaluatedAtPlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex + 7 );
}
