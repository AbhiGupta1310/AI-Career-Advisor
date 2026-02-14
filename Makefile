# ============================================================
# Makefile — AI Career Advisor
# ============================================================

.PHONY: install api frontend dev build test lint clean

# Install all dependencies
install:
	pip install -r requirements.txt
	cd frontend && npm install

# Start FastAPI backend (development)
api:
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Start React frontend (development)
frontend:
	cd frontend && npm run dev

# Start both (API in background, frontend in foreground)
dev:
	@echo "🚀 Starting API server in background..."
	uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload &
	@echo "🎨 Starting React frontend..."
	cd frontend && npm run dev

# Build React for production
build:
	cd frontend && npm run build

# Run tests
test:
	pytest tests/ -v

# Lint code
lint:
	ruff check app/ scripts/ tests/
	ruff format --check app/ scripts/ tests/

# Format code
format:
	ruff format app/ scripts/ tests/


# Clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".DS_Store" -delete 2>/dev/null || true
	rm -rf frontend/dist
