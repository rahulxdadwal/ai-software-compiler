"""Pipeline orchestrator — coordinates all 5 stages sequentially."""

import time
from datetime import datetime
from llm.provider import create_provider
from pipeline.intent_extractor import IntentExtractor
from pipeline.system_designer import SystemDesigner
from pipeline.schema_generator import SchemaGenerator
from pipeline.refinement_engine import RefinementEngine
from pipeline.execution_validator import ExecutionValidator
from schemas.final_app_spec_schema import (
    FinalAppSpec, PipelineResponse, StageOutput, PipelineMetadata,
)
from config import settings


class PipelineOrchestrator:
    """Runs the full 5-stage compiler pipeline."""

    def __init__(self):
        self.provider = create_provider()

    async def run(self, prompt: str) -> PipelineResponse:
        """Execute the full pipeline for a given prompt."""
        total_start = time.time()
        stages: list[StageOutput] = []
        durations: dict[str, int] = {}

        try:
            # Stage 1: Intent Extraction
            s1 = StageOutput(stage_name="intent_extraction", status="running")
            stages.append(s1)
            extractor = IntentExtractor(self.provider)
            intent, d1 = await extractor.extract(prompt)
            s1.status = "completed"
            s1.duration_ms = d1
            s1.data = intent.model_dump()
            durations["intent_extraction"] = d1

            # Stage 2: System Design
            s2 = StageOutput(stage_name="system_design", status="running")
            stages.append(s2)
            designer = SystemDesigner(self.provider)
            architecture, d2 = await designer.design(intent)
            s2.status = "completed"
            s2.duration_ms = d2
            s2.data = architecture.model_dump()
            durations["system_design"] = d2

            # Stage 3: Schema Generation
            s3 = StageOutput(stage_name="schema_generation", status="running")
            stages.append(s3)
            generator = SchemaGenerator(self.provider)
            schemas, d3 = await generator.generate(architecture)
            s3.status = "completed"
            s3.duration_ms = d3
            s3.data = {k: v.model_dump() for k, v in schemas.items()}
            durations["schema_generation"] = d3

            # Stage 4: Refinement & Repair
            s4 = StageOutput(stage_name="refinement", status="running")
            stages.append(s4)
            refiner = RefinementEngine()
            schemas, repair_report, d4 = refiner.refine(schemas)
            s4.status = "completed"
            s4.duration_ms = d4
            s4.data = repair_report.model_dump()
            durations["refinement"] = d4

            # Build final spec
            app_spec = FinalAppSpec(
                intent=intent,
                architecture=architecture,
                ui=schemas["ui"],
                api=schemas["api"],
                db=schemas["db"],
                auth=schemas["auth"],
                business_rules=schemas["business_rules"],
                validation_report=repair_report,
            )

            # Stage 5: Execution Validation
            s5 = StageOutput(stage_name="execution_validation", status="running")
            stages.append(s5)
            exec_validator = ExecutionValidator()
            exec_result, d5 = exec_validator.validate(app_spec)
            app_spec.execution_result = exec_result
            s5.status = "completed"
            s5.duration_ms = d5
            s5.data = exec_result.model_dump()
            durations["execution_validation"] = d5

            # Set metadata
            total_ms = int((time.time() - total_start) * 1000)
            app_spec.metadata = PipelineMetadata(
                generated_at=datetime.utcnow().isoformat(),
                total_duration_ms=total_ms,
                stage_durations_ms=durations,
                mock_mode=settings.use_mock,
                assumptions=intent.assumptions,
                ambiguities_detected=len(intent.ambiguities),
            )

            return PipelineResponse(success=True, app_spec=app_spec, stages=stages)

        except Exception as e:
            # Mark current stage as failed
            for stage in stages:
                if stage.status == "running":
                    stage.status = "failed"
                    stage.error = str(e)
            return PipelineResponse(success=False, stages=stages, error=str(e))
