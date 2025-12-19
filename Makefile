.PHONY: help install install-backend install-frontend start start-mock start-backend start-frontend stop clean logs

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)OneCard Bot - Available Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install Python dependencies
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

install-frontend: ## Install Node.js dependencies
	@echo "$(GREEN)Installing Node.js dependencies...$(NC)"
	cd onecard-bot && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

setup-db: ## Initialize and seed the database
	@echo "$(GREEN)Setting up database...$(NC)"
	python3 setup_database.py
	@echo "$(GREEN)✓ Database initialized$(NC)"

start: ## Start all services (requires 3 terminals or use start.sh/start.py)
	@echo "$(YELLOW)Starting all services...$(NC)"
	@echo "Mock API:    python3 mock_apis.py"
	@echo "Backend:     python3 backend.py"
	@echo "Frontend:    cd onecard-bot && npm run dev"
	@echo ""
	@echo "$(YELLOW)Or use: make start-all-in-one$(NC)"

start-all-in-one: ## Start all services in one command (background)
	@mkdir -p logs
	@echo "$(GREEN)Starting all services in background...$(NC)"
	@python3 mock_apis.py > logs/mock_api.log 2>&1 &
	@sleep 2
	@python3 backend.py > logs/backend.log 2>&1 &
	@sleep 3
	@cd onecard-bot && npm run dev > ../logs/frontend.log 2>&1 &
	@echo "$(GREEN)✓ All services started!$(NC)"
	@echo "$(YELLOW)Check logs/ directory for output$(NC)"
	@echo "$(YELLOW)Use 'make stop' to stop all services$(NC)"

start-mock: ## Start only Mock API server
	@echo "$(GREEN)Starting Mock API Server...$(NC)"
	python3 mock_apis.py

start-backend: ## Start only Backend server
	@echo "$(GREEN)Starting AI Backend Server...$(NC)"
	python3 backend.py

start-frontend: ## Start only Frontend server
	@echo "$(GREEN)Starting Frontend Dev Server...$(NC)"
	cd onecard-bot && npm run dev

stop: ## Stop all running services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@pkill -f "mock_apis.py" || true
	@pkill -f "backend.py" || true
	@pkill -f "vite" || true
	@echo "$(GREEN)✓ All services stopped$(NC)"

clean: ## Clean up logs and cache files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@rm -rf logs/
	@rm -rf __pycache__/
	@rm -rf onecard-bot/node_modules/.vite
	@find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

logs: ## Show logs from all services
	@echo "$(GREEN)Recent logs:$(NC)"
	@echo "$(YELLOW)--- Mock API ---$(NC)"
	@tail -n 10 logs/mock_api.log 2>/dev/null || echo "No logs found"
	@echo ""
	@echo "$(YELLOW)--- Backend ---$(NC)"
	@tail -n 10 logs/backend.log 2>/dev/null || echo "No logs found"
	@echo ""
	@echo "$(YELLOW)--- Frontend ---$(NC)"
	@tail -n 10 logs/frontend.log 2>/dev/null || echo "No logs found"

dev: install setup-db start ## Full development setup (install + setup + start)

