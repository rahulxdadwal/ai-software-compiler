"""Evaluation metrics collection and reporting."""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class PromptMetrics:
    """Metrics for a single prompt evaluation."""
    prompt_id: str
    category: str
    title: str
    success: bool = False
    total_duration_ms: int = 0
    stage_durations_ms: dict = field(default_factory=dict)
    repair_cycles: int = 0
    issues_found: int = 0
    issues_repaired: int = 0
    schema_validation_pass: bool = False
    execution_pass: bool = False
    execution_score: float = 0.0
    error: Optional[str] = None
    ambiguities_detected: int = 0
    assumptions_count: int = 0


@dataclass
class BenchmarkReport:
    """Aggregate benchmark report."""
    total_prompts: int = 0
    successful: int = 0
    failed: int = 0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    avg_repair_cycles: float = 0.0
    avg_issues_found: float = 0.0
    avg_execution_score: float = 0.0
    schema_validation_pass_rate: float = 0.0
    execution_pass_rate: float = 0.0
    failure_categories: dict = field(default_factory=dict)
    prompt_results: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def compute_report(results: list[PromptMetrics]) -> BenchmarkReport:
    """Compute aggregate metrics from individual prompt results."""
    report = BenchmarkReport()
    report.total_prompts = len(results)
    report.prompt_results = [asdict(r) for r in results]

    if not results:
        return report

    report.successful = sum(1 for r in results if r.success)
    report.failed = report.total_prompts - report.successful
    report.success_rate = report.successful / report.total_prompts

    durations = [r.total_duration_ms for r in results if r.success]
    report.avg_duration_ms = sum(durations) / len(durations) if durations else 0

    repairs = [r.repair_cycles for r in results if r.success]
    report.avg_repair_cycles = sum(repairs) / len(repairs) if repairs else 0

    issues = [r.issues_found for r in results if r.success]
    report.avg_issues_found = sum(issues) / len(issues) if issues else 0

    scores = [r.execution_score for r in results if r.success]
    report.avg_execution_score = sum(scores) / len(scores) if scores else 0

    schema_pass = sum(1 for r in results if r.schema_validation_pass)
    report.schema_validation_pass_rate = schema_pass / report.total_prompts

    exec_pass = sum(1 for r in results if r.execution_pass)
    report.execution_pass_rate = exec_pass / report.total_prompts

    # Categorize failures
    for r in results:
        if not r.success and r.error:
            cat = r.error.split(":")[0] if ":" in r.error else "unknown"
            report.failure_categories[cat] = report.failure_categories.get(cat, 0) + 1

    return report
