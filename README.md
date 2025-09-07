# KubeBoy 🤖

A Kubernetes assistant powered by LangGraph and OpenAI that helps you explore and understand your Kubernetes cluster through natural language conversations.

## Features

- **Read-only cluster exploration** - Safely query your cluster without making changes
- **Natural language interface** - Ask questions in plain English
- **Comprehensive resource coverage** - Query pods, deployments, services, nodes, namespaces, and events
- **Interactive chat** - Conversational interface for exploring your cluster
- **Cluster summaries** - Get high-level overviews of your cluster health

## Setup

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Ensure Kubernetes access**:
   Make sure you have access to a Kubernetes cluster and `kubectl` is configured properly.

## Usage

Run the interactive chat interface:

```bash
poetry run python main.py
```

### Example Questions

- "Show me all pods"
- "What deployments are running in the default namespace?"
- "Give me a cluster summary"
- "Show me recent events"
- "Are there any failed pods?"
- "What nodes do I have and what's their status?"
- "List all namespaces"
- "Show me services in the kube-system namespace"

## Architecture

KubeBoy uses:
- **LangGraph** for agent workflow orchestration
- **OpenAI GPT-4o-mini** for natural language understanding
- **Kubernetes Python client** for cluster API access
- **Read-only tools** for safe cluster exploration

The agent can only perform read operations - it cannot modify your cluster in any way.
