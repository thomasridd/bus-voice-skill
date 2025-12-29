.PHONY: help install install-dev test lint format security coverage clean deploy deploy-dev deploy-prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	cd lambda && pip install -r requirements.txt

install-dev: ## Install all dependencies including dev tools
	cd lambda && pip install -r requirements.txt -r requirements-dev.txt

test: ## Run unit tests
	cd lambda && python -m unittest discover -s tests -p "test_*.py" -v

coverage: ## Run tests with coverage report
	cd lambda && coverage run -m unittest discover -s tests -p "test_*.py"
	cd lambda && coverage report
	cd lambda && coverage html
	@echo "Coverage report generated in lambda/htmlcov/index.html"

lint: ## Run linting checks
	cd lambda && ruff check .

lint-fix: ## Run linting and auto-fix issues
	cd lambda && ruff check . --fix

format: ## Check code formatting
	cd lambda && ruff format --check .

format-fix: ## Format code automatically
	cd lambda && ruff format .

security: ## Run security scans
	cd lambda && bandit -r . -ll -x ./tests

check-deps: ## Check for vulnerable dependencies
	cd lambda && pip install safety && safety check

ci: lint format test security ## Run all CI checks locally
	@echo "All CI checks passed!"

clean: ## Remove temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf lambda/htmlcov lambda/.coverage lambda/coverage.xml
	rm -f deployment-package.zip response.json

build: ## Build SAM application
	sam build

validate: ## Validate SAM template
	sam validate

deploy-dev: ## Deploy to dev environment
	sam build
	sam deploy --config-env dev

deploy-prod: ## Deploy to prod environment
	sam build
	sam deploy --config-env prod

local-test: ## Test Lambda locally with SAM
	sam local invoke -e test-event.json

logs-dev: ## Tail Lambda logs from dev environment
	sam logs --stack-name tfl-bus-checker-dev --tail

logs-prod: ## Tail Lambda logs from prod environment
	sam logs --stack-name tfl-bus-checker-prod --tail
