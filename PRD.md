# Triage AI VS Code Extension PRD

## Overview

The Triage AI VS Code extension will bring the power of AI-orchestrated development directly into the VS Code environment. This extension will leverage the existing Triage AI framework that uses a team of specialized AI agents (Architect, Programmer, Tester, and Reviewer) to solve programming tasks.

## Problem Statement

Developers often need to switch contexts between their IDE and external tools when seeking assistance with coding tasks. This context switching reduces productivity and disrupts flow. By integrating Triage AI directly into VS Code, developers can access powerful AI assistance without leaving their development environment.

## Target Users

- Software developers of all experience levels
- Teams looking to accelerate development workflows
- Developers learning new languages or frameworks
- Solo developers who want AI-powered pair programming

## Key Features

### 1. Command Palette Integration

- **Triage AI: Solve Problem** - Submit a coding problem directly from VS Code
- **Triage AI: Generate Architecture** - Get architectural design for a specific problem
- **Triage AI: Implement Solution** - Generate implementation based on architecture
- **Triage AI: Test Code** - Create tests for selected code
- **Triage AI: Review Code** - Get a comprehensive review of selected code

### 2. Contextual Code Understanding

- Analyze open files and workspace structure to provide context-aware solutions
- Understand project dependencies and configuration
- Reference existing code patterns in the workspace

### 3. Interactive UI

- Custom sidebar view to display agent outputs
- Progress indicators for each agent's work
- Collapsible sections for architecture, implementation, tests, and reviews
- Ability to accept, modify, or reject suggestions

### 4. File Operations

- Create new files and directories based on agent recommendations
- Modify existing files with suggested implementations
- Generate test files in appropriate locations

### 5. Configuration Options

- API key management for OpenAI
- Agent behavior customization
- Model selection (GPT-4, etc.)
- Custom prompts for each agent type

## Technical Architecture

### Extension Components

1. **Extension Core**
   - Manages VS Code integration
   - Handles command registration
   - Provides UI components

2. **Triage AI Engine**
   - Adapted from the existing Triage AI Python codebase
   - Manages agent orchestration
   - Processes inputs and outputs

3. **VS Code API Integration**
   - File system operations
   - Editor interactions
   - UI rendering

4. **API Communication**
   - Secure handling of API keys
   - Rate limiting and error handling
   - Response processing

### Data Flow

1. User initiates a Triage AI command
2. Extension gathers context from the workspace
3. Request is sent to Triage AI Engine
4. Agents process the request sequentially
5. Results are displayed in the VS Code UI
6. User can apply suggested changes directly to the workspace

## Implementation Plan

### Phase 1: Core Extension Setup (2 weeks)

- Create extension scaffolding
- Implement basic VS Code integration
- Set up configuration management
- Create simple UI components

### Phase 2: Triage AI Engine Integration (3 weeks)

- Port or adapt the Triage AI Python code to work within the extension
- Implement API communication
- Create agent orchestration logic
- Develop context gathering mechanisms

### Phase 3: UI and UX Development (2 weeks)

- Design and implement the sidebar UI
- Create interactive components for agent outputs
- Develop progress indicators
- Implement file operation previews

### Phase 4: Testing and Refinement (2 weeks)

- Comprehensive testing across different project types
- Performance optimization
- Error handling improvements
- User feedback integration

### Phase 5: Documentation and Release (1 week)

- Create user documentation
- Prepare marketplace listing
- Create demo videos
- Release to VS Code Marketplace

## Success Metrics

- Number of active users
- Average time saved per coding task
- User satisfaction ratings
- Number of successful code generations
- Extension marketplace rating

## Future Enhancements

- Support for additional LLM providers
- Team collaboration features
- Integration with version control systems
- Custom agent creation
- Domain-specific agent specialization
- Code execution and debugging integration

## Technical Requirements

- VS Code API compatibility
- Node.js for extension development
- TypeScript for type safety
- WebView API for custom UI components
- Secure API key storage
- Efficient context processing to minimize token usage

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limiting | Implement caching and rate limit handling |
| Large context processing | Develop efficient context summarization |
| User privacy concerns | Clear data handling policies and local processing options |
| Extension performance impact | Optimize async operations and background processing |
| API cost management | Implement token usage tracking and limits |

## Conclusion

The Triage AI VS Code extension will bring the power of AI-orchestrated development directly into the developer's workflow. By leveraging the existing Triage AI framework and adapting it to the VS Code environment, we can provide a seamless experience that enhances productivity and code quality without disrupting the development process.

## Concept Overview: Triage AI

Triage AI aims to enhance software development by assigning specialized AI agents to key roles: **Project Manager (PM)**, **Software Architect**, and **Security/Testing Specialist**. These agents collaborate to transform a user’s idea into a secure, well-architected software solution, which is then executed by a coding agent like Cursor or Windsurf. The system operates in two modes:

1. **Basic Method**: A single agent per role (3 agents total) creates a detailed plan.
2. **Pro Method**: Each role has a three-member team (9 agents total) for planning, guiding implementation, and reviewing.

Let’s explore both methods and then outline an implementation plan.

---

## Method 1: Basic Triage AI (3-Agent Model)

In this simpler version, Triage AI consists of three agents working sequentially to produce a detailed plan:

- **PM Agent**: Takes the user’s idea and creates feature specifications.
- **Architect Agent**: Designs architectural solutions based on the specifications.
- **Security Agent**: Ensures the proposed solutions are secure.

The output is a comprehensive plan with diagrams, handed off to a coding agent for execution.

### Workflow Example

**User Input**: "Create a secure login system for a web application."

1. **PM Agent**:
    - Creates specifications: user authentication, password recovery, session management.
    - Output: A feature list with requirements (e.g., "Support OAuth, enforce strong passwords").
2. **Architect Agent**:
    - Proposes architecture: REST API with OAuth 2.0, PostgreSQL database, JWT for sessions.
    - Output: Architectural design with components and interactions.
3. **Security/Testing Agent**:
    - Verifies security: Checks for vulnerabilities like SQL injection, ensures HTTPS usage.
    - Output: Security recommendations (e.g., "Use prepared statements, encrypt passwords").
