//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
//
//////////////////////////////////////////////////////////////////////////

#include "boost/python.hpp"

#include "MarketDataPlugsBinding.h"

#include "GafferBindings/PlugBinding.h"
#include "GafferBindings/SerialisationBinding.h"
#include "GafferBindings/ValuePlugBinding.h"

#include "Gaffer/MarketContextPlug.h"
#include "Gaffer/MatrixPlug.h"
#include "Gaffer/RegimePlug.h"
#include "Gaffer/VolRegimePlug.h"
#include "Gaffer/SeriesPlug.h"
#include "Gaffer/SignalClosurePlug.h"
#include "Gaffer/SurfacePlug.h"
#include "Gaffer/VectorPlug.h"
#include "Gaffer/WeightVectorPlug.h"

#include "fmt/format.h"

using namespace boost::python;
using namespace GafferBindings;
using namespace Gaffer;

namespace
{

std::string basicPlugRepr( const char *pythonClassName, const ValuePlug *plug )
{
	std::string result = fmt::format( "Gaffer.{}( \"{}\"", pythonClassName, plug->getName().string() );
	if( plug->direction() != Plug::In )
	{
		result += ", direction = " + PlugSerialiser::directionRepr( plug->direction() );
	}
	const unsigned flags = plug->getFlags();
	if( flags != Plug::Default )
	{
		result += ", flags = " + PlugSerialiser::flagsRepr( flags );
	}
	result += " )";
	return result;
}

#define MARKET_PLUG_SERIALISER( PLUGTYPE, PYTHONNAME ) \
	class PLUGTYPE##Serialiser : public ValuePlugSerialiser \
	{ \
		public : \
			bool childNeedsConstruction( const Gaffer::GraphComponent *child, const Serialisation &serialisation ) const override \
			{ \
				return false; \
			} \
			std::string constructor( const Gaffer::GraphComponent *graphComponent, Serialisation &serialisation ) const override \
			{ \
				(void)serialisation; \
				return basicPlugRepr( PYTHONNAME, static_cast<const PLUGTYPE *>( graphComponent ) ); \
			} \
	};

MARKET_PLUG_SERIALISER( SeriesPlug, "SeriesPlug" )
MARKET_PLUG_SERIALISER( SignalClosurePlug, "SignalClosurePlug" )
MARKET_PLUG_SERIALISER( WeightVectorPlug, "WeightVectorPlug" )
MARKET_PLUG_SERIALISER( MarketContextPlug, "MarketContextPlug" )
MARKET_PLUG_SERIALISER( SurfacePlug, "SurfacePlug" )
MARKET_PLUG_SERIALISER( VectorPlug, "VectorPlug" )
MARKET_PLUG_SERIALISER( MatrixPlug, "MatrixPlug" )
MARKET_PLUG_SERIALISER( RegimePlug, "RegimePlug" )
MARKET_PLUG_SERIALISER( VolRegimePlug, "VolRegimePlug" )

#undef MARKET_PLUG_SERIALISER

} // namespace

