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
graph TD
    subgraph CodeBuddy
        B[Orchestrator Agent]
        C[ErrorExtractor Agent]
        D[StackRedHub Agent]
    end

    %% Place MCP Server and Opik side by side
    E[MCP Server] --- F[Opik Observability]

    %% Agent connections (parallel, no crossing)
    B -- Connects To --> E
    B -- Connects To --> F
    C -- Connects To --> E
    C -- Connects To --> F
    D -- Connects To --> E
    D -- Connects To --> F

    %% MCP Server connects to Tools
    E -- Utilizes --> G[Tools & APIs]
