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
    A[Users] --> B{Load Balancer}

    subgraph Orchestrator Agent
        OAD[Deployment]
        OAC[ConfigMap]
        OAS[Secret]
        OAP[Cluster IP]
        OAD --- OAC
        OAD --- OAS
    end

    subgraph Error Tracer Agent
        ETAD[Deployment]
        ETAC[ConfigMap]
        ETAS[Secret]
        ETAP[Cluster IP]
        ETAD --- ETAC
        ETAD --- ETAS
    end

    subgraph Stackredhub Agent
        SRHAD[Deployment]
        SRHAC[ConfigMap]
        SRHAS[Secret]
        SRHAP[Cluster IP]
        SRHAD --- SRHAC
        SRHAD --- SRHAS
    end

    subgraph Mcp Server
        MSD[Deployment]
        MSC[ConfigMap]
        MSS[Secret]
        MSP[Cluster IP]
        MSD --- MSC
        MSD --- MSS
    end

    Opik(Opik)

    B --> OAP
    OAP --> ETAP
    OAP --> SRHAP

    ETAP --> MSP
    SRHAP --> MSP

    MSP --> Opik
    OAP --> Opik
    SRHAP --> Opik
```

---
## ⚙️Getting Started
