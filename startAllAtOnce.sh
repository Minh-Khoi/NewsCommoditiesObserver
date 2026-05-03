#!/bin/bash

# 1. Infrastructure Setup (The "Thế" - Strategic Foundation)
echo "Creating shared networks..."
docker network create shared_pipeline 2>/dev/null || true
docker network create rag_internal 2>/dev/null || true

# 2. Start Crawler & LLM Systems (Infrastructure & Intelligence)
echo "Starting Infrastructure Stacks..."
docker-compose -f docker-compose.ollama.yml -p commodities-llm up -d
docker-compose -f docker-compose.crawler.yml -p commodities-crawler up -d

# 3. Performance Awareness: Wait for RabbitMQ to be healthy
# This prevents the RAG system from crashing on startup
echo "Waiting for intelligence_hub (Ollama) and Message Broker to stabilize..."
sleep 15 

# 4. Start RAG System (Intelligence Engine)
echo "Starting RAG Stack..."
docker-compose -f docker-compose.RAG.yml -p commodities-rag up -d

# 5. Start Evaluator System (The Judge)
echo "Starting Evaluator Stack..."
docker-compose -f docker-compose.evaluator.yml -p commodities-eval up -d

echo "All systems are running concurrently."
docker compose ls