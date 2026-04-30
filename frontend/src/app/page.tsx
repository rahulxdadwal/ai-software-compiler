"use client";

import { useState, useEffect, useCallback } from "react";
import { compilePrompt, getExamples, getHealth } from "@/lib/api";
import type { PipelineResponse, ExamplePrompt, StageOutput } from "@/lib/types";

const STAGE_LABELS: Record<string, string> = {
  intent_extraction: "Intent Extraction",
  system_design: "System Design",
  schema_generation: "Schema Generation",
  refinement: "Refinement & Repair",
  execution_validation: "Execution Validation",
};

const STAGE_KEYS = Object.keys(STAGE_LABELS);

// Sub-tabs for schema generation stage
const SCHEMA_TABS = ["ui", "api", "db", "auth", "business_rules"];

function JsonViewer({ data }: { data: unknown }) {
  const formatted = JSON.stringify(data, null, 2);
  // Simple syntax coloring
  const colored = formatted
    .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
    .replace(/: "([^"]*)"/g, ': <span class="json-string">"$1"</span>')
    .replace(/: (\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
    .replace(/: (true|false)/g, ': <span class="json-boolean">$1</span>')
    .replace(/: (null)/g, ': <span class="json-null">$1</span>');
  return (
    <div className="json-viewer">
      <pre dangerouslySetInnerHTML={{ __html: colored }} />
    </div>
  );
}

export default function Home() {
  const [prompt, setPrompt] = useState(
    "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
  );
  const [result, setResult] = useState<PipelineResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStage, setActiveStage] = useState(0);
  const [activeSchemaTab, setActiveSchemaTab] = useState(0);
  const [examples, setExamples] = useState<ExamplePrompt[]>([]);
  const [mockMode, setMockMode] = useState(true);

  useEffect(() => {
    getExamples().then(setExamples).catch(() => {});
    getHealth().then((h) => setMockMode(h.mock_mode)).catch(() => {});
  }, []);

  const handleCompile = useCallback(async () => {
    if (!prompt.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveStage(0);
    try {
      const res = await compilePrompt(prompt);
      setResult(res);
      if (!res.success) setError(res.error || "Pipeline failed");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Connection failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [prompt, loading]);

  const getStageData = (idx: number): StageOutput | null => {
    if (!result) return null;
    return result.stages[idx] || null;
  };

  const renderStageContent = (idx: number) => {
    const stage = getStageData(idx);
    if (!stage) {
      return (
        <div className="empty-state">
          <div className="icon">⚡</div>
          <h3>Run the pipeline to see results</h3>
          <p>Enter a product prompt and click Compile to start the 5-stage pipeline.</p>
        </div>
      );
    }
    if (stage.status === "failed") {
      return (
        <div className="panel">
          <div className="panel-body">
            <div className="validation-item fail">
              <span className="validation-icon">❌</span>
              <div><strong>Stage Failed</strong><br />{stage.error}</div>
            </div>
          </div>
        </div>
      );
    }

    const key = STAGE_KEYS[idx];

    // Special rendering for refinement stage — show repair report
    if (key === "refinement" && stage.data) {
      const report = stage.data;
      const issues = (report.issues as Array<Record<string, unknown>>) || [];
      return (
        <div className="panel">
          <div className="panel-header">
            <h3>Repair Report</h3>
            <span className="timing-value">{stage.duration_ms}ms</span>
          </div>
          <div className="panel-body">
            <div className="timing-bar" style={{ marginBottom: 16 }}>
              <div className="timing-item">Issues Found: <span className="timing-value">{String(report.total_issues_found)}</span></div>
              <div className="timing-item">Issues Repaired: <span className="timing-value">{String(report.total_issues_repaired)}</span></div>
              <div className="timing-item">Repair Cycles: <span className="timing-value">{String(report.repair_cycles)}</span></div>
            </div>
            {issues.length === 0 ? (
              <div className="validation-item pass">
                <span className="validation-icon">✅</span>
                <div>No cross-layer issues detected — all schemas are consistent.</div>
              </div>
            ) : (
              <div className="validation-list">
                {issues.map((issue, i) => (
                  <div key={i} className={`validation-item ${!!issue.repaired ? "pass" : issue.severity === "warning" ? "warn" : "fail"}`}>
                    <span className="validation-icon">{!!issue.repaired ? "🔧" : issue.severity === "warning" ? "⚠️" : "❌"}</span>
                    <div>
                      <div>{String(issue.description)}</div>
                      <div className="location">{String(issue.location)}</div>
                      {!!issue.repair_action && <div style={{ fontSize: 11, color: "var(--success)", marginTop: 4 }}>Repair: {String(issue.repair_action)}</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      );
    }

    // Special rendering for execution validation
    if (key === "execution_validation" && stage.data) {
      const exec = stage.data;
      const details = (exec.details as string[]) || [];
      const score = Number(exec.score || 0);
      const checks = [
        { label: "Routes Valid", val: exec.routes_valid },
        { label: "Forms→API Mapped", val: exec.forms_api_mapped },
        { label: "API→DB Mapped", val: exec.api_db_mapped },
        { label: "Auth Coverage", val: exec.auth_coverage_complete },
        { label: "Business Rules", val: exec.business_rules_consistent },
      ];
      return (
        <div className="panel">
          <div className="panel-header">
            <h3>Execution Readiness</h3>
            <span className="timing-value">{stage.duration_ms}ms</span>
          </div>
          <div className="panel-body">
            <div className="exec-score">
              <div className={`score-circle ${score >= 0.8 ? "score-pass" : "score-fail"}`}>
                {Math.round(score * 100)}%
              </div>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  {exec.is_executable ? "✅ Executable" : "❌ Not Ready"}
                </div>
                <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>
                  Execution readiness score
                </div>
              </div>
            </div>
            <div className="exec-checks">
              {checks.map((c, i) => (
                <div key={i} className="exec-check">
                  <span>{c.val ? "✅" : "❌"}</span>
                  <span>{c.label}</span>
                </div>
              ))}
            </div>
            {details.length > 0 && (
              <div style={{ marginTop: 16 }}>
                {details.map((d, i) => (
                  <div key={i} style={{ fontSize: 13, padding: "4px 0", color: "var(--text-secondary)" }}>{d}</div>
                ))}
              </div>
            )}
          </div>
        </div>
      );
    }

    // Schema generation — show sub-tabs
    if (key === "schema_generation" && stage.data) {
      const schemaData = stage.data;
      return (
        <div className="panel">
          <div className="panel-header">
            <h3>Generated Schemas</h3>
            <span className="timing-value">{stage.duration_ms}ms</span>
          </div>
          <div style={{ padding: "12px 20px 0" }}>
            <div className="stage-tabs" style={{ marginBottom: 0 }}>
              {SCHEMA_TABS.map((tab, i) => (
                <button key={tab} className={`stage-tab ${activeSchemaTab === i ? "active" : ""}`}
                  onClick={() => setActiveSchemaTab(i)}>
                  {tab.replace("_", " ").toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          <div className="panel-body">
            <JsonViewer data={schemaData[SCHEMA_TABS[activeSchemaTab]] || {}} />
          </div>
        </div>
      );
    }

    // Default — show JSON
    return (
      <div className="panel">
        <div className="panel-header">
          <h3>{STAGE_LABELS[STAGE_KEYS[idx]]}</h3>
          <span className="timing-value">{stage.duration_ms}ms</span>
        </div>
        <div className="panel-body">
          <JsonViewer data={stage.data || {}} />
        </div>
      </div>
    );
  };

  // Assumptions panel
  const renderAssumptions = () => {
    if (!result?.app_spec) return null;
    const meta = result.app_spec.metadata;
    const intent = result.app_spec.intent as Record<string, unknown>;
    const assumptions = (meta.assumptions || []) as string[];
    const ambiguities = (intent.ambiguities || []) as Array<Record<string, string>>;
    if (assumptions.length === 0 && ambiguities.length === 0) return null;
    return (
      <div className="panel" style={{ marginTop: 20 }}>
        <div className="panel-header"><h3>Assumptions & Ambiguities</h3></div>
        <div className="panel-body">
          {ambiguities.length > 0 && ambiguities.map((a, i) => (
            <div key={i} className="ambiguity-item">
              <div className="area">⚠️ {a.area}</div>
              <div className="desc">{a.description}</div>
              <div className="assumption-text">Assumed: {a.assumption}</div>
            </div>
          ))}
          {assumptions.length > 0 && assumptions.map((a, i) => (
            <div key={i} className="assumption-item">💡 {a}</div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">⚙</div>
          <div>
            <div className="logo-text">Software Compiler</div>
            <div className="logo-sub">AI Platform Engineer</div>
          </div>
        </div>

        <div className="section-header">Example Prompts</div>
        {examples.map((ex, i) => (
          <div key={i} className="example-card" onClick={() => setPrompt(ex.prompt)}>
            <div className={`badge ${ex.category === "realistic" ? "badge-realistic" : "badge-edge"}`}>
              {ex.category === "realistic" ? "Realistic" : "Edge Case"}
            </div>
            <div className="title">{ex.title}</div>
            <div className="desc">{ex.prompt}</div>
          </div>
        ))}

        {/* Timing summary */}
        {result?.app_spec && (
          <>
            <div className="section-header">Pipeline Timing</div>
            <div style={{ fontSize: 12 }}>
              {Object.entries(result.app_spec.metadata.stage_durations_ms).map(([k, v]) => (
                <div key={k} className="timing-item" style={{ padding: "4px 8px" }}>
                  {STAGE_LABELS[k] || k}: <span className="timing-value">{v}ms</span>
                </div>
              ))}
              <div className="timing-item" style={{ padding: "4px 8px", marginTop: 4, fontWeight: 600 }}>
                Total: <span className="timing-value">{result.app_spec.metadata.total_duration_ms}ms</span>
              </div>
            </div>
          </>
        )}
      </aside>

      {/* Main */}
      <main className="main-content">
        <div className="page-header">
          <h1>AI Software Compiler</h1>
          <p>Transform natural language prompts into validated, executable application configurations</p>
        </div>

        {/* Prompt input */}
        <div className="prompt-section">
          <textarea
            className="prompt-textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the application you want to build..."
            disabled={loading}
          />
          <div className="prompt-actions">
            <button className={`btn-compile ${loading ? "running" : ""}`}
              onClick={handleCompile} disabled={loading || !prompt.trim()}>
              {loading ? "⟳ Compiling..." : "⚡ Compile"}
            </button>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              {mockMode && <span className="mock-badge">Mock Mode</span>}
            </div>
          </div>
        </div>

        {error && !result && (
          <div className="validation-item fail" style={{ marginBottom: 20 }}>
            <span className="validation-icon">❌</span>
            <div>{error}</div>
          </div>
        )}

        {loading && <div className="loading-skeleton" />}

        {/* Stage tabs */}
        {result && (
          <>
            <div className="stage-tabs">
              {STAGE_KEYS.map((key, i) => {
                const stage = getStageData(i);
                const status = stage?.status || "pending";
                return (
                  <button key={key} className={`stage-tab ${activeStage === i ? "active" : ""}`}
                    onClick={() => setActiveStage(i)}>
                    <span className={`status-dot dot-${status}`} />
                    {STAGE_LABELS[key]}
                  </button>
                );
              })}
            </div>
            {renderStageContent(activeStage)}
            {renderAssumptions()}
          </>
        )}
      </main>
    </div>
  );
}