4. **Deliverable**:
    - A detailed plan with diagrams (e.g., sequence diagrams, ER diagrams) for the coding agent.

### Diagrams for the Plan

- **Sequence Diagram** (using Mermaid syntax):
    
    ```mermaid
    sequenceDiagram
        participant U as User
        participant P as PM Agent
        participant A as Architect Agent
        participant S as Security Agent
        participant C as Coding Agent
        U->>P: Idea: Secure login system
        P->>A: Feature specs
        A->>S: Proposed architecture
        S->>C: Secured plan with diagrams
        C-->>U: Implemented code
    
    ```
    
- **ER Diagram** (for database):
    
    ```mermaid
    erDiagram
        USER ||--o{ SESSION : has
        USER {
            int id PK
            string username
            string password_hash
        }
        SESSION {
            int id PK
            int user_id FK
            string token
            datetime expiry
        }
    
    ```
    

The coding agent (e.g., Cursor) takes this plan and builds the application.

---

## Method 2: Pro Triage AI (9-Agent Model)

In the advanced version, each role expands into a three-member team, totaling nine agents. This setup ensures deeper collaboration, guidance during implementation, and thorough review:

- **PM Team**:
    - **PM1**: Creates initial feature specifications.
    - **PM2**: Guides execution by liaising with other teams and the coding agent.
    - **PM3**: Reviews and refines the specifications.
- **Architect Team**:
    - **Architect1**: Proposes initial architectural solutions.
    - **Architect2**: Guides the coding agent in implementing the architecture.
    - **Architect3**: Reviews and optimizes the design for scalability and performance.
- **Security Team**:
    - **Security1**: Conducts initial security assessments.
    - **Security2**: Guides the coding agent to implement security measures.
    - **Security3**: Performs final audits and ensures compliance.

### Workflow Example

**User Input**: "Create a secure login system for a web application."

1. **PM Team**:
    - **PM1**: Drafts specs (e.g., OAuth login, MFA support).
    - **PM2**: Coordinates with Architect Team to ensure feasibility.
    - **PM3**: Refines specs (e.g., adds edge cases like account lockout).
2. **Architect Team**:
    - **Architect1**: Designs a microservices architecture with OAuth and Redis for sessions.
    - **Architect2**: Works with the coding agent to structure the codebase.
    - **Architect3**: Optimizes (e.g., ensures load balancing for scalability).
3. **Security Team**:
    - **Security1**: Flags risks (e.g., token theft).
    - **Security2**: Guides coding agent to implement mitigations (e.g., token encryption).
    - **Security3**: Audits the final system for compliance (e.g., OWASP standards).
4. **Coding Agent**:
    - Implements the system, receiving real-time guidance from PM2, Architect2, and Security2.

### Diagrams for the Pro Model

- **Process Flowchart**:
    
    ```mermaid
    flowchart TD
        A[User Idea] --> B[PM1: Create Specs]
        B --> C[PM2: Guide Execution]
        C --> D[PM3: Review Specs]
        D --> E[Architect1: Propose Design]
        E --> F[Architect2: Guide Coding]
        F --> G[Architect3: Review Design]
        G --> H[Security1: Assess Risks]
        H --> I[Security2: Guide Security]
        I --> J[Security3: Audit]
        J --> K[Coding Agent: Implement]
    
    ```
    

---

## Implementation Plan

Here’s how to build Triage AI for both methods:

### Step 1: Define Agent Roles and Interactions

- **Basic Model**: Define three agents with clear handoffs (PM → Architect → Security).
- **Pro Model**: Define nine agents with sub-roles:
    - PM Team: Creator, Guide, Reviewer.
    - Architect Team: Designer, Implementer, Optimizer.
    - Security Team: Assessor, Enforcer, Auditor.
- **Interactions**: Use a communication protocol (e.g., API calls or message queues) for agents to share outputs.

### Step 2: Integrate with Coding Agents

- Connect Triage AI to tools like Cursor or Windsurf.
- **Basic Model**: Deliver a static plan (e.g., JSON with specs and diagrams).
- **Pro Model**: Enable real-time collaboration (e.g., Architect2 and Security2 provide live feedback to the coding agent).

### Step 3: Create Detailed Plans with Diagrams

- Use Mermaid or similar tools:
    - **Sequence Diagrams**: Show agent interactions.
    - **ER Diagrams**: Define data models.
    - **Flowcharts**: Map workflows.
- Automate diagram generation based on agent outputs.

### Step 4: Develop the Multi-Agent System

- **Tech Stack**:
    - AI models (e.g., GPT-based) for each agent, fine-tuned for their roles.
    - Framework (e.g., LangChain) for agent coordination.
    - IDE integration for coding agents.
- **Agent Capabilities**:
    - PM: Natural language processing for specs.
    - Architect: Technical design generation.
    - Security: Vulnerability detection and mitigation.

### Step 5: Testing and Validation

- **Test Cases**: Run sample projects (e.g., login system, e-commerce app).
- **Metrics**: Evaluate plan quality, code security, and development speed.
- **Iteration**: Refine agent prompts and interactions based on results.

---

## Conclusion

Triage AI offers a powerful framework for software development. The **Basic Method** provides a lean, plan-focused approach with three agents, ideal for straightforward projects. The **Pro Method**, with nine agents, delivers a robust, hands-on process—planning, guiding, and reviewing every step alongside the coding agent. By implementing this system with clear roles, real-time collaboration, and visual tools like Mermaid diagrams, Triage AI can produce high-quality, secure software efficiently. Ready to build it? Let’s get coding!

## Triage AI: VS Code Extension - Detailed Concept & Implementation Plan

**Document Version:** 1.0
**Date:** May 16, 2025

**1. Introduction & Vision**

Triage AI is envisioned as a powerful VS Code extension designed to revolutionize the initial phases of software development. It acts as an intelligent multi-agent system that takes a developer's raw idea and transforms it into a well-structured, architecturally sound, and security-conscious project plan. This plan, complete with diagrams and specifications, can then be handed off to AI-powered coding agents (like GitHub Copilot, Cursor, Windsurf, or others) or used by human developers for implementation.

