//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include "Gaffer/Export.h"
#include "Gaffer/StringPlug.h"
#include "Gaffer/TypedObjectPlug.h"
#include "Gaffer/ValuePlug.h"

namespace Gaffer
{

/// Implied-volatility **surface**: sorted 1-D ``strikes`` and ``expiries`` (years) axes and
/// ``ivsRowMajor`` with ``strikes.size() * expiries.size()`` entries
/// (\ ``ivsRowMajor[ i * expiries.size() + j ]`` = IV at strike ``i``, expiry ``j`` ).
/// ``asOfTime`` is wall-clock / session time as a decimal string (e.g. ns), matching
/// :cpp:class:`MarketContextPlug::timeNanosecondsPlug`.
class GAFFER_API SurfacePlug : public ValuePlug
{

	public :

		explicit SurfacePlug(
			const std::string &name = defaultName<SurfacePlug>(),
			Direction direction = In,
			const std::string &defaultAsOfTime = "",
			IECore::ConstFloatVectorDataPtr defaultStrikes = nullptr,
			IECore::ConstFloatVectorDataPtr defaultExpiries = nullptr,
			IECore::ConstFloatVectorDataPtr defaultIvsRowMajor = nullptr,
			unsigned flags = Default
		);

		explicit SurfacePlug( const std::string &name, Direction direction, unsigned flags );

		~SurfacePlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::SurfacePlug, SurfacePlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		StringPlug *asOfTimePlug();
		const StringPlug *asOfTimePlug() const;
		FloatVectorDataPlug *strikesPlug();
		const FloatVectorDataPlug *strikesPlug() const;
		FloatVectorDataPlug *expiriesPlug();
		const FloatVectorDataPlug *expiriesPlug() const;
		FloatVectorDataPlug *ivsRowMajorPlug();
		const FloatVectorDataPlug *ivsRowMajorPlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( SurfacePlug )

} // namespace Gaffer
