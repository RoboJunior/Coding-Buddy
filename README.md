# CodeBuddy: Multi-Agent Orchestrator with Error Resolution

CodeBuddy is a multi-agent system designed to help developers troubleshoot and resolve errors faster. It leverages an **Orchestrator-Agent** architecture with specialized agents that can extract errors from logs/screenshots and resolve them using community-driven knowledge sources like GitHub, Reddit, and StackOverflow.  

It also integrates with a dedicated **MCP server** for tool access and **Opik** for observability, ensuring full visibility into agent behaviors.  

---

## 🚀 Features

- **Orchestrator Agent** – Routes tasks to the most suitable agent based on context and available tools.  
- **Error Extractor Agent** – Extracts and interprets error messages from logs or images.  
- **StackRedHub Agent** – Searches GitHub, Reddit, and StackOverflow for potential resolutions.  
- **MCP Server** – Provides a unified tool layer for agents to interact with.  
- **Agent Observability with Opik** – Monitor and analyze agent behavior in real time.  
- **CodeBuddy CLI** – Interactive developer companion to debug errors seamlessly.  

---

## 🏗️ Architecture

```mermaid
flowchart LR
  %% Placement & main flow
  U[Users] --> LB[Load Balancer]
  LB --> ORC[Orchestrator Agent<br/>(Deployment · Secret · ConfigMap)]

  subgraph AGENTS[Agents Layer]
    direction TB
    ERR[Error Tracer Agent<br/>(Deployment · Secret · ConfigMap)]
    SRH[StackRedHub Agent<br/>(Deployment · Secret · ConfigMap)]
  end

  %% Core broker / server
  MCP[MCP Server<br/>(Deployment · Secret · ConfigMap)]

  %% External tools
  TOOLS[Tools & APIs]

  %% Main solid flows (control/data)
  ORC -->|Cluster IP →| ERR
  ORC -->|Cluster IP →| SRH
  ORC -->|register / send events →| MCP

  ERR -->|submit errors →| MCP
  SRH -->|push stacks →| MCP
  MCP -->|call / proxy →| TOOLS

  %% Observability (dashed = monitoring/telemetry)
  subgraph OPIK[Opik Observability]
    OP[Opik]
  end

  ORC -.->|metrics / traces| OP
  ERR -.->|error events| OP
  SRH -.->|logs / alerts| OP
  MCP -.->|server telemetry| OP

  %% Optional arrows (match your diagram: agents also feed Opik and MCP)
  ORC -->|(also) push telemetry →| OP
  ERR -->|(also) API →| TOOLS

  %% Legend
  classDef dashed stroke-dasharray: 5 5;
  style OP stroke:#333,stroke-dasharray: 5 5