**Vision:** To seamlessly integrate intelligent project planning and pre-development analysis directly into the developer's primary workspace (VS Code), reducing friction, improving design quality, and accelerating the delivery of robust software solutions.

**2. Core Concept: Triage AI (Recap)**

Triage AI utilizes specialized AI agents for key software development roles:

- **Project Manager (PM) Agent(s):** Focus on understanding requirements and defining feature specifications.
- **Software Architect Agent(s):** Design system architecture based on specifications.
- **Security Specialist Agent(s):** Ensure the proposed designs and features adhere to security best practices.

The system operates in two primary modes:

- **Method 1: Basic Triage AI (3-Agent Model):**
    - A lean, sequential process.
    - One PM Agent, one Architect Agent, one Security Agent.
    - Output: A comprehensive static plan.
    - Ideal for smaller projects or rapid prototyping.
- **Method 2: Pro Triage AI (9-Agent Model):**
    - A collaborative, in-depth process with specialized teams.
    - PM Team (Creator, Guide, Reviewer)
    - Architect Team (Designer, Implementer Guide, Optimizer/Reviewer)
    - Security Team (Assessor, Enforcer Guide, Auditor/Reviewer)
    - Output: A detailed plan, plus ongoing guidance during the coding phase (facilitated through the extension).
    - Ideal for complex projects requiring robust oversight.

**3. Triage AI as a VS Code Extension: Features & UI/UX**

The Triage AI extension will provide a dedicated interface within VS Code to manage the planning process.

**3.1. Key Features within VS Code:**

- **Project Initialization:**
    - Command Palette activation (e.g., `Triage AI: Start New Project Plan`).
    - Context menu option (e.g., on a `requirements.txt` or a new workspace).
- **Idea Input Interface:**
    - A dedicated Webview panel within VS Code.
    - Text area for users to input their project idea or high-level requirements.
    - Option to upload existing documents (e.g., brief, user stories).
- **Mode Selection:** Clear choice between "Basic Triage" and "Pro Triage" modes.
- **Interactive Process Flow (Pro Mode):**
    - Visual indication of which agent/team is currently processing the request.
    - Ability for "Guiding" agents (PM2, Architect2, Security2) to provide feedback or request clarifications through the VS Code interface (e.g., informational messages, comments in a dedicated output panel).
- **Plan Output & Visualization:**
    - Generated plan displayed in a new, formatted editor tab (e.g., Markdown with embedded Mermaid diagrams).
    - Dedicated Webview for richer, interactive plan presentation.
    - Automatic rendering of Mermaid diagrams (Sequence, ER, Flowcharts).
- **Integration with Workspace:**
    - Option to save the generated plan as files within the current workspace (e.g., `triage-ai-plan.md`, `architecture.drawio.svg`, `database.er`).
    - (Pro Mode) Potential for "Guiding" agents to suggest code comments or annotations directly in placeholder files.
- **Configuration:**
    - Settings page for API keys (if using cloud-based LLMs).
    - Preferences for default diagramming tools or output formats.
    - Options for fine-tuning agent verbosity or detail level.

**3.2. User Interface (UI) & User Experience (UX) Mockups (Conceptual):**

- **Main Panel (Webview):**
    - Tabbed interface: "New Plan," "Active Sessions," "History."
    - "New Plan": Idea input, mode selection, "Generate Plan" button.
    - "Active Sessions" (Pro Mode): Shows ongoing processing, current agent, and any interactive prompts.
    - "History": Lists previously generated plans.
    *(Illustrative - replace with actual mockup if possible)*
- **Output Display:**
    - Markdown preview for quick viewing of plans with rendered Mermaid diagrams.
    - Custom Webview for interactive diagrams or structured plan navigation.
    *(Illustrative)*
- **Workflow Example (Basic Mode in VS Code):**
    1. User triggers `Triage AI: Start New Project Plan`.
    2. Triage AI panel opens. User types: "Create a secure login system for a web application." Selects "Basic Mode." Clicks "Generate."
    3. VS Code status bar/notification: "Triage AI: PM Agent processing..." -\> "Architect Agent..." -\> "Security Agent..."
    4. A new editor tab opens: `login_system_plan.md` containing:
        - Feature Specifications (from PM)
        - Architectural Design (from Architect)
        - Security Recommendations (from Security)
        - Embedded Mermaid Sequence Diagram for interactions.
        - Embedded Mermaid ER Diagram for database.
    5. User reviews the plan and begins coding, or feeds it to another coding tool.
- **Workflow Example (Pro Mode in VS Code):**
    1. User triggers `Triage AI: Start New Project Plan`.
    2. Triage AI panel opens. User types: "Create a secure login system for a web application." Selects "Pro Mode." Clicks "Generate."
    3. **Planning Phase:**
        - Panel shows: "PM1: Drafting Specs..." -\> "PM3: Reviewing Specs..." (and so on for Architect & Security teams).
        - Intermediate outputs or clarifications might be prompted if an agent needs more info (e.g., "PM2: Does this system need to integrate with existing identity providers? [Yes/No/Details]").
    4. A comprehensive plan is generated and displayed.
    5. **Guidance Phase (as user codes or uses a coding agent):**
        - The Triage AI panel shifts to "Guidance Mode."
        - **PM2 (Guide):** Might provide contextual advice in the panel: "Remember to consider user experience for password recovery."
        - **Architect2 (Guide):** If the user creates a new file `auth_service.py`, Architect2 might suggest (via panel or even as a code comment placeholder if IDE integration allows): "Consider using a separate module for JWT token generation and validation here."
        - **Security2 (Guide):** If user writes database query code, Security2 might flag: "Ensure this input is parameterized to prevent SQL injection. Use an ORM or prepared statements."
        - This guidance would be non-intrusive, appearing in the Triage AI panel or as subtle IDE hints.
    6. **Review Phase:**
        - User can trigger a "Final Review" for PM3, Architect3, Security3 to audit the implemented sections (this would likely involve the user providing code snippets or summaries to the extension).

