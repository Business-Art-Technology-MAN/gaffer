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

/// OTL dense float **vector** (e.g. PCA loadings stack, weights)—single ``values`` :cpp:class:`FloatVectorDataPlug`.
class GAFFER_API VectorPlug : public ValuePlug
{

	public :

		explicit VectorPlug(
			const std::string &name = defaultName<VectorPlug>(),
			Direction direction = In,
			IECore::ConstFloatVectorDataPtr defaultValues = nullptr,
			unsigned flags = Default
		);

		explicit VectorPlug( const std::string &name, Direction direction, unsigned flags );

		~VectorPlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::VectorPlug, VectorPlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		FloatVectorDataPlug *valuesPlug();
		const FloatVectorDataPlug *valuesPlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( VectorPlug )

} // namespace Gaffer
