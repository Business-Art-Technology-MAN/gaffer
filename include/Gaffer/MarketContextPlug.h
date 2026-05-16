//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include "Gaffer/Export.h"
#include "Gaffer/NumericPlug.h"
#include "Gaffer/StringPlug.h"
#include "Gaffer/ValuePlug.h"

namespace Gaffer
{

/// Evaluation context injected when evaluating OTL / PCE networks (macro snapshot).
class GAFFER_API MarketContextPlug : public ValuePlug
{

	public :

		explicit MarketContextPlug(
			const std::string &name = defaultName<MarketContextPlug>(),
			Direction direction = In,
			const std::string &defaultTimeNanoseconds = "",
			const std::string &defaultMacroRegime = "",
			float defaultVixLevel = 0.0f,
			float defaultTermSpread = 0.0f,
			float defaultCreditSpread = 0.0f,
			unsigned flags = Default
		);
		~MarketContextPlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::MarketContextPlug, MarketContextPlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		/// Wall-clock or exchange time as decimal string (e.g. nanoseconds) for OTL precision.
		StringPlug *timeNanosecondsPlug();
		const StringPlug *timeNanosecondsPlug() const;
		StringPlug *macroRegimePlug();
		const StringPlug *macroRegimePlug() const;
		FloatPlug *vixLevelPlug();
		const FloatPlug *vixLevelPlug() const;
		FloatPlug *termSpreadPlug();
		const FloatPlug *termSpreadPlug() const;
		FloatPlug *creditSpreadPlug();
		const FloatPlug *creditSpreadPlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( MarketContextPlug )

} // namespace Gaffer
