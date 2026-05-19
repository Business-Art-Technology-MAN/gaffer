//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include "Gaffer/Export.h"
#include "Gaffer/StringPlug.h"
#include "Gaffer/ValuePlug.h"

namespace Gaffer
{

/// OTL **volatility regime** output (Phase 3). Distinct :cpp:type:`TypeId` from :cpp:class:`RegimePlug`
/// so Layer 4 option nodes can wire **VOL_HIGH** / **VOL_NORMAL** / **VOL_LOW** / **ANY** without
/// ambiguity versus macro **RISK_\*** tokens.
class GAFFER_API VolRegimePlug : public ValuePlug
{

	public :

		explicit VolRegimePlug(
			const std::string &name = defaultName<VolRegimePlug>(),
			Direction direction = In,
			const std::string &defaultValue = "VOL_NORMAL",
			unsigned flags = Default
		);

		explicit VolRegimePlug( const std::string &name, Direction direction, unsigned flags );

		~VolRegimePlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::VolRegimePlug, VolRegimePlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		StringPlug *valuePlug();
		const StringPlug *valuePlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( VolRegimePlug )

} // namespace Gaffer
