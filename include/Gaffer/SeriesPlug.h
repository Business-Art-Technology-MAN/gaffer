//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include "Gaffer/Export.h"
#include "Gaffer/TypedObjectPlug.h"
#include "Gaffer/ValuePlug.h"

namespace Gaffer
{

/// Time-sampled scalar series: parallel `times` (int64, e.g. nanoseconds) and
/// `values` (float). Length must match for well-formed OTL usage; nodes may enforce.
class GAFFER_API SeriesPlug : public ValuePlug
{

	public :

		explicit SeriesPlug(
			const std::string &name = defaultName<SeriesPlug>(),
			Direction direction = In,
			IECore::ConstInt64VectorDataPtr defaultTimes = nullptr,
			IECore::ConstFloatVectorDataPtr defaultValues = nullptr,
			unsigned flags = Default
		);

		/// Construct with default empty series vectors (for Python `init` / node parenting).
		explicit SeriesPlug( const std::string &name, Direction direction, unsigned flags );

		~SeriesPlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::SeriesPlug, SeriesPlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		Int64VectorDataPlug *timesPlug();
		const Int64VectorDataPlug *timesPlug() const;
		FloatVectorDataPlug *valuesPlug();
		const FloatVectorDataPlug *valuesPlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( SeriesPlug )

} // namespace Gaffer
