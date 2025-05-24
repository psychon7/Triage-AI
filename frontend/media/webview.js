// Global state
const state = {
  currentTaskId: null,
  currentStep: 1,
  totalSteps: 4,
  debugMode: true, // Start with debug mode enabled for testing
  connectionOk: false,
  pendingRequests: new Map(), // Store pending API requests
  outputs: {
    pm: null,
    architect: null,
    security: null,
    test: null
  }
};

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM loaded - TriageAI initialized");
  log("Triage AI is initializing...");
  
  // Set up event listeners
  setupEventListeners();
  
  // Listen for messages from the extension
  window.addEventListener('message', handleExtensionMessages);
  
  // Request session state from extension
  requestStoredSession();
  
  // Test connection on startup
  testBackendConnection();
});

// Request stored session state from extension
function requestStoredSession() {
  vscode.postMessage({
    command: 'getStoredSession'
  });
  
  log('Requesting stored session data...');
}

// Handle messages from the VS Code extension
function handleExtensionMessages(event) {
  const message = event.data;
  log(`Received message from extension: ${message.command}`);
  
  if (message.command === 'apiResponse') {
    const pendingRequest = state.pendingRequests.get(message.requestId);
    
    if (pendingRequest) {
      // Remove from pending requests
      state.pendingRequests.delete(message.requestId);
      
      if (message.error) {
        pendingRequest.reject(new Error(message.error));
      } else {
        pendingRequest.resolve(message.data);
      }
    } else {
      log(`Warning: Received response for unknown request ID: ${message.requestId}`);
    }
  } else if (message.command === 'sessionInfo') {
    // Handle restored session info
    log(`Received session info: taskId=${message.taskId}, step=${message.currentStep}`);
    
    if (message.taskId) {
      state.currentTaskId = message.taskId;
      state.currentStep = message.currentStep || 1;
      
      // Restore UI based on stored step
      updateUI();
      
      // Fetch and restore agent outputs
      restoreSessionData();
    }
  }
}

// Restore session data from the backend
async function restoreSessionData() {
  if (!state.currentTaskId) return;
  
  log(`Restoring session data for task: ${state.currentTaskId}`);
  showLoading('Restoring session...');
  
  try {
    // Get task status
    const status = await apiCall(`/status/${state.currentTaskId}`, 'GET');
    log('Loaded task status:', status);
    
    // Load each agent's output based on the step
    if (state.currentStep >= 1) {
      try {
        const pmResponse = await apiCall(`/agent_output/${state.currentTaskId}/project_manager`, 'GET');
        if (pmResponse && pmResponse.output) {
          updateOutput('pm-output', pmResponse.output);
          state.outputs.pm = pmResponse.output;
          log('Restored PM output');
        }
      } catch (error) {
        log('Could not restore PM output:', error);
      }
    }
    
    if (state.currentStep >= 2) {
      try {
        const architectResponse = await apiCall(`/agent_output/${state.currentTaskId}/architect`, 'GET');
        if (architectResponse && architectResponse.output) {
          updateOutput('architect-output', architectResponse.output);
          state.outputs.architect = architectResponse.output;
          log('Restored architect output');
        }
      } catch (error) {
        log('Could not restore architect output:', error);
      }
    }
    
    if (state.currentStep >= 3) {
      try {
        const securityResponse = await apiCall(`/agent_output/${state.currentTaskId}/security`, 'GET');
        if (securityResponse && securityResponse.output) {
          updateOutput('security-output', securityResponse.output);
          state.outputs.security = securityResponse.output;
          log('Restored security output');
        }
      } catch (error) {
        log('Could not restore security output:', error);
      }
    }
    
    if (state.currentStep >= 4) {
      try {
        const testResponse = await apiCall(`/agent_output/${state.currentTaskId}/tester`, 'GET');
        if (testResponse && testResponse.output) {
          updateOutput('test-output', testResponse.output);
          state.outputs.test = testResponse.output;
          log('Restored tester output');
        }
      } catch (error) {
        log('Could not restore tester output:', error);
      }
    }
    
  } catch (error) {
    log('Error restoring session:', error.message);
    showMessage('Failed to restore session: ' + error.message);
  } finally {
    hideLoading();
  }
}

// Debug logging function
function log(message, data = null) {
  const msg = data ? `${message}: ${JSON.stringify(data, null, 2)}` : message;
  console.log(msg);
  
  const debugOutput = document.getElementById('debug-output');
  if (debugOutput) {
    const time = new Date().toLocaleTimeString();
    debugOutput.innerHTML += `<div>[${time}] ${msg.replace(/\n/g, '<br>').replace(/ /g, '&nbsp;')}</div>`;
    debugOutput.scrollTop = debugOutput.scrollHeight;
  }
}

