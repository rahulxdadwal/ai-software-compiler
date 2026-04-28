.PHONY: setup backend frontend dev test benchmark clean

# Setup everything
setup: setup-backend setup-frontend
	@echo "✅ Setup complete. Run 'make dev' to start."

setup-backend:
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

setup-frontend:
	cd frontend && npm install

# Run backend
backend:
	cd backend && . venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run frontend
frontend:
	cd frontend && npm run dev

# Run both (requires two terminals — use run.sh instead)
dev:
	@echo "Use ./run.sh to start both servers, or run 'make backend' and 'make frontend' in separate terminals."

# Run tests
test:
	cd backend && . venv/bin/activate && python -m pytest tests/ -v

# Run benchmark
benchmark:
	cd backend && . venv/bin/activate && python -m evaluation.benchmark_runner

# Clean
clean:
	rm -rf backend/venv backend/__pycache__ backend/**/__pycache__
	rm -rf frontend/node_modules frontend/.next