void GafferModule::bindMarketDataPlugs()
{
	PlugClass<SeriesPlug>()
		.def(
			init<const std::string &, Plug::Direction, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<SeriesPlug>(),
					arg( "direction" ) = Plug::In,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "timesPlug", static_cast<Int64VectorDataPlug *(SeriesPlug::*)()>( &SeriesPlug::timesPlug ), return_value_policy<reference_existing_object>() )
		.def( "valuesPlug", static_cast<FloatVectorDataPlug *(SeriesPlug::*)()>( &SeriesPlug::valuesPlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( SeriesPlug::staticTypeId(), new SeriesPlugSerialiser );

	PlugClass<SignalClosurePlug>()
		.def(
			init<const std::string &, Plug::Direction, float, float, float, float, const std::string &, bool, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<SignalClosurePlug>(),
					arg( "direction" ) = Plug::In,
					arg( "defaultAlphaWeight" ) = 0.0f,
					arg( "defaultConfidence" ) = 0.0f,
					arg( "defaultHalfLife" ) = 0.0f,
					arg( "defaultMaxImpactFrac" ) = 0.0f,
					arg( "defaultRegimeCondition" ) = std::string(),
					arg( "defaultSideBet" ) = false,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "alphaWeightPlug", static_cast<FloatPlug *(SignalClosurePlug::*)()>( &SignalClosurePlug::alphaWeightPlug ), return_value_policy<reference_existing_object>() )
		.def( "confidencePlug", static_cast<FloatPlug *(SignalClosurePlug::*)()>( &SignalClosurePlug::confidencePlug ), return_value_policy<reference_existing_object>() )
		.def( "halfLifePlug", static_cast<FloatPlug *(SignalClosurePlug::*)()>( &SignalClosurePlug::halfLifePlug ), return_value_policy<reference_existing_object>() )
		.def( "maxImpactFracPlug", static_cast<FloatPlug *(SignalClosurePlug::*)()>( &SignalClosurePlug::maxImpactFracPlug ), return_value_policy<reference_existing_object>() )
		.def( "regimeConditionPlug", static_cast<StringPlug *(SignalClosurePlug::*)()>( &SignalClosurePlug::regimeConditionPlug ), return_value_policy<reference_existing_object>() )
		.def( "sideBetPlug", static_cast<BoolPlug *(SignalClosurePlug::*)()>( &SignalClosurePlug::sideBetPlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( SignalClosurePlug::staticTypeId(), new SignalClosurePlugSerialiser );

	PlugClass<WeightVectorPlug>()
		.def(
			init<const std::string &, Plug::Direction, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<WeightVectorPlug>(),
					arg( "direction" ) = Plug::In,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "instrumentIdsPlug", static_cast<StringVectorDataPlug *(WeightVectorPlug::*)()>( &WeightVectorPlug::instrumentIdsPlug ), return_value_policy<reference_existing_object>() )
		.def( "targetWeightsPlug", static_cast<FloatVectorDataPlug *(WeightVectorPlug::*)()>( &WeightVectorPlug::targetWeightsPlug ), return_value_policy<reference_existing_object>() )
		.def( "confidencesPlug", static_cast<FloatVectorDataPlug *(WeightVectorPlug::*)()>( &WeightVectorPlug::confidencesPlug ), return_value_policy<reference_existing_object>() )
		.def( "grossExposurePlug", static_cast<FloatPlug *(WeightVectorPlug::*)()>( &WeightVectorPlug::grossExposurePlug ), return_value_policy<reference_existing_object>() )
		.def( "netExposurePlug", static_cast<FloatPlug *(WeightVectorPlug::*)()>( &WeightVectorPlug::netExposurePlug ), return_value_policy<reference_existing_object>() )
		.def( "activeRegimePlug", static_cast<StringPlug *(WeightVectorPlug::*)()>( &WeightVectorPlug::activeRegimePlug ), return_value_policy<reference_existing_object>() )
		.def( "evaluatedAtPlug", static_cast<StringPlug *(WeightVectorPlug::*)()>( &WeightVectorPlug::evaluatedAtPlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( WeightVectorPlug::staticTypeId(), new WeightVectorPlugSerialiser );

	PlugClass<MarketContextPlug>()
		.def(
			init<const std::string &, Plug::Direction, const std::string &, const std::string &, float, float, float, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<MarketContextPlug>(),
					arg( "direction" ) = Plug::In,
					arg( "defaultTimeNanoseconds" ) = std::string(),
					arg( "defaultMacroRegime" ) = std::string(),
					arg( "defaultVixLevel" ) = 0.0f,
					arg( "defaultTermSpread" ) = 0.0f,
					arg( "defaultCreditSpread" ) = 0.0f,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "timeNanosecondsPlug", static_cast<StringPlug *(MarketContextPlug::*)()>( &MarketContextPlug::timeNanosecondsPlug ), return_value_policy<reference_existing_object>() )
		.def( "macroRegimePlug", static_cast<StringPlug *(MarketContextPlug::*)()>( &MarketContextPlug::macroRegimePlug ), return_value_policy<reference_existing_object>() )
		.def( "vixLevelPlug", static_cast<FloatPlug *(MarketContextPlug::*)()>( &MarketContextPlug::vixLevelPlug ), return_value_policy<reference_existing_object>() )
		.def( "termSpreadPlug", static_cast<FloatPlug *(MarketContextPlug::*)()>( &MarketContextPlug::termSpreadPlug ), return_value_policy<reference_existing_object>() )
		.def( "creditSpreadPlug", static_cast<FloatPlug *(MarketContextPlug::*)()>( &MarketContextPlug::creditSpreadPlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( MarketContextPlug::staticTypeId(), new MarketContextPlugSerialiser );

	PlugClass<SurfacePlug>()
		.def(
			init<const std::string &, Plug::Direction, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<SurfacePlug>(),
					arg( "direction" ) = Plug::In,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "asOfTimePlug", static_cast<StringPlug *(SurfacePlug::*)()>( &SurfacePlug::asOfTimePlug ), return_value_policy<reference_existing_object>() )
		.def( "strikesPlug", static_cast<FloatVectorDataPlug *(SurfacePlug::*)()>( &SurfacePlug::strikesPlug ), return_value_policy<reference_existing_object>() )
		.def( "expiriesPlug", static_cast<FloatVectorDataPlug *(SurfacePlug::*)()>( &SurfacePlug::expiriesPlug ), return_value_policy<reference_existing_object>() )
		.def( "ivsRowMajorPlug", static_cast<FloatVectorDataPlug *(SurfacePlug::*)()>( &SurfacePlug::ivsRowMajorPlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( SurfacePlug::staticTypeId(), new SurfacePlugSerialiser );

	PlugClass<VectorPlug>()
		.def(
			init<const std::string &, Plug::Direction, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<VectorPlug>(),
					arg( "direction" ) = Plug::In,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "valuesPlug", static_cast<FloatVectorDataPlug *(VectorPlug::*)()>( &VectorPlug::valuesPlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( VectorPlug::staticTypeId(), new VectorPlugSerialiser );

	PlugClass<MatrixPlug>()
		.def(
			init<const std::string &, Plug::Direction, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<MatrixPlug>(),
					arg( "direction" ) = Plug::In,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "rowTimesPlug", static_cast<Int64VectorDataPlug *(MatrixPlug::*)()>( &MatrixPlug::rowTimesPlug ), return_value_policy<reference_existing_object>() )
		.def( "valuesRowMajorPlug", static_cast<FloatVectorDataPlug *(MatrixPlug::*)()>( &MatrixPlug::valuesRowMajorPlug ), return_value_policy<reference_existing_object>() )
		.def( "numColumnsPlug", static_cast<IntPlug *(MatrixPlug::*)()>( &MatrixPlug::numColumnsPlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( MatrixPlug::staticTypeId(), new MatrixPlugSerialiser );

	PlugClass<RegimePlug>()
		.def(
			init<const std::string &, Plug::Direction, const std::string &, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<RegimePlug>(),
					arg( "direction" ) = Plug::In,
					arg( "defaultValue" ) = std::string( "ANY" ),
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def(
			init<const std::string &, Plug::Direction, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<RegimePlug>(),
					arg( "direction" ) = Plug::In,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "valuePlug", static_cast<StringPlug *(RegimePlug::*)()>( &RegimePlug::valuePlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( RegimePlug::staticTypeId(), new RegimePlugSerialiser );

	PlugClass<VolRegimePlug>()
		.def(
			init<const std::string &, Plug::Direction, const std::string &, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<VolRegimePlug>(),
					arg( "direction" ) = Plug::In,
					arg( "defaultValue" ) = std::string( "VOL_NORMAL" ),
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def(
			init<const std::string &, Plug::Direction, unsigned>(
				(
					arg( "name" ) = GraphComponent::defaultName<VolRegimePlug>(),
					arg( "direction" ) = Plug::In,
					arg( "flags" ) = Plug::Default
				)
			)
		)
		.def( "valuePlug", static_cast<StringPlug *(VolRegimePlug::*)()>( &VolRegimePlug::valuePlug ), return_value_policy<reference_existing_object>() )
	;
	Serialisation::registerSerialiser( VolRegimePlug::staticTypeId(), new VolRegimePlugSerialiser );
}