// Show a message in VS Code
function showMessage(text) {
  vscode.postMessage({ command: 'alert', text });
  log(`Alert: ${text}`);
}

// Set up all event listeners
function setupEventListeners() {
  // Debug panel toggle
  const toggleDebugButton = document.getElementById('toggle-debug');
  if (toggleDebugButton) {
    toggleDebugButton.addEventListener('click', () => {
      state.debugMode = !state.debugMode;
      const debugPanel = document.getElementById('debug-panel');
      if (debugPanel) {
        debugPanel.style.display = state.debugMode ? 'block' : 'none';
      }
      log("Debug panel toggled: " + (state.debugMode ? "visible" : "hidden"));
    });
  } else {
    console.error("Toggle debug button not found");
  }
  
  // Test connection button
  const testConnectionButton = document.getElementById('test-connection');
  if (testConnectionButton) {
    testConnectionButton.addEventListener('click', testBackendConnection);
  } else {
    console.error("Test connection button not found");
  }
  
  // Analyze button
  const analyzeButton = document.getElementById('analyze-prompt');
  if (analyzeButton) {
    analyzeButton.addEventListener('click', handleAnalyze);
    log("Analyze button handler set up");
  } else {
    console.error("Analyze button not found");
  }
  
  // Navigation buttons
  document.querySelectorAll('.next-button').forEach(btn => {
    btn.addEventListener('click', handleNext);
  });
  
  document.querySelectorAll('.back-button').forEach(btn => {
    btn.addEventListener('click', handleBack);
  });
  
  // Apply plan button
  const applyButton = document.getElementById('apply-plan');
  if (applyButton) {
    applyButton.addEventListener('click', handleApplyPlan);
  } else {
    console.error("Apply plan button not found");
  }
  
  // Start new task button
  const startNewButton = document.getElementById('start-new');
  if (startNewButton) {
    startNewButton.addEventListener('click', handleStartNew);
  } else {
    console.error("Start new button not found");
  }
  
  log("All event listeners set up");
}

// Start a new task by clearing session data
function handleStartNew() {
  // Clear the session
  vscode.postMessage({
    command: 'clearSession'
  });
  
  // Reset UI state
  state.currentTaskId = null;
  state.currentStep = 1;
  state.outputs = {
    pm: null,
    architect: null,
    security: null,
    test: null
  };
  
  // Clear output areas
  document.getElementById('pm-output').innerHTML = '';
  document.getElementById('architect-output').innerHTML = '';
  document.getElementById('security-output').innerHTML = '';
  document.getElementById('test-output').innerHTML = '';
  document.getElementById('user-prompt').value = '';
  
  // Reset UI to first step
  updateUI();
  
  showMessage('Ready to start a new task');
}

// Make API request through the extension
async function apiCall(endpoint, method, body = null) {
  const requestId = generateRequestId();
  log(`API Call (${requestId}): ${method} ${endpoint}`, body);
  
  return new Promise((resolve, reject) => {
    // Store the promise callbacks to resolve/reject them when we get the response
    state.pendingRequests.set(requestId, { resolve, reject });
    
    // Send the request to the extension
    vscode.postMessage({
      command: 'apiRequest',
      requestId: requestId,
      endpoint: endpoint,
      method: method,
      body: body
    });
  });
}

// Generate a unique request ID
function generateRequestId() {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
}

// Test backend connection
function testBackendConnection() {
  log('Testing backend connection...');
  showLoading('Testing connection...');
  
  apiCall('/', 'GET')
    .then(response => {
      log('✅ Backend connection successful!', response);
      state.connectionOk = true;
      showMessage('Connected to backend successfully');
    })
    .catch(error => {
      log('❌ Backend connection error', error);
      state.connectionOk = false;
      showMessage('Cannot reach backend server. Is it running?');
    })
    .finally(() => {
      hideLoading();
    });
}

// Show the loading spinner
function showLoading(message) {
  const spinner = document.getElementById('loading-spinner');
  const messageEl = document.getElementById('loading-message');
  if (messageEl) messageEl.textContent = message || 'Processing...';
  if (spinner) spinner.classList.add('active');
  log(`Loading: ${message}`);
}

// Hide the loading spinner
function hideLoading() {
  const spinner = document.getElementById('loading-spinner');
  if (spinner) spinner.classList.remove('active');
}

// Update the UI based on current step
function updateUI() {
  // Update step indicators
  document.querySelectorAll('.step').forEach((step, index) => {
    step.classList.remove('active', 'completed');
    if (index + 1 === state.currentStep) {
      step.classList.add('active');
    } else if (index + 1 < state.currentStep) {
      step.classList.add('completed');
    }
  });
  
  // Update panels
  document.querySelectorAll('.agent-panel').forEach((panel, index) => {
    if (index + 1 === state.currentStep) {
      panel.classList.add('active');
    } else {
      panel.classList.remove('active');
    }
  });
  
  // Notify extension about step change
  vscode.postMessage({
    command: 'updateCurrentStep',
    step: state.currentStep
  });
  
  log(`UI updated to step ${state.currentStep}`);
}

