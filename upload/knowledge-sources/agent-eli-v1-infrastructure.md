# Agent Eli v1 — Infrastructure & Config

services:
  eli:
    build: ../backend
    ports:
      - "8000:8000"
    env_file:
      - ../.env
    depends_on:
      - postgres
      - redis
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: agent_eli
      POSTGRES_USER: eli
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - eli_postgres:/var/lib/postgresql/data
  redis:
    image: redis:7-alpine
    volumes:
      - eli_redis:/data
volumes:
  eli_postgres:
  eli_redis:


{
  "name": "agent-eli-v1",
  "version": "1.0.0",
  "private": true,
  "description": "Human-led AI SEO operating system and public portfolio prototype",
  "scripts": {
    "preview": "python -m http.server 4173 -d frontend/public"
  }
}