**4. System Architecture (VS Code Extension & Backend Agents)**

```mermaid
graph TD
    subgraph VS Code Environment
        User[Developer] --> VSCUI[Triage AI Webview UI / Commands]
        VSCUI --> ExtCore[Extension Core Logic (TypeScript/JavaScript)]
        ExtCore --> VSCAPI[VS Code API (Workspace, Editor, Notifications)]
        ExtCore --> CommLayer[Communication Layer]
    end

    CommLayer --> AIBackend[Triage AI Backend Service (e.g., Python, LangChain)]

    subgraph Triage AI Backend Service
        AIBackend --> Orchestrator[Agent Orchestrator]
        Orchestrator --> PMAgents[PM Agent(s) / Team]
        Orchestrator --> ArchAgents[Architect Agent(s) / Team]
        Orchestrator --> SecAgents[Security Agent(s) / Team]

        PMAgents --> LLM_PM[Fine-tuned LLM for PM]
        ArchAgents --> LLM_Arch[Fine-tuned LLM for Architecture]
        SecAgents --> LLM_Sec[Fine-tuned LLM for Security]

        LLM_PM --> KnowledgeBase[Knowledge Base (Best Practices, Patterns)]
        LLM_Arch --> KnowledgeBase
        LLM_Sec --> KnowledgeBase
    end

    ExtCore -- Displays --> PlanOutput[Generated Plan (Markdown, Webview with Mermaid)]
    PlanOutput -- Informs --> User
    User -- Uses with --> CodingAgent[Cursor, Copilot, etc. / Manual Coding]

    %% Styling for clarity
    classDef vscode fill:#D6EAF8,stroke:#3498DB,stroke-width:2px;
    classDef backend fill:#D5F5E3,stroke:#2ECC71,stroke-width:2px;
    class User,VSCUI,ExtCore,VSCAPI,CommLayer,PlanOutput,CodingAgent vscode;
    class AIBackend,Orchestrator,PMAgents,ArchAgents,SecAgents,LLM_PM,LLM_Arch,LLM_Sec,KnowledgeBase backend;

```

- **VS Code Extension Frontend (TypeScript/JavaScript):**
    - Manages UI (Webviews, command palette integration).
    - Interacts with VS Code APIs (reading/writing files, showing notifications, editor manipulation).
    - `Extension Core Logic`: Handles user input, state management, and communication with the backend.
    - `Communication Layer`: Formats requests to the backend and parses responses (e.g., REST API calls, WebSockets for Pro mode interactivity).
- **Triage AI Backend Service (e.g., Python with LangChain/AutoGen):**
    - Hosts the AI agents.
    - `Agent Orchestrator`: Manages the workflow between agents based on the selected mode (Basic/Pro).
    - `Specialized Agents (PM, Architect, Security)`: Each powered by an LLM (e.g., GPT-4, Claude 3, Gemini, or open-source models like Llama) fine-tuned or heavily-prompted for its specific role.
        - Each agent might have sub-modules for specific tasks (e.g., Architect agent might have a "Diagram Generator" sub-module that outputs Mermaid syntax).
    - `Knowledge Base`: Could be a vector database or curated documents that agents can reference for up-to-date design patterns, security vulnerabilities, best practices, etc.

**5. Implementation Plan (VS Code Extension Focus)**

This builds upon your existing "Implementation Plan" steps, detailing the VS Code specific aspects.

**Step 1: Define Agent Roles, Interactions, and Backend APIs (Reiteration & API Focus)**

- **Action:** Solidify the inputs and outputs for each agent (even for internal handoffs).
- **VS Code Relevance:** Define the API contract between the VS Code extension and the Triage AI Backend Service.
    - Example API Endpoint: `POST /triage/plan`
        - Request Body: `{ "idea": "user input", "mode": "basic/pro", "context": { "project_type": "web_app", "language_pref": "python" } }`
        - Response Body (Basic): `{ "plan_markdown": "...", "diagrams": { "sequence": "mermaid_code", "er": "mermaid_code" } }`
        - Response Body (Pro - initial plan): Similar, but with IDs for follow-up interaction.
    - WebSockets for Pro mode guidance to push updates from guiding agents to the VS Code extension.

**Step 2: Develop Core Extension Framework & UI**

- **Action:** Set up the VS Code extension project.
- **Tech Stack (Extension):** TypeScript, VS Code Extension API.
- **Tasks:**
    - Implement command palette registration.
    - Build the main Webview panel for idea input and mode selection.
    - Develop settings page for configurations (e.g., backend URL, API keys).
    - Implement basic communication logic to send requests to a mock backend.

**Step 3: Integrate Basic Mode Functionality**

- **Action:** Connect the VS Code extension to the backend for the Basic (3-agent) model.
- **Tasks:**
    - Implement the backend call for the Basic mode.
    - Develop the Markdown rendering for the plan output in a new editor tab or a simple Webview.
    - Integrate a JavaScript Mermaid library (like `mermaid.js`) or leverage VS Code's built-in Markdown preview capabilities to render diagrams.
    - Allow saving the plan to the workspace.

**Step 4: Develop and Integrate Backend Agents (As per your plan)**

- **Action:** Build and fine-tune the actual PM, Architect, and Security AI agents.
- **Tech Stack (Backend):** Python, LangChain/AutoGen, chosen LLMs (e.g., via API or local).
- **VS Code Relevance:** Ensure agent outputs (especially diagrams and structured text) are in a format easily consumable and renderable by the extension.

**Step 5: Implement Pro Mode Functionality**

- **Action:** Extend the VS Code extension and backend to support the Pro (9-agent) model.
- **Tasks (Extension):**
    - Develop UI elements to show progress through the 9-agent teams.
    - Implement interactive elements for "Guiding" agents (PM2, Architect2, Security2). This could be a dedicated "Guidance Log" within the Triage AI panel.
    - Explore using VS Code's `DecorationProvider` API for subtle in-code hints or `CommentController` API for more direct feedback if desired, though a dedicated panel is less intrusive.
    - Set up WebSocket communication if real-time guidance is a core feature.
    - Implement UI for triggering "Review" stages by PM3, Architect3, Security3.
