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

/// OTL **macro regime** output (Phase 3). Value is a string token serialised in scripts/USD;
/// canonical labels include **RISK_ON**, **RISK_OFF**, **TRANSITION**, **ANY** — nodes may use a
/// wider vocabulary until a stricter enum is required.
class GAFFER_API RegimePlug : public ValuePlug
{

	public :

		explicit RegimePlug(
			const std::string &name = defaultName<RegimePlug>(),
			Direction direction = In,
			const std::string &defaultValue = "ANY",
			unsigned flags = Default
		);

		explicit RegimePlug( const std::string &name, Direction direction, unsigned flags );

		~RegimePlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::RegimePlug, RegimePlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		StringPlug *valuePlug();
		const StringPlug *valuePlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( RegimePlug )

} // namespace Gaffer
