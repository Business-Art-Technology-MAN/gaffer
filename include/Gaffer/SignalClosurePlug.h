//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include "Gaffer/TypedPlug.h"
#include "Gaffer/Export.h"
#include "Gaffer/NumericPlug.h"
#include "Gaffer/StringPlug.h"
#include "Gaffer/ValuePlug.h"

namespace Gaffer
{

/// OTL signal closure (SigC): factor tilt fields for portfolio / chart tooling.
class GAFFER_API SignalClosurePlug : public ValuePlug
{

	public :

		explicit SignalClosurePlug(
			const std::string &name = defaultName<SignalClosurePlug>(),
			Direction direction = In,
			float defaultAlphaWeight = 0.0f,
			float defaultConfidence = 0.0f,
			float defaultHalfLife = 0.0f,
			float defaultMaxImpactFrac = 0.0f,
			const std::string &defaultRegimeCondition = "",
			bool defaultSideBet = false,
			unsigned flags = Default
		);
		~SignalClosurePlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::SignalClosurePlug, SignalClosurePlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		FloatPlug *alphaWeightPlug();
		const FloatPlug *alphaWeightPlug() const;
		FloatPlug *confidencePlug();
		const FloatPlug *confidencePlug() const;
		FloatPlug *halfLifePlug();
		const FloatPlug *halfLifePlug() const;
		FloatPlug *maxImpactFracPlug();
		const FloatPlug *maxImpactFracPlug() const;
		StringPlug *regimeConditionPlug();
		const StringPlug *regimeConditionPlug() const;
		BoolPlug *sideBetPlug();
		const BoolPlug *sideBetPlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( SignalClosurePlug )

} // namespace Gaffer
