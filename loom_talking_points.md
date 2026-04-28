# Loom Demo Talking Points (5–10 minutes)

## Opening (30 seconds)
- "This is a compiler-style system that converts natural language product prompts into strict, validated, executable application configurations."
- "It's not a single-prompt wrapper — it's a modular, multi-stage pipeline with real validation and repair."

---

## 1. Architecture Overview (1.5 minutes)

**Show the architecture diagram from README.**

- 5 discrete pipeline stages, each a separate module:
  1. **Intent Extraction** — NLP to structured intent
  2. **System Design** — Intent to architecture plan
  3. **Schema Generation** — Architecture to 5 typed schemas (UI, API, DB, Auth, Business Rules)
  4. **Refinement & Repair** — Cross-layer validation + targeted repair
  5. **Execution Validation** — Proves the output is actually usable

- Why compiler-like: deterministic, typed, staged, repairable — not a black-box prompt.

---

## 2. Live Demo (2 minutes)

**Run the CRM prompt end-to-end in the UI.**

- Enter: "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
- Click Compile
- Walk through each stage tab:
  - Intent: show extracted features, roles, monetization, ambiguities
  - System Design: show modules, page map, entity model
  - Schema Generation: flip through UI → API → DB → Auth → Business Rules sub-tabs
  - Refinement: show repair report — issues found, repaired, cycles
  - Execution: show readiness score and check results

---

## 3. Validation & Repair Engine (2 minutes)

**This is the core differentiator.**

- Cross-layer consistency checks:
  - UI form fields ↔ API request fields
  - API endpoints ↔ DB tables
  - Protected pages ↔ auth route_access
  - Permissions ↔ defined roles
  - Premium flags consistent across UI, API, and business rules
  - Navigation routes → actual pages

- Repair is **targeted**, not brute retry:
  - RepairPlanner analyzes each issue and decides fix type
  - TargetedRegenerator patches only the broken part
  - Re-validates after repair
  - Max 3 cycles to prevent infinite loops

- Show a concrete example: "Settings page had no auth route_access → repair engine auto-added it"

---

## 4. Strict Schema Enforcement (1 minute)

- Every stage output is validated against Pydantic v2 models
- `extra = "forbid"` — no hallucinated fields
- Required fields, enums, type safety
- If LLM returns invalid JSON → caught immediately, not silently passed

---

## 5. Determinism & Reliability (1 minute)

- Low temperature (0.1)
- Fixed prompt templates per stage
- Schema-first parsing
- Mock mode: works without API key with deterministic outputs
- Handles vague prompts: detects ambiguities, records assumptions

---

## 6. Evaluation Framework (1 minute)

- 20 prompts: 10 realistic + 10 edge cases
- Metrics tracked: success rate, repair count, latency, execution score
- Benchmark runner produces JSON report
- Edge cases test: vague, conflicting, incomplete, single-word prompts

---

## 7. Cost vs. Quality Tradeoff (30 seconds)

- 7 LLM calls per pipeline run (1 intent + 1 design + 5 schemas)
- Repair uses targeted fix, not full regeneration — saves ~5x cost
- Mock mode for development — zero cost
- Each stage is independently cacheable

---

## 8. Future Improvements (30 seconds)

- Parallel schema generation (currently sequential)
- Streaming stage results to frontend
- Code stub generation from final spec
- Prompt history and versioning
- Diff-based modification (change requirements mid-way)

---

## Closing (15 seconds)
- "The key insight: treat LLM output like compiler output — typed, validated, repairable."
- "This isn't AI-generated fluff — it's an engineered system with real guarantees."
