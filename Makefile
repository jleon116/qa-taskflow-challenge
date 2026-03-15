.PHONY: help start stop seed test-api test-ui test-perf test-all

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

start: ## Levantar la aplicación
	docker compose up -d --build
	@echo "⏳ Esperando a que la app esté lista..."
	@sleep 5
	@echo "✅ App disponible en http://localhost:8080"

stop: ## Detener la aplicación
	docker compose down -v

seed: ## Poblar datos de prueba
	pip install requests --quiet --break-system-packages 2>/dev/null || true
	python scripts/seed.py

restart: stop start seed ## Reiniciar todo desde cero con datos frescos

# ── El candidato debe implementar estos targets ──

test-api: ## Ejecutar tests de API
	@echo "❌ TODO: Implementar tests de API"

test-ui: ## Ejecutar tests de UI (E2E)
	@echo "❌ TODO: Implementar tests de UI"

test-perf: ## Ejecutar tests de rendimiento
	@echo "❌ TODO: Implementar tests de rendimiento"

test-all: test-api test-ui test-perf ## Ejecutar todos los tests
