//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#pragma once

#include "Gaffer/Export.h"
#include "Gaffer/NumericPlug.h"
#include "Gaffer/StringPlug.h"
#include "Gaffer/TypedObjectPlug.h"
#include "Gaffer/ValuePlug.h"

namespace Gaffer
{

/// Per-step portfolio weight vector and metadata for OTL / PCE.
class GAFFER_API WeightVectorPlug : public ValuePlug
{

	public :

		explicit WeightVectorPlug(
			const std::string &name = defaultName<WeightVectorPlug>(),
			Direction direction = In,
			IECore::ConstStringVectorDataPtr defaultInstrumentIds = nullptr,
			IECore::ConstFloatVectorDataPtr defaultTargetWeights = nullptr,
			IECore::ConstFloatVectorDataPtr defaultConfidences = nullptr,
			IECore::ConstFloatVectorDataPtr defaultHalfLives = nullptr,
			float defaultGrossExposure = 0.0f,
			float defaultNetExposure = 0.0f,
			const std::string &defaultActiveRegime = "",
			const std::string &defaultEvaluatedAt = "",
			unsigned flags = Default
		);

		/// Construct with default empty vectors / zero scalars (for Python `init` / node parenting).
		explicit WeightVectorPlug( const std::string &name, Direction direction, unsigned flags );

		~WeightVectorPlug() override;

		GAFFER_PLUG_DECLARE_TYPE( Gaffer::WeightVectorPlug, WeightVectorPlugTypeId, ValuePlug );

		bool acceptsChild( const GraphComponent *potentialChild ) const override;
		PlugPtr createCounterpart( const std::string &name, Direction direction ) const override;

		StringVectorDataPlug *instrumentIdsPlug();
		const StringVectorDataPlug *instrumentIdsPlug() const;
		FloatVectorDataPlug *targetWeightsPlug();
		const FloatVectorDataPlug *targetWeightsPlug() const;
		FloatVectorDataPlug *confidencesPlug();
		const FloatVectorDataPlug *confidencesPlug() const;
		FloatVectorDataPlug *halfLivesPlug();
		const FloatVectorDataPlug *halfLivesPlug() const;
		FloatPlug *grossExposurePlug();
		const FloatPlug *grossExposurePlug() const;
		FloatPlug *netExposurePlug();
		const FloatPlug *netExposurePlug() const;
		StringPlug *activeRegimePlug();
		const StringPlug *activeRegimePlug() const;
		StringPlug *evaluatedAtPlug();
		const StringPlug *evaluatedAtPlug() const;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( WeightVectorPlug )

} // namespace Gaffer
