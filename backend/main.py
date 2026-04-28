"""FastAPI application — main entry point for the backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline.orchestrator import PipelineOrchestrator
from schemas.final_app_spec_schema import PipelineResponse
from config import settings

app = FastAPI(
    title="AI Software Compiler",
    description="Compiler-style pipeline that converts NL prompts into executable app specifications",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompileRequest(BaseModel):
    prompt: str


class HealthResponse(BaseModel):
    status: str
    mock_mode: bool
    version: str


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", mock_mode=settings.use_mock, version="1.0.0")


@app.post("/api/compile", response_model=PipelineResponse)
async def compile_prompt(request: CompileRequest):
    """Run the full compilation pipeline on a product prompt."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    orchestrator = PipelineOrchestrator()
    result = await orchestrator.run(request.prompt.strip())
    return result


@app.get("/api/examples")
async def get_examples():
    """Return example prompts for the UI."""
    return {
        "examples": [
            {
                "title": "CRM Platform",
                "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
                "category": "realistic",
            },
            {
                "title": "E-Commerce Store",
                "prompt": "Create an online store with product listings, shopping cart, checkout with Stripe, admin panel for inventory management, customer reviews, and order tracking.",
                "category": "realistic",
            },
            {
                "title": "Learning Management System",
                "prompt": "Build a learning management system with courses, quizzes, student progress tracking, instructor dashboard, certificate generation, and discussion forums.",
                "category": "realistic",
            },
            {
                "title": "Vague Prompt",
                "prompt": "Make me an app for managing stuff",
                "category": "edge_case",
            },
            {
                "title": "Conflicting Requirements",
                "prompt": "Build a free app with premium features. All users should have admin access but restrict sensitive data to admins only.",
                "category": "edge_case",
            },
        ]
    }
