"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const SidebarProvider_1 = require("./SidebarProvider");
const http = require("http");
const https = require("https");
const url_1 = require("url");
// Backend API configuration
const apiBaseUrl = 'http://localhost:8000';
function activate(context) {
    // Create and register the sidebar provider
    const sidebarProvider = new SidebarProvider_1.SidebarProvider(context.extensionUri, context);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider("triageAI", sidebarProvider));
    // Register command to make API requests from webview
    context.subscriptions.push(vscode.commands.registerCommand('triage-ai.makeApiRequest', async (endpoint, method, body) => {
        try {
            // If this is a /run request, add the workspace path to the request body
            if (endpoint === '/run' && method === 'POST' && body) {
                const workspaceFolders = vscode.workspace.workspaceFolders;
                if (workspaceFolders && workspaceFolders.length > 0) {
                    body.workspace_path = workspaceFolders[0].uri.fsPath;
                    console.log(`Adding workspace path: ${body.workspace_path}`);
                }
                else {
                    console.log('No workspace folders available');
                }
            }
            const result = await makeApiRequest(endpoint, method, body);
            return result;
        }
        catch (error) {
            vscode.window.showErrorMessage(`API request failed: ${error}`);
            throw error;
        }
    }));
    // Register command to open generated files
    context.subscriptions.push(vscode.commands.registerCommand('triage-ai.openGeneratedFile', async (filePath) => {
        try {
            const uri = vscode.Uri.file(filePath);
            const document = await vscode.workspace.openTextDocument(uri);
            await vscode.window.showTextDocument(document);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to open file: ${error}`);
        }
    }));
    console.log('Triage AI extension activated');
}
exports.activate = activate;
/**
 * Make an API request to the backend server
 * @param endpoint The API endpoint (e.g., '/run')
 * @param method The HTTP method (e.g., 'GET', 'POST')
 * @param body Optional request body for POST requests
 * @returns Promise that resolves to the response data
 */
async function makeApiRequest(endpoint, method, body) {
    return new Promise((resolve, reject) => {
        const url = new url_1.URL(endpoint, apiBaseUrl);
        console.log(`Making ${method} request to ${url.toString()}`);
        const options = {
            hostname: url.hostname,
            port: url.port || (url.protocol === 'https:' ? 443 : 80),
            path: url.pathname + url.search,
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        const client = url.protocol === 'https:' ? https : http;
        const req = client.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            res.on('end', () => {
                if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        const parsedData = data ? JSON.parse(data) : {};
                        resolve(parsedData);
                    }
                    catch (error) {
                        console.error('Error parsing JSON response:', error);
                        reject(new Error(`Invalid JSON response: ${data}`));
                    }
                }
                else {
                    console.error(`API error: ${res.statusCode} - ${data}`);
                    reject(new Error(`API error: ${res.statusCode} - ${data}`));
                }
            });
        });
        req.on('error', (error) => {
            console.error('Request error:', error);
            reject(error);
        });
        if (body) {
            const jsonBody = JSON.stringify(body);
            req.write(jsonBody);
        }
        req.end();
    });
}
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map