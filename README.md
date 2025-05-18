# Triage AI

<p align="center">
  <img src="https://via.placeholder.com/200x200?text=Triage+AI" alt="Triage AI Logo" width="200" height="200">
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

## 🚀 Vision

Triage AI is a powerful VS Code extension that brings AI-orchestrated development directly into your workflow. It leverages a team of specialized AI agents (Architect, Programmer, Tester, and Reviewer) to transform your ideas into well-structured, architecturally sound, and security-conscious project plans.

Unlike traditional AI coding assistants, Triage AI focuses on the critical pre-implementation phase, ensuring your projects start with solid foundations before a single line of code is written.

## ✨ Features

### Multi-Agent Orchestration

Triage AI operates in two powerful modes:

#### Basic Mode (3-Agent Model)
- **PM Agent**: Takes your idea and creates detailed feature specifications
- **Architect Agent**: Designs architectural solutions based on the specifications
- **Security Agent**: Ensures the proposed solutions are secure and robust

#### Pro Mode (9-Agent Model)
Each role expands into a three-member team for deeper collaboration:
- **PM Team**: Creator, Guide, Reviewer
- **Architect Team**: Designer, Implementer, Optimizer
- **Security Team**: Assessor, Enforcer, Auditor

### Seamless VS Code Integration

- **Command Palette Integration**: Submit problems, generate architecture, implement solutions, test and review code
- **Contextual Understanding**: Analyzes your workspace for context-aware solutions
- **Interactive UI**: Custom sidebar with progress indicators and collapsible sections
- **Diagram Generation**: Automatically creates sequence, ER, and flowcharts using Mermaid

### Intelligent Planning

- **Comprehensive Documentation**: Generates detailed project plans with architecture diagrams
- **Security-First Approach**: Built-in security validation against OWASP standards
- **Code-Ready Handoff**: Plans can be directly used by AI coding assistants or human developers

## 🏗️ Architecture

Triage AI combines a TypeScript VS Code extension with a powerful multi-agent backend:

```mermaid
graph TD
    A[VS Code Extension] -->|API Calls| B[Triage AI Engine]
    B --> C[PM Agent(s)]
    B --> D[Architect Agent(s)]
    B --> E[Security Agent(s)]
    C & D & E --> F[Generated Plan]
    F --> G[Implementation]
```

The extension communicates with specialized AI agents through a well-defined API, ensuring seamless integration and real-time feedback.

## 📦 Installation

*Coming soon to VS Code Marketplace*

For development setup:

```bash
git clone https://github.com/psychon7/Triage-AI.git
cd Triage-AI
npm install
npm run compile
```

## 🔧 Usage

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "Triage AI: Solve Problem"
3. Enter your project idea or requirements
4. Choose between Basic or Pro mode
5. Review the generated plan with architecture diagrams
6. Begin implementation with confidence

## 🗺️ Roadmap

- [x] Project concept and architecture design
- [x] Product Requirements Document (PRD)
- [ ] VS Code extension scaffolding
- [ ] Basic Mode implementation
- [ ] Pro Mode implementation
- [ ] Diagram generation integration
- [ ] Public beta release
- [ ] VS Code Marketplace publication

See the [PRD.md](PRD.md) for detailed implementation plans.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- Inspired by the [Devyan](https://github.com/theyashwanthsai/Devyan) project
- Built with VS Code Extension API
- Powered by state-of-the-art language models

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/psychon7">psychon7</a>
</p>
