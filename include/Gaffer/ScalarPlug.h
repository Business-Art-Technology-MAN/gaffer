//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include <limits>

#include "Gaffer/Export.h"
#include "Gaffer/NumericPlug.h"

namespace Gaffer
{

/// OTL **scalar** output type—subclasses :cpp:type:`FloatPlug` with a distinct ``TypeId`` so nodes can
/// expose single-float results (e.g. realized vol, λ proxy) with type-aware wiring vs generic ``FloatPlug``.
class GAFFER_API ScalarPlug : public FloatPlug
{

	public :

		explicit ScalarPlug(
			const std::string &name = defaultName<ScalarPlug>(),
			Direction direction = In,
			float defaultValue = 0.0f,
			float minValue = std::numeric_limits<float>::lowest(),
			float maxValue = std::numeric_limits<float>::max(),
			unsigned flags = Default
		);

		~ScalarPlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::ScalarPlug, ScalarPlugTypeId, FloatPlug );

		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

};

IE_CORE_DECLAREPTR( ScalarPlug )

} // namespace Gaffer
