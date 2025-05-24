# Triage AI VS Code Extension

A Visual Studio Code extension that adds a custom sidebar panel with a multi-step workflow for AI-assisted software development planning. The extension guides users through a process involving Product Manager, Architect, Security, and Test agents.

## Features

- **Multi-step Workflow**: Navigate through four specialized AI agents
- **PM Agent**: Converts user requests into specific feature specifications
- **Architect Agent**: Creates architectural designs based on the specifications
- **Security Agent**: Reviews the architecture for security issues
- **Test Agent**: Provides comprehensive testing strategies
- **Modern UI**: Clean interface with step tracking, agent-specific styling, and loading animations

## Screenshots

The extension provides a sidebar with four panels, each representing a different agent in the workflow:

1. **PM Agent**: Enter project requirements and get feature specifications
2. **Architect Agent**: View architectural design based on requirements
3. **Security Agent**: Receive security recommendations for the architecture
4. **Test Agent**: Get testing strategy suggestions for the project

## Installation & Running

### For Development

1. Clone this repository
   ```
   git clone https://github.com/Pavun57/triageai-frontend.git
   cd triageai-frontend
   ```

2. Install dependencies
   ```
   npm install (or) pnpm install
   ```

3. Compile the extension
   ```
   npm run compile (or) pnpm run compile
   ```

4. Launch the extension in VS Code:
   - Open VS Code in this folder
   - Press `F5` to launch a new VS Code window with the extension loaded
   - In the new window, click on the Triage AI icon in the Activity Bar (sidebar)

### For End Users (once published)

1. Install from the VS Code Marketplace
2. Click on the Triage AI icon in the Activity Bar
3. Begin using the workflow

## Using the Extension

1. **PM Agent**:
   - Enter your project requirements in the text area
   - Click "Analyze" to generate feature specifications
   - Review the specifications and click "Approve & Continue"

2. **Architect Agent**:
   - Review the architectural design created based on the requirements
   - Navigate with "Back" or "Approve & Continue"

3. **Security Agent**:
   - Review security recommendations for the proposed architecture
   - Navigate with "Back" or "Approve & Continue"

4. **Test Agent**:
   - Review testing strategy suggestions
   - Click "Apply Plan" to complete the workflow

## Troubleshooting

If the extension isn't working correctly:

- Check the Developer Tools console (Help > Toggle Developer Tools) for error messages
- Make sure you're using a compatible version of VS Code
- Try reloading the window (Developer: Reload Window command)
- If navigation issues occur, try clicking directly on step indicators

## Development

This extension uses:
- TypeScript for the extension code
- HTML/CSS/JavaScript for the webview UI
- VS Code Extension API

To make changes:
1. Modify files in the `src` directory for extension logic
2. Update the webview HTML in `SidebarProvider.ts` for UI changes
3. Add or modify styles in `media/main.css`
4. Run `npm run compile` to rebuild

## License

[MIT](LICENSE)
