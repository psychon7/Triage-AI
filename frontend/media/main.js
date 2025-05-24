// Store VS Code API reference
const vscode = acquireVsCodeApi();
  
// Global state
let currentStep = 1;
const totalSteps = 4;

// Log execution start to verify the script is loaded
console.log('Triage AI: Script executed');

// DOM Elements
let analyzeButton = null;
let nextButtons = null;
let backButtons = null;
let applyPlanButton = null;
let stepIndicators = null;
let agentPanels = null;
let loadingSpinner = null;
let loadingMessage = null;

// Execute when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('Triage AI: DOM content loaded');
  initializeUI();
});

// Also try immediate initialization for VSCode webviews
initializeUI();

function initializeUI() {
  // Check if we've already initialized to avoid duplicate handlers
  if (analyzeButton !== null) {
    console.log('UI already initialized');
    return;
  }
  
  console.log('Triage AI: Initializing UI elements');
  
  // Get all UI elements
  analyzeButton = document.getElementById('analyze-prompt');
  nextButtons = document.querySelectorAll('.next-button');
  backButtons = document.querySelectorAll('.back-button');
  applyPlanButton = document.getElementById('apply-plan');
  stepIndicators = document.querySelectorAll('.step-indicator .step');
  agentPanels = document.querySelectorAll('.agent-panel');
  loadingSpinner = document.getElementById('loading-spinner');
  loadingMessage = document.getElementById('loading-message');
  
  // Debug element counts
  console.log(`Elements found: ${nextButtons?.length || 0} next buttons, ${backButtons?.length || 0} back buttons, ${agentPanels?.length || 0} panels`);

  // Set up analyze button
  if (analyzeButton) {
    console.log('Setting analyze button handler');
    analyzeButton.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Analyze button clicked');
      
      const userPrompt = document.getElementById('user-prompt');
      if (userPrompt && userPrompt.value.trim() === '') {
        vscode.postMessage({
          command: 'alert',
          text: 'Please enter a description before analyzing'
        });
        return;
      }
      
      showLoading('Analyzing request...');
      
      // Simulate processing
      setTimeout(function() {
        const pmOutput = document.getElementById('pm-output');
        if (pmOutput) {
          pmOutput.style.display = 'block';
          console.log('PM output displayed');
        }
        hideLoading();
      }, 1500);
    });
  }

  // Set up next buttons
  nextButtons.forEach(function(button) {
    console.log('Setting next button handler');
    button.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Next button clicked');
      
      if (currentStep < totalSteps) {
        showLoading(`Processing step ${currentStep}...`);
        
        setTimeout(function() {
          currentStep++;
          updateUI();
          hideLoading();
          console.log(`Advanced to step ${currentStep}`);
        }, 1000);
      }
    });
  });

  // Set up back buttons
  backButtons.forEach(function(button) {
    console.log('Setting back button handler');
    button.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Back button clicked');
      
      if (currentStep > 1) {
        currentStep--;
        updateUI();
        console.log(`Went back to step ${currentStep}`);
      }
    });
  });

  // Set up apply plan button
  if (applyPlanButton) {
    console.log('Setting apply plan button handler');
    applyPlanButton.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Apply plan button clicked');
      
      showLoading('Finalizing plan...');
      
      setTimeout(function() {
        hideLoading();
        vscode.postMessage({
          command: 'alert',
          text: 'Plan ready for implementation!'
        });
      }, 1500);
    });
  }

  updateUI();
}

// Update UI based on current step
function updateUI() {
  console.log(`Updating UI for step ${currentStep}`);
  
  // Update step indicators
  if (stepIndicators) {
    stepIndicators.forEach(function(indicator, index) {
      const step = index + 1;
      indicator.classList.remove('active', 'completed');
      
      if (step === currentStep) {
        indicator.classList.add('active');
      } else if (step < currentStep) {
        indicator.classList.add('completed');
      }
    });
  }

  // Show active panel, hide others
  if (agentPanels) {
    agentPanels.forEach(function(panel, index) {
      const step = index + 1;
      if (step === currentStep) {
        panel.classList.add('active');
        console.log(`Panel ${step} activated`);
      } else {
        panel.classList.remove('active');
      }
    });
  }
}

// Show loading spinner
function showLoading(message) {
  console.log(`Loading: ${message}`);
  if (loadingMessage) {
    loadingMessage.textContent = message;
  }
  if (loadingSpinner) {
    loadingSpinner.classList.add('active');
  }
}

// Hide loading spinner
function hideLoading() {
  console.log('Loading complete');
  if (loadingSpinner) {
    loadingSpinner.classList.remove('active');
  }
}
