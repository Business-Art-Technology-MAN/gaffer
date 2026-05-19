//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include "Gaffer/ArrayPlug.h"
#include "Gaffer/Export.h"
#include "Gaffer/Plug.h"
#include "Gaffer/TypedObjectPlug.h"

namespace Gaffer
{

/// OTL Phase 5 — parallel **instrument ids** and **SignalClosurePlug** array for portfolio aggregation.
/// Note: subclasses \c Plug (not \c ValuePlug) because \c ArrayPlug is a \c Plug.
class GAFFER_API ArraySignalPlug : public Plug
{

	public :

		explicit ArraySignalPlug(
			const std::string &name = defaultName<ArraySignalPlug>(),
			Direction direction = In,
			unsigned flags = Default
		);
		~ArraySignalPlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::ArraySignalPlug, ArraySignalPlugTypeId, Plug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		StringVectorDataPlug *instrumentIdsPlug();
		const StringVectorDataPlug *instrumentIdsPlug() const;
		ArrayPlug *signalsPlug();
		const ArrayPlug *signalsPlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( ArraySignalPlug )

} // namespace Gaffer
