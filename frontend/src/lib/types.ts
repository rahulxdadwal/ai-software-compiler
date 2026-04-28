/** API client types matching backend Pydantic schemas. */

export interface CompileRequest {
  prompt: string;
}

export interface StageOutput {
  stage_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration_ms: number;
  data: Record<string, unknown> | null;
  error: string | null;
}

export interface ValidationIssue {
  issue_type: string;
  layer: string;
  location: string;
  description: string;
  severity: string;
  repaired: boolean;
  repair_action: string | null;
}

export interface RepairReport {
  total_issues_found: number;
  total_issues_repaired: number;
  repair_cycles: number;
  issues: ValidationIssue[];
}

export interface ExecutionResult {
  is_executable: boolean;
  routes_valid: boolean;
  forms_api_mapped: boolean;
  api_db_mapped: boolean;
  auth_coverage_complete: boolean;
  business_rules_consistent: boolean;
  details: string[];
  score: number;
}

export interface PipelineMetadata {
  pipeline_version: string;
  generated_at: string;
  total_duration_ms: number;
  stage_durations_ms: Record<string, number>;
  mock_mode: boolean;
  assumptions: string[];
  ambiguities_detected: number;
}

export interface FinalAppSpec {
  intent: Record<string, unknown>;
  architecture: Record<string, unknown>;
  ui: Record<string, unknown>;
  api: Record<string, unknown>;
  db: Record<string, unknown>;
  auth: Record<string, unknown>;
  business_rules: Record<string, unknown>;
  validation_report: RepairReport;
  execution_result: ExecutionResult;
  metadata: PipelineMetadata;
}

export interface PipelineResponse {
  success: boolean;
  app_spec: FinalAppSpec | null;
  stages: StageOutput[];
  error: string | null;
}

export interface ExamplePrompt {
  title: string;
  prompt: string;
  category: string;
}

export interface HealthResponse {
  status: string;
  mock_mode: boolean;
  version: string;
}