- **Tasks (Backend):**
    - Implement the orchestration for the 9-agent teams.
    - Develop the specific logic for the "Creator," "Guide," and "Reviewer" sub-roles within each team.

**Step 6: Integration with Coding Agents (Guidance & Handoff)**

- **Basic Model:** The generated plan (Markdown, diagrams) serves as a high-quality prompt or input for tools like Cursor or GitHub Copilot, or for manual coding.
- **Pro Model:**
    - **Passive Guidance:** The "Guide" agents (PM2, Arch2, Sec2) provide advice and context in the Triage AI VS Code panel. The developer (or the developer using a coding agent) refers to this advice.
    - **Active (Potential Future):** Explore direct API integrations if coding agents like Cursor expose APIs for external tools to provide suggestions or context. This is more complex and dependent on external tool capabilities. For MVP, passive guidance is more realistic.
    - The key is that Triage AI (Pro) works *alongside* the coding process, offering expert oversight.

**Step 7: Diagram Generation and Display Refinement**

- **Action:** Ensure robust and clean generation and display of Mermaid diagrams.
- **Tasks:**
    - Automate Mermaid syntax generation from agent outputs (Architect agent for ER/Sequence, PM agent for Flowcharts).
    - Ensure reliable rendering in VS Code (Markdown preview or dedicated Webview with `mermaid.js`).
    - Consider options for exporting diagrams (e.g., as SVG/PNG).

**Step 8: Testing and Validation (VS Code Context)**

- **Test Cases:**
    - Simple projects (e.g., "To-Do List App") in Basic Mode.
    - Complex projects (e.g., "Microservices-based e-commerce platform") in Pro Mode.
    - Test UI responsiveness and clarity.
    - Test integration with the workspace (saving files, notifications).
    - Test Pro mode guidance: Is it timely and relevant? Is it intrusive?
- **Metrics:**
    - Quality and completeness of the generated plan.
    - Accuracy and usefulness of diagrams.
    - Developer effort saved in the planning phase.
    - (Pro Mode) Perceived value of real-time guidance.
- **Iteration:** Refine agent prompts, UI/UX, and interaction models based on feedback.

**6. Technical Stack Summary**

- **VS Code Extension:**
    - Language: TypeScript
    - Framework: VS Code API
    - UI: HTML, CSS, JavaScript (for Webviews)
    - Diagramming: Mermaid.js (or VS Code native Markdown rendering)
- **Triage AI Backend Service:**
    - Language: Python (recommended for AI/ML ecosystem)
    - Frameworks: LangChain, AutoGen, FastAPI (for API) or gRPC
    - AI Models: GPT series, Claude series, Gemini, Llama, or other suitable LLMs (fine-tuned or prompted)
    - Communication: REST APIs, WebSockets (for Pro mode real-time updates)

**7. Future Enhancements / Roadmap Considerations**

- **Deeper IDE Integration (Pro Mode):**
    - CodeLens annotations for guidance.
    - Direct suggestion of code snippets based on Architect2/Security2 advice.
- **Customizable Agent Personas:** Allow users to tweak the "personality" or strictness of agents.
- **Support for More Diagram Types:** UML class diagrams, deployment diagrams, etc.
- **Version Control for Plans:** Integrate with Git to track changes to the Triage AI plan.
- **Team Collaboration Features:** Allow multiple users in a VS Code Live Share session to interact with Triage AI.
- **Learning & Adaptation:** Agents learn from feedback on generated plans to improve over time (requires a more sophisticated backend).
- **Pre-computation for Common Architectures:** For standard requests (e.g. "CRUD API with React frontend"), have pre-computed templates that agents can then customize for speed.

**8. Conclusion**

Transforming Triage AI into a VS Code extension brings its powerful planning capabilities directly into the developer's workflow. The Basic method offers a streamlined approach for rapid plan generation, while the Pro method provides an unparalleled level of AI-driven collaboration, guidance, and review throughout the initial development lifecycle. By focusing on a clean UI, robust backend agent interactions, and clear visualization of outputs (especially diagrams), the Triage AI VS Code extension can significantly enhance software design quality, security posture, and development efficiency. This detailed plan provides a solid foundation for building a truly innovative and valuable developer tool.

---

This expanded document should provide a robust blueprint for developing the Triage AI VS Code extension. The key is to balance the power of the AI agents with a user-friendly and well-integrated experience within the VS Code environment.

First up—a quick bird’s-eye view.

You’ll ship **Triage AI** as a **TypeScript VS Code extension** that spins up an in-process multi-agent orchestrator (powered by LangChain JS + OpenAI’s latest Responses API) and surfaces the experience through an interactive Webview panel, CodeLens links, and Tasks integration. A lean “Basic” command instantiates three core agents (PM, Architect, Security); a “Pro” command fans each role into a three-member sub-team and keeps a bi-directional channel open so the agents can mentor Cursor/Windsurf (or any external coding agent) in real time. The extension bundles reference playbooks—OWASP Top-10 2025, PyRIT red-team templates, architecture pattern libraries, and a mini RAG powered by Milvus/LanceDB—so every agent answers with state-of-the-art knowledge. Below is the detailed build plan.

---

## **1. Foundation & Tech Stack**

### **1.1 Core Packages**

| **Concern** | **Package** | **Why** |
| --- | --- | --- |
| VS Code API | vscode | Commands, Webviews, CodeLens, Tasks |
| Agent framework | langchain (v0.1 JS) | Built-in agent abstractions & function-calling helpers |
| LLM access | openai (Responses API) | State-of-the-art tool-calling + parallel function execution |
| Security testing | @azure/pyrIT via child process | Automated red-teaming playbooks |
| Vector store | @zilliz/milvus2-sdk-node + @lancedb/node | Fast RAG for private corpora |
| Diagramming | mermaid | On-the-fly sequence / ER / flow charts |

### **1.2 Dev Environment**