// UPDATE: Simple function to display content directly with minimal formatting
function updateOutput(elementId, content) {
  const outputElement = document.getElementById(elementId);
  if (!outputElement) {
    log(`Element not found: ${elementId}`);
    return;
  }
  
  if (!content) {
    log(`No content provided for ${elementId}`);
    outputElement.innerHTML = '<p>No output available</p>';
    return;
  }
  
  log(`BEFORE UPDATE: Element ${elementId} display: ${outputElement.style.display}`);
  
  // Make sure element is visible
  outputElement.style.display = 'block';
  
  // Create a container for the raw content
  const rawContentDiv = document.createElement('div');
  rawContentDiv.className = 'raw-content';
  rawContentDiv.style.whiteSpace = 'pre-wrap';
  rawContentDiv.style.fontFamily = 'monospace';
  rawContentDiv.style.border = '1px solid #ddd';
  rawContentDiv.style.padding = '10px';
  rawContentDiv.style.margin = '10px 0';
  rawContentDiv.style.backgroundColor = '#f5f5f5';
  rawContentDiv.textContent = content;
  
  // Create a container for simple formatted content
  const formattedDiv = document.createElement('div');
  formattedDiv.className = 'formatted-content';
  
  // Very basic formatting to preserve content
  let formattedContent = content
    .replace(/##\s+([^\n]+)/g, '<h3>$1</h3>')
    .replace(/###\s+([^\n]+)/g, '<h4>$1</h4>')
    .replace(/\n- ([^\n]+)/g, '<ul><li>$1</li></ul>')
    .replace(/\n\n/g, '<br><br>');
  
  formattedDiv.innerHTML = formattedContent;
  
  // Clear existing content and append both versions
  outputElement.innerHTML = '';
  outputElement.appendChild(rawContentDiv);
  outputElement.appendChild(formattedDiv);
  
  log(`AFTER UPDATE: Element ${elementId} now has content and is visible`);
}

// Handle the analyze button click
async function handleAnalyze() {
  log('Analyze button clicked');
  const promptInput = document.getElementById('user-prompt');
  
  if (!promptInput || !promptInput.value.trim()) {
    showMessage('Please enter a prompt first');
    return;
  }
  
  const prompt = promptInput.value.trim();
  showLoading('Starting analysis...');
  
  try {
    // Call backend to start a new task
    log('Sending prompt to backend:', prompt);
    const runResponse = await apiCall('/run', 'POST', { problem: prompt });
    log('Run response received:', runResponse);
    
    if (!runResponse || !runResponse.task_id) {
      throw new Error('Invalid response from server - no task_id received');
    }
    
    state.currentTaskId = runResponse.task_id;
    log(`Task created with ID: ${state.currentTaskId}`);
    
    // Poll until PM agent is done
    let status;
    let retryCount = 0;
    const maxRetries = 30;  // Maximum number of status checks
    
    do {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
      try {
        status = await apiCall('/status/' + state.currentTaskId, 'GET');
        log('Status update:', status);
        
        if (status && status.agent_status && status.agent_status.project_manager === 'awaiting_approval') {
          break; // Exit the loop when project manager is ready
        }
        
        retryCount++;
        if (retryCount >= maxRetries) {
          throw new Error('Timeout waiting for project manager to complete');
        }
      } catch (error) {
        log('Error checking status:', error);
        // Wait and retry
        await new Promise(resolve => setTimeout(resolve, 3000));
      }
    } while (retryCount < maxRetries);
    
    // Get PM output
    log('Fetching project manager output...');
    const pmResponse = await apiCall('/agent_output/' + state.currentTaskId + '/project_manager', 'GET');
    log('PM output received:', pmResponse);
    
    if (pmResponse && pmResponse.output) {
      log('Updating PM output with API response, output length:', pmResponse.output.length);
      state.outputs.pm = pmResponse.output;
      
      // Update output element
      const outputElement = document.getElementById('pm-output');
      if (outputElement) {
        // Make output element visible before updating content
        outputElement.style.display = 'block';
        
        // Wait a moment and update the content
        setTimeout(() => {
          updateOutput('pm-output', pmResponse.output);
        }, 100);
      }
      showMessage('Analysis complete!');
    } else {
      throw new Error('No output from project manager');
    }
  } catch (error) {
    log('Error during analysis:', error.message);
    showMessage('Error: ' + error.message);
  } finally {
    hideLoading();
  }
}

// Handle next button click
async function handleNext() {
  if (state.currentStep >= state.totalSteps) return;
  
  if (!state.currentTaskId) {
    showMessage('Please analyze a prompt first');
    return;
  }
  
  let currentAgent;
  switch (state.currentStep) {
    case 1: currentAgent = 'project_manager'; break;
    case 2: currentAgent = 'architect'; break;
    case 3: currentAgent = 'security'; break;
    default: return;
  }
  
  showLoading('Processing...');
  
  try {
    // Approve current agent
    log(`Approving agent: ${currentAgent}`);
    const approveResponse = await apiCall(
      '/approve/' + state.currentTaskId + '/' + currentAgent, 
      'POST', 
      { approved: true, feedback: '' }
    );
    log('Approve response:', approveResponse);
    
    // Update UI to next step
    state.currentStep++;
    updateUI();
    
    // Get next agent name
    let nextAgent;
    switch (state.currentStep) {
      case 2: nextAgent = 'architect'; break;
      case 3: nextAgent = 'security'; break;
      case 4: nextAgent = 'tester'; break;
      default: return;
    }
    
    // Poll until next agent is ready
    log(`Waiting for ${nextAgent} to complete...`);
    let status;
    let retryCount = 0;
    const maxRetries = 30;
    
    do {
      await new Promise(resolve => setTimeout(resolve, 2000));
      status = await apiCall('/status/' + state.currentTaskId, 'GET');
      log('Status update:', status);
      
      if (status && status.agent_status && status.agent_status[nextAgent] === 'awaiting_approval') {
        break;
      }
      
      retryCount++;
      if (retryCount >= maxRetries) {
        throw new Error(`Timeout waiting for ${nextAgent} to complete`);
      }
    } while (retryCount < maxRetries);
    
    // Get output for next agent
    log(`Fetching ${nextAgent} output...`);
    const agentResponse = await apiCall('/agent_output/' + state.currentTaskId + '/' + nextAgent, 'GET');
    log(`${nextAgent} response:`, agentResponse);
    
    // Update appropriate output area
    let outputId;
    switch (state.currentStep) {
      case 2: 
        outputId = 'architect-output'; 
        state.outputs.architect = agentResponse.output;
        break;
      case 3: 
        outputId = 'security-output'; 
        state.outputs.security = agentResponse.output;
        break;
      case 4: 
        outputId = 'test-output'; 
        state.outputs.test = agentResponse.output;
        break;
      default: return;
    }
    
    if (agentResponse && agentResponse.output) {
      log(`Updating ${outputId} with API response`);
      const outputElement = document.getElementById(outputId);
      if (outputElement) {
        // Make output element visible before updating content
        outputElement.style.display = 'block';
        
        // Wait a moment and update the content
        setTimeout(() => {
          updateOutput(outputId, agentResponse.output);
        }, 100);
      }
    } else {
      throw new Error(`No output from ${nextAgent}`);
    }
  } catch (error) {
    log('Error during next step:', error.message);
    showMessage('Error: ' + error.message);
  } finally {
    hideLoading();
  }
}

// Handle back button click
function handleBack() {
  if (state.currentStep <= 1) return;
  
  state.currentStep--;
  updateUI();
  log('Navigated back to step ' + state.currentStep);
}

// Handle apply plan button click
async function handleApplyPlan() {
  if (!state.currentTaskId) {
    showMessage('No active task');
    return;
  }
  
  showLoading('Applying plan...');
  
  try {
    // Approve tester agent
    log('Approving tester agent...');
    const approveResponse = await apiCall(
      '/approve/' + state.currentTaskId + '/tester', 
      'POST', 
      { approved: true, feedback: '' }
    );
    log('Tester approve response:', approveResponse);
    
    // Get final results
    log('Fetching final results...');
    const resultsResponse = await apiCall('/results/' + state.currentTaskId, 'GET');
    log('Final results:', resultsResponse);
    
    // Try to get the workspace path from the status
    const statusResponse = await apiCall('/status/' + state.currentTaskId, 'GET');
    
    if (statusResponse && statusResponse.workspace_path) {
      // Get the path to the output file
      const outputPath = `${statusResponse.workspace_path}/triage-output/${state.currentTaskId}/full_plan.md`;
      log(`Full plan should be at: ${outputPath}`);
      
      // Offer to open the file
      showMessage('Plan generated! Opening the file...');
      
      // Open the file
      vscode.postMessage({
        command: 'openFile',
        path: outputPath
      });
    } else {
      showMessage('Plan applied successfully!');
    }
  } catch (error) {
    log('Error applying plan:', error.message);
    showMessage('Error: ' + error.message);
  } finally {
    hideLoading();
  }
}
