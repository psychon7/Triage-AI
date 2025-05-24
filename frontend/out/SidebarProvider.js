"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SidebarProvider = void 0;
const vscode = require("vscode");
class SidebarProvider {
    constructor(_extensionUri, context) {
        this._extensionUri = _extensionUri;
        this._context = context;
    }
    resolveWebviewView(webviewView, context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (message) => {
            console.log('Received message from webview:', message);
            switch (message.command) {
                case 'alert':
                    vscode.window.showInformationMessage(message.text);
                    return;
                case 'apiRequest':
                    try {
                        const result = await vscode.commands.executeCommand('triage-ai.makeApiRequest', message.endpoint, message.method, message.body);
                        // If this is a task creation result, store the task ID
                        if (message.endpoint === '/run' && message.method === 'POST' && result && result.task_id) {
                            this._context.globalState.update('triage-current-task', result.task_id);
                            // Also store current step as step 1 (PM)
                            this._context.globalState.update('triage-current-step', 1);
                            console.log(`Stored task ID: ${result.task_id} in globalState`);
                        }
                        // Send the result back to the webview
                        webviewView.webview.postMessage({
                            command: 'apiResponse',
                            requestId: message.requestId,
                            data: result,
                            error: null
                        });
                    }
                    catch (error) {
                        console.error('API request failed:', error);
                        // Send the error back to the webview
                        webviewView.webview.postMessage({
                            command: 'apiResponse',
                            requestId: message.requestId,
                            data: null,
                            error: error instanceof Error ? error.message : String(error)
                        });
                    }
                    return;
                case 'updateCurrentStep':
                    // Store the current step in global state
                    this._context.globalState.update('triage-current-step', message.step);
                    console.log(`Updated current step to: ${message.step}`);
                    return;
                case 'getStoredSession':
                    // Return the stored session info (current task ID and step)
                    const taskId = this._context.globalState.get('triage-current-task');
                    const currentStep = this._context.globalState.get('triage-current-step') || 1;
                    webviewView.webview.postMessage({
                        command: 'sessionInfo',
                        taskId: taskId,
                        currentStep: currentStep
                    });
                    console.log(`Sending stored session: task=${taskId}, step=${currentStep}`);
                    return;
                case 'clearSession':
                    // Clear stored session data
                    this._context.globalState.update('triage-current-task', undefined);
                    this._context.globalState.update('triage-current-step', 1);
                    console.log('Cleared session data');
                    return;
                case 'openFile':
                    // Open a file in the editor
                    vscode.commands.executeCommand('triage-ai.openGeneratedFile', message.path);
                    return;
            }
        });
    }
    _getHtmlForWebview(webview) {
        // Get the local path to main script and CSS
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "media", "main.css"));
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "media", "webview.js"));
        // Get icons
        const pmIconUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "media", "icons", "pm-icon.svg"));
        const architectIconUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "media", "icons", "architect-icon.svg"));
        const securityIconUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "media", "icons", "security-icon.svg"));
        const testIconUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "media", "icons", "test-icon.svg"));
        // Use a nonce to whitelist which scripts can be run
        const nonce = getNonce();
        return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
  <title>Triage AI</title>
  <link href="${styleUri}" rel="stylesheet" />
  <style nonce="${nonce}">
    .output-content {
      margin-top: 10px;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      background-color: #f9f9f9;
      overflow-wrap: break-word;
    }
    .output-content h3 {
      margin-top: 10px;
      margin-bottom: 5px;
    }
    .output-content h4 {
      margin-top: 8px;
      margin-bottom: 4px;
    }
    .output-content ul {
      margin-top: 5px;
      margin-bottom: 5px;
      padding-left: 20px;
    }
    .output-content p {
      margin-top: 5px;
      margin-bottom: 5px;
    }
    .restart-button {
      display: inline-block;
      margin-top: 15px;
      padding: 5px 10px;
      background-color: #f0f0f0;
      border: 1px solid #ccc;
      border-radius: 4px;
      cursor: pointer;
    }
    .restart-button:hover {
      background-color: #e0e0e0;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Triage AI</h1>
      <div class="step-indicator">
        <div class="step active" data-step="1">
          <div class="step-icon">
            <img src="${pmIconUri}" alt="PM" />
          </div>
          <span>PM</span>
        </div>
        <div class="step" data-step="2">
          <div class="step-icon">
            <img src="${architectIconUri}" alt="Architect" />
          </div>
          <span>Architect</span>
        </div>
        <div class="step" data-step="3">
          <div class="step-icon">
            <img src="${securityIconUri}" alt="Security" />
          </div>
          <span>Security</span>
        </div>
        <div class="step" data-step="4">
          <div class="step-icon">
            <img src="${testIconUri}" alt="Test" />
          </div>
          <span>Test</span>
        </div>
      </div>
    </header>

    <!-- Debug panel -->
    <div id="debug-panel" style="background: #f0f0f0; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; display: block;">
      <h3>Debug Information</h3>
      <div id="debug-output" style="font-family: monospace; white-space: pre-wrap; max-height: 200px; overflow: auto;"></div>
      <div style="margin-top: 10px;">
        <button id="test-connection" style="margin-right: 10px;">Test Backend Connection</button>
        <button id="toggle-debug">Toggle Debug Panel</button>
      </div>
      <div style="margin-top: 5px;">
        <button id="start-new" class="restart-button">Start New Task</button>
      </div>
    </div>

    <main>
      <!-- PM Agent Panel -->
      <section id="pm-panel" class="agent-panel active">
        <div class="agent-header pm">
          <img src="${pmIconUri}" alt="PM Agent" />
          <h2>Product Manager Agent</h2>
        </div>
        <div class="agent-content">
          <p>The PM Agent converts your request into specific feature requirements.</p>
          <div class="input-area">
            <textarea id="user-prompt" placeholder="Describe the product or feature you want to build..."></textarea>
            <button id="analyze-prompt" class="primary-button">Analyze</button>
          </div>
          <div class="output-area">
            <h3>Feature Specifications</h3>
            <div id="pm-output" class="output-content"></div>
          </div>
        </div>
        <div class="navigation">
          <button class="next-button">Approve & Continue</button>
        </div>
      </section>

      <!-- Architect Agent Panel -->
      <section id="architect-panel" class="agent-panel">
        <div class="agent-header architect">
          <img src="${architectIconUri}" alt="Architect Agent" />
          <h2>Architect Agent</h2>
        </div>
        <div class="agent-content">
          <p>The Architect Agent creates a technical design based on the feature specifications.</p>
          <div class="output-area">
            <h3>Architecture Design</h3>
            <div id="architect-output" class="output-content"></div>
          </div>
        </div>
        <div class="navigation">
          <button class="back-button">Back</button>
          <button class="next-button">Approve & Continue</button>
        </div>
      </section>

      <!-- Security Agent Panel -->
      <section id="security-panel" class="agent-panel">
        <div class="agent-header security">
          <img src="${securityIconUri}" alt="Security Agent" />
          <h2>Security Agent</h2>
        </div>
        <div class="agent-content">
          <p>The Security Agent reviews the architecture for potential security issues.</p>
          <div class="output-area">
            <h3>Security Recommendations</h3>
            <div id="security-output" class="output-content"></div>
          </div>
        </div>
        <div class="navigation">
          <button class="back-button">Back</button>
          <button class="next-button">Approve & Continue</button>
        </div>
      </section>
      
      <!-- Test Agent Panel -->
      <section id="test-panel" class="agent-panel">
        <div class="agent-header test">
          <img src="${testIconUri}" alt="Test Agent" />
          <h2>Test Agent</h2>
        </div>
        <div class="agent-content">
          <p>The Test Agent provides a comprehensive testing strategy.</p>
          <div class="output-area">
            <h3>Testing Strategy</h3>
            <div id="test-output" class="output-content"></div>
          </div>
        </div>
        <div class="navigation">
          <button class="back-button">Back</button>
          <button id="apply-plan" class="primary-button">Apply Plan</button>
        </div>
      </section>

      <!-- Loading Spinner -->
      <div id="loading-spinner" class="loading-overlay">
        <div class="spinner"></div>
        <p id="loading-message">Processing...</p>
      </div>
    </main>
  </div>

  <script nonce="${nonce}">
    // Initialize VS Code API and store it in a global variable
    const vscode = acquireVsCodeApi();
  </script>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
    }
}
exports.SidebarProvider = SidebarProvider;
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
//# sourceMappingURL=SidebarProvider.js.map