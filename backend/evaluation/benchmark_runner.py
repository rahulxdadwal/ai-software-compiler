"""Benchmark runner — evaluates all prompts in dataset.json."""

import asyncio
import json
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.orchestrator import PipelineOrchestrator
from evaluation.metrics import PromptMetrics, compute_report


async def run_benchmark():
    """Run all evaluation prompts and generate report."""
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
    with open(dataset_path) as f:
        dataset = json.load(f)

    orchestrator = PipelineOrchestrator()
    results: list[PromptMetrics] = []

    print(f"🚀 Running benchmark on {len(dataset['prompts'])} prompts...\n")

    for item in dataset["prompts"]:
        metrics = PromptMetrics(
            prompt_id=item["id"],
            category=item["category"],
            title=item["title"],
        )
        print(f"  [{item['id']}] {item['title']}...", end=" ", flush=True)

        try:
            response = await orchestrator.run(item["prompt"])
            metrics.success = response.success

            if response.success and response.app_spec:
                spec = response.app_spec
                metrics.total_duration_ms = spec.metadata.total_duration_ms
                metrics.stage_durations_ms = spec.metadata.stage_durations_ms
                metrics.repair_cycles = spec.validation_report.repair_cycles
                metrics.issues_found = spec.validation_report.total_issues_found
                metrics.issues_repaired = spec.validation_report.total_issues_repaired
                metrics.schema_validation_pass = True
                metrics.execution_pass = spec.execution_result.is_executable
                metrics.execution_score = spec.execution_result.score
                metrics.ambiguities_detected = spec.metadata.ambiguities_detected
                metrics.assumptions_count = len(spec.metadata.assumptions)
                print(f"✅ score={spec.execution_result.score}")
            else:
                metrics.error = response.error or "Unknown failure"
                print(f"❌ {metrics.error}")
        except Exception as e:
            metrics.error = str(e)
            print(f"💥 {e}")

        results.append(metrics)

    # Generate report
    report = compute_report(results)

    # Save report
    report_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(report_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Total: {report.total_prompts} | Pass: {report.successful} | Fail: {report.failed}")
    print(f"Success Rate: {report.success_rate:.0%}")
    print(f"Avg Duration: {report.avg_duration_ms:.0f}ms")
    print(f"Avg Repair Cycles: {report.avg_repair_cycles:.1f}")
    print(f"Schema Validation Pass Rate: {report.schema_validation_pass_rate:.0%}")
    print(f"Execution Pass Rate: {report.execution_pass_rate:.0%}")
    print(f"Avg Execution Score: {report.avg_execution_score:.2f}")
    print(f"\nResults saved to: {report_path}")

    return report


if __name__ == "__main__":
    asyncio.run(run_benchmark())