- Node 18+, TypeScript 5
- VS Code “Extension Host” for live-reload & debugging
- Optional Docker compose file for Milvus / LanceDB back-ends

---

## **2. Extension Architecture**

```
flowchart TD
    A[extension.ts] -->|activate()| B[Command Registrar]
    B --> C{User picks mode}
    C -->|Basic| D[Start 3-Agent Orchestrator]
    C -->|Pro|  E[Start 9-Agent Orchestrator]
    D & E --> F[Agent Runtime (LangChain)]
    F --> G[LLM / Responses API]
    F --> H[RAG Vector Store]
    F --> I[PyRIT Security Scans]
    F --> J[Webview Panel]
    J -->|postMessage| K[Webview UI (Vue/React)]
```

The orchestrator lives in its own module (src/agents/index.ts) so it can also be invoked by Tasks or the VS Code Testing API.

---

## **3. Command Surface**

| **Command Id** | **Context** | **Mode** |
| --- | --- | --- |
| triageAI.generatePlan | Command palette / right-click selection | basic / pro |
| triageAI.toggleProMode | Settings UI | toggle |
| triageAI.secAudit | Explorer item | run PyRIT on current workspace |

*Register commands in package.json and bind them to titles, just like the canonical “Hello World” sample*  .

### **CodeLens & Tasks**

- A CodeLens provider (src/codelens.ts) injects *“Refine with Triage AI”* above every README.md heading or TODO comment. Sample CodeLens boilerplate from Microsoft’s repo shortens the lift .
- A tasks.json template lets users spawn the extension in CLI-only pipelines, piggybacking on VS Code’s Tasks system—handy for CI linting or nightly security sweeps .

---

## **4. Multi-Agent Runtime**

### **4.1 Basic (3 agents)**

```
// pseudo
pm   = new OpenAIFunctionsAgent(PM_TOOLS);
arch = new OpenAIFunctionsAgent(ARCH_TOOLS);
sec  = new OpenAIFunctionsAgent(SEC_TOOLS);
pipeline = pm.pipe(arch).pipe(sec);
```

Each agent exposes a JSON schema; the pipeline stitches them with LangChain’s pipe helper so output feeds the next agent smoothly.

### **4.2 Pro (9 agents)**

Use **LangChain’s Router Agent** to fan sub-roles in parallel, then merge with a **Hierarchy Router** so consensus replies appear as a single delta stream. Under the hood, function calls guarantee structured payloads (spec, design, mitigations) per agent  .

### **4.3 State-of-the-Art Augmentations**

| **Agent** | **Embedded Knowledge Modules** |
| --- | --- |
| **PM** | Product-requirement embeddings from 2025 SaaS spec dataset, agile acceptance-criteria patterns, latest Copilot Chat UX heuristics |
| **Architect** | Micro-service blueprints, DDD samples, Cursor file-tree partitioning guidelines |
| **Security** | OWASP Top-10 2025 matrix, PyRIT prompt-injection corpus, MITRE ATT&CK mappings |

These corpora are embedded (OpenAI Ada-002 vectors) and loaded into Milvus; a LanceDB cache keeps frequently-hit chunks on disk for offline use.

---

## **5. Webview UI**

