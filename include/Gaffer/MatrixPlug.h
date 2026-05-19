//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include "Gaffer/Export.h"
#include "Gaffer/NumericPlug.h"
#include "Gaffer/TypedObjectPlug.h"
#include "Gaffer/ValuePlug.h"

namespace Gaffer
{

/// OTL numeric **panel** / matrix over time: ``rowTimes`` (int64), ``valuesRowMajor`` with ``numColumns`` columns per row.
class GAFFER_API MatrixPlug : public ValuePlug
{

	public :

		explicit MatrixPlug(
			const std::string &name = defaultName<MatrixPlug>(),
			Direction direction = In,
			IECore::ConstInt64VectorDataPtr defaultRowTimes = nullptr,
			IECore::ConstFloatVectorDataPtr defaultValuesRowMajor = nullptr,
			int defaultNumColumns = 0,
			unsigned flags = Default
		);

		explicit MatrixPlug( const std::string &name, Direction direction, unsigned flags );

		~MatrixPlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::MatrixPlug, MatrixPlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		Int64VectorDataPlug *rowTimesPlug();
		const Int64VectorDataPlug *rowTimesPlug() const;
		FloatVectorDataPlug *valuesRowMajorPlug();
		const FloatVectorDataPlug *valuesRowMajorPlug() const;
		IntPlug *numColumnsPlug();
		const IntPlug *numColumnsPlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( MatrixPlug )

} // namespace Gaffer