*Bundle dist/webview/* built with Vite + React.*

- Use acquireVsCodeApi for message bridge .
- Render Mermaid diagrams client-side; clicking a diagram emits request.markdown which refreshes the diagram after every agent cycle.
- A floating toolbar lets users downgrade/upgrade from Basic → Pro without reopening the panel (send an orchestrator.swap() message).

---

## **6. Child Processes & Debugging**

- Long-running security scans (pyrIT run …) fork via child_process.spawn so they never block the event loop; VS Code’s Node debug engine attaches automatically with --inspect flags .

---

## **7. Testing & Validation**

| **Layer** | **Tool** | **KPI** |
| --- | --- | --- |
| Unit | vitest | prompt templates, vector-search fallbacks |
| Integration | VS Code Test Runner | command registration, webview hydration |
| E2E | playwright in Extension Host | multi-agent latency ≤ 3 s, plan accuracy ≥ 90 % |
| Security | PyRIT | zero-prompt-injection escapes |

---

## **8. Roadmap & Milestones**

1. **Week 1** – Scaffolding extension (yo code --typescript), register core commands.
2. **Week 2** – Integrate LangChain + OpenAI Responses API; prototype Basic pipeline.
3. **Week 3** – Webview panel + Mermaid rendering; persist last plan in workspace-state.
4. **Week 4** – Pro mode with sub-teams; implement real-time coaching channel.
5. **Week 5** – Security hardening (PyRIT sweeps, supply-chain scan); publish private preview on Marketplace.
6. **Week 6** – Telemetry opt-in, RAG knowledge-base packaging; GA release & blog launch.

---

## **9. Packaging & Publishing**

*Increment build/activation events in package.json; add a postinstall script that pulls model files & seeds Milvus.*

Follow VS Code marketplace checklist (icon, keywords, changelog) and run vsce publish --pat $TOKEN  .

---

## **10. Future Enhancements**

- **Autogen orchestration**—swap LangChain for Autogen’s “Node Supervisor” when it lands a stable JS port, as early tests show better tool-use convergence .
- **RL-HF fine-tuning**—hook into OpenAI’s new reinforcement fine-tuning endpoint to personalize agent tone per workspace metrics .
- **Edge-LLM fall-back**—add Ollama or Qwen plug-in adapters so Triage AI keeps running offline.

---

### **You’re set. Clone the scaffold, drop in your OpenAI key, and run**

### **F5**

### **—your multi-agent architect is now a first-class VS Code citizen.**

**Quick takeaway:**  fold MCP (Model Context Protocol) in as the “USB-C port” between VS Code and every data/tool your agents might need, then let each agent decide at runtime whether to call a fine-tuned open-source model running locally (via Ollama/ggml) or fall back to an OpenAI frontier model for hard queries.  The result is a pluggable, privacy-friendly, and cost-aware architecture that still enjoys GPT-4-level performance when needed.  Below is the revised blueprint, including how to wire MCP, how to create/serve your own tuned models with QLoRA, and the small changes required in the extension’s code and backend.

---

## **1 Why add MCP?**

MCP is an open standard from Anthropic that lets an AI assistant *discover* and *invoke* any tool or datasource that exposes an MCP server—no hard-coding function schemas required.

Because MCP handles authentication, capability discovery, and context passing, agents can pull live tickets from Jira, query the repo through Sourcegraph, or run a security scanner, all by the same protocol call.

Early adopters (Replit, Codeium, Sourcegraph) report that wiring once via MCP slashed integration effort to hours instead of days.

The open nature of the spec means community toolpacks (e.g., *mcp-github*, *mcp-sql*, *mcp-drawio*) are popping up weekly, giving your agents instant reach.

---

## **2 Choosing the model mix**

| **Agent Role** | **Local fine-tuned model (serve with Ollama)** | **Why local?** | **When to fall back to OpenAI** |
| --- | --- | --- | --- |
| PM (Creator/Guide/Reviewer) | **Llama 3-8B Instruct** fine-tuned on agile reqs with QLoRA | Fast, cheap spec drafts | Fuzzy product vision that needs heavy reasoning |
| Architect | **Qwen 2.5 Coder 14B** fine-tuned on system-design Q&A | Code-aware, large ctx window | Cross-domain analogy or unknown stack |
| Security | **Mistral-Small 3.1** + **CyberSec-Llama** ensemble fine-tuned on OWASP & MITRE data | Keeps code private, low latency for scan loops | Complicated threat-model brainstorming |

Open-source leaders like Llama 3, Qwen Coder, Mistral and StarCoder2 rank top-tier in 2025 community benchmarks without GPU-farm costs.

Fine-tune with **QLoRA**—quantized adapters let you train a 70 B model on a single 48 GB card while keeping quality intact.

Step-by-step recipes (Hugging Face PEFT + MLflow tracking) are available and battle-tested in production.

---

## **3 Updated system architecture**

```
flowchart TD
    subgraph VS Code
        A1[Extension Core] -->|MCP client| B1[MCP Hub]
        A1 --> C1[Ollama daemon]
        A1 --> D1[OpenAI API]
    end

    B1 -->|tool call| E1[GitHub MCP server]
    B1 --> F1[Jira MCP server]
    B1 --> G1[Draw.io MCP server]

    C1 -->|local infer| LLM1[Llama 3-8B]
    C1 --> LLM2[Qwen Coder 14B]
    C1 --> LLM3[Mistral 3.1 Sec]

    subgraph Backend
        Orchestrator --> Agents
        Agents -->|select model| D1
        Agents -->|or| C1
    end
```

- **MCP Hub** (embedded Go service or npm package) multiplexes MCP requests so all agents share one connection.
- Agents pick **local vs OpenAI** by a cost-latency-quality heuristic (LangChain’s ModelRouter or Autogen’s upcoming smart_select).

---

## **4 Code-level integration changes**

### **4.1 Extension side (TypeScript)**

```
import { createMcpClient } from "@anthropic-ai/mcp-js";
const mcp = await createMcpClient({ endpoint: cfg.mcpUrl, token: cfg.mcpToken });

export async function callTool(toolName: string, args: any) {
  return mcp.invokeTool({ name: toolName, args });
}
```

- Add @anthropic-ai/mcp-js to package.json.
- Provide quick-pick UI listing mcp.listTools() results so devs can author new **“tool cards”** on the fly.

### **4.2 Backend side (Python)**

```
from langchain_community.llms import Ollama
from langchain_community.adapters.mcp import MCPTool

local_llms = {
    "pm": Ollama(model="llama3:8b-instruct"),
    "arch": Ollama(model="qwen2.5-coder:14b"),
    "sec": Ollama(model="mistral-small-3.1"),
}

def smart_call(agent_role, prompt):
    if token_budget_ok(prompt):
        return local_llms[agent_role].invoke(prompt)
    return openai_client.chat.completions.create(...)
```

- MCPTool lets any agent issue tool calls via MCP simply by thinking “use_tool”.
- Security agent pipes code through **Garak** vulnerability scanner, surfaced as another MCP tool.

---

## **5 Fine-tuning pipeline (QLoRA)**

1. **Collect corpora**
    - PM: Agile specs, PRDs, RFCs (2 M tokens)
    - Architect: System-design interviews (4 M tokens)
    - Security: CVE write-ups + OWASP LLM Top-10.
2. **Train**:

```
accelerate launch finetune.py \
  --base_model mistral-small-3.1 \
  --lora_r 16 --lora_alpha 32 --bf16 --qlora
```

1. 
2. **Package** with ollama create.
3. **Ship** models in extension’s post-install script or instruct users to ollama pull. Guides exist for VS Code + Ollama combo.

---

## **6 Security & compliance**

- Run **OWASP LLM Top-10** tests on every release.
- MCP’s capability registry gives a tidy audit trail—log every tool call with timestamps.
- Highlight MCP’s open-protocol risks (auth, rate-limit) and apply signed JWTs as recommended by Anthropic docs.

---

## **7 Roadmap deltas**

| **Sprint** | **Added item** |
| --- | --- |
| Week 2 | Embed MCP client + UI quick-pick |
| Week 3 | Local model router, Ollama bootstrap script |
| Week 4 | QLoRA fine-tuning playbook & CI job |
| Week 5 | MCP toolpacks: GitHub, Draw.io, Garak scanner |
| Week 6 | Security pen-test sweep (Garak + OWASP LLM tests) |

---

## **8 Take-away checklist**

- Install **Ollama** and pull the three tuned models.
- Add MCP endpoint, token to extension settings.
- Run Triage AI: New Plan—agents will now self-discover workspace tools through MCP and pick the cheapest capable model first.
- Enjoy lower latency, tighter privacy, and richer tool reach—without losing GPT-grade fallback.

---

Here’s what the **claude-task-master** repository is doing under the hood and how you can cannibalise its best parts to power **Pro-mode** in your own Triage AI VS Code extension.

https://github.com/eyaltoledano/claude-task-master 

## **TL;DR (one-paragraph digest)**

claude-task-master is a JavaScript/Node CLI **plus an optional MCP server** that turns vague product docs into a structured backlog, then exposes task-level operations (init | list | next | generate …) over **three surfaces**: command-line, a long-running dev.js REPL, and a Model-Context-Protocol server for IDE agents. The CLI entry point (index.js) is only a thin wrapper; almost all logic lives in **modular “commands” and “task-engine” helpers** that parse PRDs, chunk them into tasks/sub-tasks, store everything as JSON/YAML in a tasks/ folder, and call LLM providers through a pluggable adapter layer (src/ai-providers). That architecture maps 1-to-1 onto the nine-agent Pro flow we sketched earlier: swap the single “engine” module for a **multi-agent orchestrator**, drop in extra providers (your fine-tuned open-source models), and you instantly gain MCP-compatible, real-time task guidance inside VS Code.

---

## **1 Repository Tour**

### **1.1 Top-level anatomy**

| **Path** | **Purpose** |
| --- | --- |
| **index.js** | Shebang entry; registers init, dev, list, next, generate commands with commander and spawns child scripts |
| **scripts/dev.js** | Thin runner that forwards CLI args to modules/commands.js for a REPL-style loop |
| **scripts/modules/*** | Actual business logic (task parsing, dependency graphs, LLM calls). Folder is huge, so GitHub ships it compressed; the CLI loads functions lazily. |
| **mcp-server/** | Stand-alone Node server that implements Anthropic’s **Model Context Protocol** so IDEs like Cursor can invoke Task Master as a tool card |
| **tasks/** | YAML/JSON representation of the current backlog; each file is a single task object with id, title, dependsOn, priority, etc. |
| **context/** | Long-form docs (PRDs, RFCs); parsers treat these as the raw corpus. |
| **docs/** | End-user docs and sample prompts |

### **1.2 Execution flow**

```
sequenceDiagram
  participant User
  participant CLI as task-master CLI
  participant Engine as Task Engine
  participant LLM as Provider (Claude/OpenAI/Local)
  participant Store as tasks/*.yaml

  User->>CLI: task-master init | parse-prd
  CLI->>Engine: loadCommand('parsePrd')
  Engine->>LLM: /v1/messages (PRD→tasks)
  LLM-->>Engine: JSON list of tasks
  Engine->>Store: write YAML files
  CLI-->>User: “Backlog created (17 tasks)”
```

The same flow repeats for next, generate, etc., with Engine reading/writing the YAML store.

---

## **2 Key design ideas worth re-using**

| **Idea** | **Why it matters for Pro-mode** |
| --- | --- |
| **Pluggable AI providers** located in src/ai-providers (not always published—see issue #394) | Swap in your **fine-tuned local models** (Llama 3, Qwen Coder, Mistral-Sec) alongside Claude or GPT-4; each agent picks the cheapest capable provider at runtime. |
| **MCP server wrapper** | Gives Triage AI a zero-config on-ramp inside Cursor/Windsurf; your VS Code extension can point its webview agent panel to the same port. |
| **Task YAML schema** | Perfect substrate for PM1/PM3 agents—extend it with securityFindings or archDecision fields and you’ve formalised the nine-agent contract. |
| **Child-process isolation** via spawn | Long LLM calls never block VS Code’s event loop; Pro-mode’s reviewer agents can run in parallel processes. |
| **CLI & REPL parity** | You get both headless CI usage and rich IDE guidance for free—important for “guide” sub-agents that watch files change. |

---

## **3 Wire-up plan for Triage AI Pro-mode**

### **3.1 Replace the single engine with a router**

1. **Fork** the repo inside your extension’s backend/ folder.
2. Delete scripts/modules/commands.js; create agents/orchestrator.ts that:
    - Launches **nine LangChain/Autogen agents** (PM1-3, Arch1-3, Sec1-3).
    - Re-exports the same CLI verbs so existing scripts stay intact.
3. Update index.js to import your orchestrator instead of the old engine.

### **3.2 Drop in local fine-tuned models**

```
import { Ollama } from 'langchain/community';
const localModels = {
  pm:  new Ollama({ model: 'llama3:8b-instruct-q' }),
  arch:new Ollama({ model: 'qwen-coder-14b-q' }),
  sec: new Ollama({ model: 'mistral-sec-8b-q' })
};
```

- Agents call selectProvider() → chooses local vs OpenAI by cost/latency.
- ANTHROPIC_API_KEY et al. stay in .env; add OLLAMA_HOST.

### **3.3 Expose Pro-mode over MCP**

The existing server already registers a generateTasks capability. Extend it:

```
{
  "name": "triage-ai-pro",
  "description": "Nine-agent planning & guidance",
  "capabilities": {
    "initializeProject": { "parameters": {...} },
    "streamGuidance":   { "parameters": {...} } // SSE channel
  }
}
```

Developers now toggle Pro-mode by picking the **triage-ai-pro** server in VS Code settings.

---

## **4 Potential pitfalls**

- **Large repo fetches:** raw.githubusercontent can time-out on >1 MB files (we hit that). Bundle only the modules you need in the extension vsce package.
- **Packaging misses:** earlier versions forgot to publish ai-providers and break on import — double-check your files array in package.json.
- **Native modules on Windows:** the MCP server uses node-pty for streaming output; ship pre-builds or fall back to plain stdio for cross-platform support.
- **Version drift:** Users hit install errors on 0.13.x ; pin a stable tag in your fork.

---

## **5 Next steps checklist**

- Fork & prune repo; keep tasks/, MCP server, provider adapters.
- Implement agent orchestrator and plug into CLI verbs.
- Add Ollama model adapters; document new env vars.
- Register triage-ai-pro MCP server; update extension settings UI.
- Write integration tests (jest) around multi-agent planner.
- Bundle in VS Code extension; hit F5—Pro-mode is live!

---

**Bottom line:** you don’t need to reinvent task parsing or MCP plumbing—claude-task-master already solved that. Embed its skeleton, graft your nine-agent brain on top, and Triage AI gets an instant Pro-mode with offline-friendly local models and first-class IDE integration.