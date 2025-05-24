import warnings
warnings.filterwarnings("ignore")

import os
import asyncio
import time
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from decouple import config
from crewai.tools import tool

# Record start time for uptime tracking
start_time = time.time()

from textwrap import dedent
from agents import CustomAgents
from tasks import CustomTasks
from crewai_tools import FileReadTool
from tools.file_write import FileWriteTool
from tools.directory_write import DirWriteTool
from search_utils import cached_search

# FastAPI imports
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Dict, List, Optional, Any

# Initialize tools
file_read_tool = FileReadTool()

# Create native CrewAI tools using the tool decorator
from crewai.tools import tool

@tool("Search the web")
def search_web(query: str) -> str:
    """Search the web for information with caching and retry logic."""
    return cached_search.search(query)

@tool("Read file")
def read_file(file_path: str) -> str:
    """Read content from a file."""
    return file_read_tool.run(file_path)

@tool("Write file")
def write_file(filename: str, content: str) -> str:
    """Write content to a file."""
    return FileWriteTool().run(filename, content)

@tool("Create directory")
def create_directory(directory_path: str) -> str:
    """Create a new directory."""
    return DirWriteTool().run(directory_path)

# Tool lists
architect_tools = [
    search_web,
    read_file,
    write_file,
    create_directory
]

security_tools = [
    search_web,
    read_file,
    write_file,
    create_directory
]

programmer_tools = [
    read_file,
    write_file,
    create_directory
]

tester_tools = [
    read_file,
    write_file,
    create_directory
]

reviewer_tools = [
    read_file,
    write_file,
    create_directory
]

# FIXED: Use ANTHROPIC_API_KEY instead of OPENAI_API_KEY
api_key = config("ANTHROPIC_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key



# Task tracking storage
tasks_store = {}

# Task status structure
class TaskStatus:
    def __init__(self):
        self.started = True
        self.current_agent = "project_manager"  # Start with project manager now
        self.completed_agents = []
        self.agent_outputs = {
            "project_manager": None,
            "architect": None,
            "security": None, 
            "tester": None,
            "reviewer": None
        }
        self.agent_status = {
            "project_manager": "pending",
            "architect": "pending",
            "security": "pending",
            "tester": "pending",
            "reviewer": "pending"
        }
        self.agent_feedback = {
            "project_manager": None,
            "architect": None,
            "security": None,
            "tester": None,
            "reviewer": None
        }
        self.revision_counts = {
            "project_manager": 0,
            "architect": 0,
            "security": 0,
            "tester": 0,
            "reviewer": 0
        }
        
        # User approval fields
        self.awaiting_user_approval = False
        self.user_approved = False
        self.user_feedback = None
        
        # Pause/Resume fields
        self.paused = False
        self.pause_reason = None
        self.pause_timestamp = None
        
        # Legacy field, kept for compatibility
        self.awaiting_feedback = False
        
        self.progress = 0  # Progress percentage 0-100
        self.step_messages = []  # List of progress messages
        self.created_at = time.time()  # Timestamp when task was created
        self.updated_at = time.time()  # Timestamp of last update
        self.final_result = ""  # Initialize as empty string instead of None
        self.complete = False
        self.error = None

# Helper function to update task status - moved outside of run_problem
def update_task_status(task_id, message, progress_increment=0, agent=None, agent_status=None):
    if task_id in tasks_store:
        tasks_store[task_id].updated_at = time.time()
        tasks_store[task_id].step_messages.append(message)
        tasks_store[task_id].progress += progress_increment
        # Cap progress at 100%
        tasks_store[task_id].progress = min(tasks_store[task_id].progress, 100)
        
        # Update agent status if provided
        if agent and agent_status:
            tasks_store[task_id].agent_status[agent] = agent_status
            
        print(f"Task {task_id} update: {message} (progress: {tasks_store[task_id].progress}%)")

class CustomCrew:
    def __init__(self, user_input, task_id=None, feedback=None, restart_agent=None):
        self.user_input = user_input
        self.task_id = task_id
        self.feedback = feedback
        self.restart_agent = restart_agent
        
    def run_with_feedback(self, agent, feedback):
        """Restart a specific agent with feedback"""
        if agent == "architect":
            return self.run_architect_with_feedback(feedback)
        elif agent == "programmer":
            return self.run_programmer_with_feedback(feedback)
        elif agent == "tester":
            return self.run_tester_with_feedback(feedback)
        elif agent == "reviewer":
            return self.run_reviewer_with_feedback(feedback)
        else:
            return f"Invalid agent: {agent}"
            
    def run_architect_with_feedback(self, feedback):
        """Run architect agent with feedback"""
        try:
            agents = CustomAgents()
            tasks = CustomTasks()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id, 
                    f"Restarting architect agent with feedback: {feedback}", 
                    5, 
                    "architect", 
                    "in_progress"
                )
            
            # Create architect agent with feedback
            architect_agent = agents.architect_agent(architect_tools)
            
            # Create architecture task with feedback
            modified_problem = f"{self.user_input}\n\nPrevious feedback: {feedback}"
            architecture_task = tasks.architecture_task(architect_agent, architect_tools, modified_problem)
            
            # Create mini crew with just the architect task
            mini_crew = Crew(
                agents=[architect_agent],
                tasks=[architecture_task],
                verbose=True,
            )
            
            # Run the architect workflow
            result = mini_crew.kickoff()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    "Architecture revised based on feedback.",
                    5,
                    "architect",
                    "awaiting_feedback"
                )
                tasks_store[self.task_id].agent_outputs["architect"] = str(result)
                tasks_store[self.task_id].awaiting_feedback = True
                
            return result
        except Exception as e:
            error_msg = f"Error during architect revision: {str(e)}"
            print(error_msg)
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    f"Error during revision: {str(e)}",
                    0,
                    "architect",
                    "error"
                )
                tasks_store[self.task_id].error = str(e)
            return error_msg
            
    def run_programmer_with_feedback(self, feedback):
        """Run programmer agent with feedback"""
        try:
            agents = CustomAgents()
            tasks = CustomTasks()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id, 
                    f"Restarting programmer agent with feedback: {feedback}", 
                    5, 
                    "programmer", 
                    "in_progress"
                )
            
            # Get architect output
            architect_output = tasks_store[self.task_id].agent_outputs.get("architect", "No architecture provided")
            
            # Create programmer agent with feedback
            programmer_agent = agents.programmer_agent(programmer_tools)
            
            # Create a context task to provide the architecture and feedback
            context_task = Task(
                description=f"Architecture: {architect_output}\n\nPrevious implementation feedback: {feedback}",
                agent=programmer_agent,
                expected_output="Context information for implementation with feedback."
            )
            
            # Create implementation task based on context
            implementation_task = tasks.implementation_task(programmer_agent, programmer_tools, [context_task])
            
            # Create mini crew with just the programmer task
            mini_crew = Crew(
                agents=[programmer_agent],
                tasks=[implementation_task],
                verbose=True,
            )
            
            # Run the programmer workflow
            result = mini_crew.kickoff()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    "Implementation revised based on feedback.",
                    5,
                    "programmer",
                    "awaiting_feedback"
                )
                tasks_store[self.task_id].agent_outputs["programmer"] = str(result)
                tasks_store[self.task_id].awaiting_feedback = True
                
            return result
        except Exception as e:
            error_msg = f"Error during programmer revision: {str(e)}"
            print(error_msg)
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    f"Error during revision: {str(e)}",
                    0,
                    "programmer",
                    "error"
                )
                tasks_store[self.task_id].error = str(e)
            return error_msg
    
    def run_tester_with_feedback(self, feedback):
        """Run tester agent with feedback"""
        try:
            agents = CustomAgents()
            tasks = CustomTasks()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id, 
                    f"Restarting tester agent with feedback: {feedback}", 
                    5, 
                    "tester", 
                    "in_progress"
                )
            
            # Get programmer output
            programmer_output = tasks_store[self.task_id].agent_outputs.get("programmer", "No implementation provided")
            
            # Create tester agent with feedback
            tester_agent = agents.tester_agent(tester_tools)
            
            # Create a context task to provide the implementation and feedback
            context_task = Task(
                description=f"Implementation: {programmer_output}\n\nPrevious testing feedback: {feedback}",
                agent=tester_agent,
                expected_output="Context information for testing with feedback."
            )
            
            # Create testing task based on context
            testing_task = tasks.testing_task(tester_agent, tester_tools, [context_task])
            
            # Create mini crew with just the tester task
            mini_crew = Crew(
                agents=[tester_agent],
                tasks=[testing_task],
                verbose=True,
            )
            
            # Run the tester workflow
            result = mini_crew.kickoff()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    "Testing revised based on feedback.",
                    5,
                    "tester",
                    "awaiting_feedback"
                )
                tasks_store[self.task_id].agent_outputs["tester"] = str(result)
                tasks_store[self.task_id].awaiting_feedback = True
                
            return result
        except Exception as e:
            error_msg = f"Error during tester revision: {str(e)}"
            print(error_msg)
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    f"Error during revision: {str(e)}",
                    0,
                    "tester",
                    "error"
                )
                tasks_store[self.task_id].error = str(e)
            return error_msg
            
    def run_reviewer_with_feedback(self, feedback):
        """Run reviewer agent with feedback"""
        try:
            agents = CustomAgents()
            tasks = CustomTasks()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id, 
                    f"Restarting reviewer agent with feedback: {feedback}", 
                    5, 
                    "reviewer", 
                    "in_progress"
                )
            
            # Get previous outputs
            architect_output = tasks_store[self.task_id].agent_outputs.get("architect", "No architecture provided")
            programmer_output = tasks_store[self.task_id].agent_outputs.get("programmer", "No implementation provided")
            tester_output = tasks_store[self.task_id].agent_outputs.get("tester", "No tests provided")
            
            # Create reviewer agent with feedback
            reviewer_agent = agents.reviewer_agent(reviewer_tools)
            
            # Create context tasks to provide all previous outputs and feedback
            architect_context = Task(
                description=f"Architecture: {architect_output}",
                agent=reviewer_agent,
                expected_output="Context information for architecture review."
            )
            
            programmer_context = Task(
                description=f"Implementation: {programmer_output}",
                agent=reviewer_agent,
                expected_output="Context information for implementation review."
            )
            
            tester_context = Task(
                description=f"Testing: {tester_output}",
                agent=reviewer_agent,
                expected_output="Context information for test results review."
            )
            
            feedback_context = Task(
                description=f"Previous review feedback: {feedback}",
                agent=reviewer_agent,
                expected_output="Context information for review feedback."
            )
            
            # Create reviewing task based on all contexts
            reviewing_task = tasks.reviewing_task(
                reviewer_agent, 
                reviewer_tools, 
                [architect_context, programmer_context, tester_context, feedback_context]
            )
            
            # Create mini crew with just the reviewer task
            mini_crew = Crew(
                agents=[reviewer_agent],
                tasks=[reviewing_task],
                verbose=True,
            )
            
            # Run the reviewer workflow
            result = mini_crew.kickoff()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    "Review revised based on feedback.",
                    5,
                    "reviewer",
                    "awaiting_feedback"
                )
                tasks_store[self.task_id].agent_outputs["reviewer"] = str(result)
                tasks_store[self.task_id].awaiting_feedback = True
                
            return result
        except Exception as e:
            error_msg = f"Error during reviewer revision: {str(e)}"
            print(error_msg)
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    f"Error during revision: {str(e)}",
                    0,
                    "reviewer",
                    "error"
                )
                tasks_store[self.task_id].error = str(e)
            return error_msg
    
    def run(self):
        try:
            agents = CustomAgents()
            tasks = CustomTasks()

            # Update task status to show we're starting with architect
            if self.task_id and self.task_id in tasks_store:
                tasks_store[self.task_id].current_agent = "architect"
                update_task_status(
                    self.task_id, 
                    "Starting architect agent...", 
                    10, 
                    "architect", 
                    "in_progress"
                )

            # Agents
            architect_agent = agents.architect_agent(architect_tools)
            programmer_agent = agents.programmer_agent(programmer_tools)
            tester_agent = agents.tester_agent(tester_tools)
            reviewer_agent = agents.reviewer_agent(reviewer_tools)

            # Tasks
            architecture_task = tasks.architecture_task(architect_agent, architect_tools, self.user_input)
            
            # Update status before moving to implementation task
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id, 
                    "Architecture completed, moving to implementation phase...", 
                    15, 
                    "architect", 
                    "completed"
                )
                update_task_status(
                    self.task_id,
                    "Starting programmer agent...",
                    5,
                    "programmer",
                    "in_progress"
                )
                
            # Create implementation task based on architecture
            implementation_task = tasks.implementation_task(programmer_agent, programmer_tools, [architecture_task])
            
            # Update task status after architect completes
            if self.task_id and self.task_id in tasks_store:
                tasks_store[self.task_id].agent_outputs["architect"] = "Architecture task completed"
                tasks_store[self.task_id].completed_agents.append("architect")
                tasks_store[self.task_id].current_agent = "programmer"
            
            # Update status before moving to testing task
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id, 
                    "Implementation completed, moving to testing phase...", 
                    15, 
                    "programmer", 
                    "completed"
                )
                update_task_status(
                    self.task_id,
                    "Starting tester agent...",
                    5,
                    "tester",
                    "in_progress"
                )
                
            # Create testing task based on implementation
            testing_task = tasks.testing_task(tester_agent, tester_tools, [implementation_task])
            
            # Update task status after programmer completes
            if self.task_id and self.task_id in tasks_store:
                tasks_store[self.task_id].agent_outputs["programmer"] = "Programming task completed"
                tasks_store[self.task_id].completed_agents.append("programmer")
                tasks_store[self.task_id].current_agent = "tester"
            
            # Update status before moving to reviewing task
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id, 
                    "Testing completed, moving to review phase...", 
                    15, 
                    "tester", 
                    "completed"
                )
                update_task_status(
                    self.task_id,
                    "Starting reviewer agent...",
                    5,
                    "reviewer",
                    "in_progress"
                )
                
            # Create reviewing task based on all previous tasks
            reviewing_task = tasks.reviewing_task(reviewer_agent, reviewer_tools, [architecture_task, implementation_task, testing_task])
            
            # Update task status after tester completes
            if self.task_id and self.task_id in tasks_store:
                tasks_store[self.task_id].agent_outputs["tester"] = "Testing task completed"
                tasks_store[self.task_id].completed_agents.append("tester")
                tasks_store[self.task_id].current_agent = "reviewer"

            # Create crew with all agents and tasks
            if self.task_id and self.task_id in tasks_store:
                update_task_status(self.task_id, "Creating AI crew with all agents and tasks...", 5)
                
            crew = Crew(
                agents=[architect_agent, programmer_agent, tester_agent, reviewer_agent],
                tasks=[architecture_task, implementation_task, testing_task, reviewing_task],
                verbose=True,
            )

            # Run the crew workflow
            if self.task_id and self.task_id in tasks_store:
                update_task_status(self.task_id, "Executing crew workflow...", 5)
                
            result = crew.kickoff()
            
            # Update task status after reviewer completes
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    "Review process completed, finalizing results...",
                    15,
                    "reviewer",
                    "completed"
                )
                tasks_store[self.task_id].agent_outputs["reviewer"] = "Review task completed"
                tasks_store[self.task_id].completed_agents.append("reviewer")
                # Convert the result to string to ensure it can be properly serialized
                tasks_store[self.task_id].final_result = str(result) if result is not None else ""
                tasks_store[self.task_id].complete = True
                tasks_store[self.task_id].current_agent = "complete"
                
                # Final completion update
                update_task_status(self.task_id, "Task completed successfully!", 5)
            
            return result
        except Exception as e:
            error_msg = f"Error during crew execution: {str(e)}"
            print(error_msg)
            if self.task_id and self.task_id in tasks_store:
                # Update the task status with the error
                update_task_status(
                    self.task_id,
                    f"Error: {str(e)}",
                    0,
                    tasks_store[self.task_id].current_agent,
                    "error"
                )
                tasks_store[self.task_id].error = str(e)
                tasks_store[self.task_id].complete = True  # Mark as complete with error
            raise e

# Create FastAPI app
app = FastAPI(title="Triage AI API", description="API for Triage AI agent system")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tool lists for project manager
project_manager_tools = [
    search_web,
    read_file,
    write_file,
    create_directory
]

# API Models
class ProblemRequest(BaseModel):
    problem: str

class FeedbackRequest(BaseModel):
    feedback: str
    approved: bool = False

class ApprovalRequest(BaseModel):
    approved: bool = True
    feedback: Optional[str] = None

class PauseRequest(BaseModel):
    reason: Optional[str] = "User requested pause"
    
class ResumeRequest(BaseModel):
    continue_from: Optional[str] = None  # Optional parameter to specify where to resume

class TaskResponse(BaseModel):
    task_id: str
    message: str = "Task submitted successfully"
    timestamp: float = time.time()

class StatusResponse(BaseModel):
    task_id: str
    current_agent: str
    agent_status: Dict[str, str]
    completed_agents: List[str]
    progress: int
    step_messages: List[str]
    created_at: float
    updated_at: float
    complete: bool
    error: Optional[str] = None
    agent_feedback: Dict[str, Optional[str]]
    revision_counts: Dict[str, int]
    awaiting_feedback: bool
    awaiting_user_approval: bool = False
    paused: bool = False
    pause_reason: Optional[str] = None
    pause_timestamp: Optional[float] = None

class AgentOutputResponse(BaseModel):
    agent: str
    output: Optional[str] = None

class ResultResponse(BaseModel):
    result: str = ""  # Default to empty string instead of None
    complete: bool
    error: Optional[str] = None

# Function to generate a consolidated full plan file
def generate_full_plan(task_id: str):
    """
    Generate a consolidated full plan document with all agent outputs
    """
    if task_id not in tasks_store:
        raise ValueError(f"Task {task_id} not found")
        
    task = tasks_store[task_id]
    
    # Get the original problem description
    problem = task.step_messages[0].replace("Task created: ", "")
    
    # Create directory structure
    output_dir = f"{task_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all agent outputs
    project_manager_output = task.agent_outputs.get("project_manager", "No project management output available")
    architect_output = task.agent_outputs.get("architect", "No architecture output available")
    security_output = task.agent_outputs.get("security", "No security analysis available")
    tester_output = task.agent_outputs.get("tester", "No testing output available")
    reviewer_output = task.agent_outputs.get("reviewer", "No review output available")
    
    # Create timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Format the full plan document
    full_plan = f"""# Complete Project Plan
## Task ID: {task_id}
## Generated: {timestamp}

## Original Problem:
{problem}

---

## 1. Project Management Specification
{project_manager_output}

---

## 2. Architecture Design
{architect_output}

---

## 3. Security Analysis
{security_output}

---

## 4. Testing Plan
{tester_output}

---

## 5. Final Review and Implementation Plan
{reviewer_output}

---

*This document was automatically generated by combining the outputs of all agents in the workflow.*
"""
    
    # Write the consolidated plan to file
    output_file = f"{output_dir}/full_plan.md"
    with open(output_file, 'w') as f:
        f.write(full_plan)
        
    # Update the final result in the task store
    tasks_store[task_id].final_result = full_plan
        
    print(f"Generated full plan saved to {output_file}")
    return output_file

# API Endpoints
@app.post("/run", response_model=TaskResponse)
async def run_problem(request: ProblemRequest, background_tasks: BackgroundTasks):
    """Start a new agent processing task with Project Manager first"""
    task_id = str(uuid.uuid4())
    
    # Initialize task status
    tasks_store[task_id] = TaskStatus()
    tasks_store[task_id].step_messages.append(f"Task created: {request.problem}")
    
    # Run only the Project Manager agent in the background
    async def run_first_agent():
        try:
            # Add a small delay to ensure the task ID is returned before processing starts
            await asyncio.sleep(0.5)
            
            update_task_status(task_id, "Starting task execution...", 5)
            
            # Start with the Project Manager agent
            await start_project_manager(task_id)
            
        except Exception as e:
            error_msg = f"Error in task {task_id}: {str(e)}"
            print(error_msg)
            if task_id in tasks_store:
                # Mark task as failed in status
                update_task_status(
                    task_id,
                    f"Error occurred: {str(e)}",
                    0,
                    tasks_store[task_id].current_agent, 
                    "error"
                )
                tasks_store[task_id].error = str(e)
                tasks_store[task_id].complete = True  # Mark as complete but with error
    
    # Start the background task
    background_tasks.add_task(run_first_agent)
    
    # Return the task ID immediately 
    return {
        "task_id": task_id, 
        "message": "Task submitted successfully and is being processed",
        "timestamp": time.time()
    }

@app.get("/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    """Get current status of a task"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    task = tasks_store[task_id]
    return {
        "task_id": task_id,
        "current_agent": task.current_agent,
        "agent_status": task.agent_status,
        "completed_agents": task.completed_agents,
        "progress": task.progress,
        "step_messages": task.step_messages,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "complete": task.complete,
        "error": task.error,
        "agent_feedback": task.agent_feedback,
        "revision_counts": task.revision_counts,
        "awaiting_feedback": task.awaiting_feedback,
        "awaiting_user_approval": task.awaiting_user_approval,
        "paused": task.paused,
        "pause_reason": task.pause_reason,
        "pause_timestamp": task.pause_timestamp
    }

@app.get("/agent_output/{task_id}/{agent}", response_model=AgentOutputResponse)
async def get_agent_output(task_id: str, agent: str):
    """Get output from a specific agent"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if agent not in ["project_manager", "architect", "security", "tester", "reviewer"]:
        raise HTTPException(status_code=400, detail="Invalid agent name")
    
    output = tasks_store[task_id].agent_outputs.get(agent)
    return {
        "agent": agent,
        "output": output
    }

@app.get("/results/{task_id}", response_model=ResultResponse)
async def get_results(task_id: str):
    """Get final results of a completed task"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_store[task_id]
    
    # Ensure the result is a string before returning
    result = str(task.final_result) if task.final_result is not None else ""
    
    return {
        "result": result,
        "complete": task.complete,
        "error": task.error
    }

@app.post("/approve/{task_id}/{agent}")
async def approve_agent_work(task_id: str, agent: str, request: ApprovalRequest, background_tasks: BackgroundTasks):
    """Submit approval/rejection for an agent's work"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task = tasks_store[task_id]
    
    if task.current_agent != agent:
        raise HTTPException(status_code=400, detail=f"Current agent is {task.current_agent}, not {agent}")
    
    if not task.awaiting_user_approval:
        # Allow approval anyway, but notify
        print(f"Warning: Agent {agent} was not awaiting approval")
        
    # Record user feedback if provided
    if request.feedback:
        task.user_feedback = request.feedback
        task.agent_feedback[agent] = request.feedback
    
    task.awaiting_user_approval = False
    task.user_approved = request.approved
    
    # Save agent output to file when approved
    if request.approved:
        try:
            # Create directory structure
            output_dir = f"{task_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Get agent output
            agent_output = task.agent_outputs.get(agent, "No output available")
            
            # Create formatted output with metadata
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            formatted_output = f"""# {agent.capitalize()} Output
## Task ID: {task_id}
## Timestamp: {timestamp}
## Status: Approved

{agent_output}
"""
            
            # Write output to file
            output_file = f"{output_dir}/{agent}_output.md"
            with open(output_file, 'w') as f:
                f.write(formatted_output)
                
            print(f"Saved {agent} output to {output_file}")
        except Exception as e:
            # Log error but don't fail the approval process
            print(f"Error saving {agent} output to file: {str(e)}")
    
    # Get next agent in sequence
    def get_next_agent(current_agent):
        sequence = ["project_manager", "architect", "security", "tester", "reviewer"]
        try:
            current_index = sequence.index(current_agent)
            if current_index < len(sequence) - 1:
                return sequence[current_index + 1]
            return None  # No more agents
        except ValueError:
            return None
    
    if request.approved:
        # Mark agent as approved
        update_task_status(
            task_id,
            f"{agent.capitalize()} output approved by user",
            5,
            agent,
            "approved"
        )
        
        task.completed_agents.append(agent)
        
        # Determine next agent
        next_agent = get_next_agent(agent)
        if next_agent:
            task.current_agent = next_agent
            
            # Start next agent in background
            background_tasks.add_task(start_agent, task_id, next_agent)
            
            return {"message": f"{agent.capitalize()} work approved, proceeding to {next_agent}"}
        else:
            # This was the last agent - generate full plan file and mark as complete
            task.complete = True
            
            # Generate the consolidated full plan document
            try:
                generate_full_plan(task_id)
            except Exception as e:
                print(f"Error generating full plan: {str(e)}")
            
            update_task_status(
                task_id,
                f"All agents completed and approved. Task finished! Full plan generated.",
                5,
                "complete",
                "completed"
            )
            return {"message": f"{agent.capitalize()} work approved. Task completed! Full plan file has been generated."}
    else:
        # Rejected, restart agent with feedback
        if not request.feedback:
            raise HTTPException(
                status_code=400, 
                detail="Feedback is required when rejecting an agent's output"
            )
            
        update_task_status(
            task_id,
            f"{agent.capitalize()} output rejected. Restarting with feedback: {request.feedback}",
            0,
            agent,
            "needs_revision"
        )
        
        # Increment revision count
        task.revision_counts[agent] += 1
        
        # Restart agent with feedback in background
        async def restart_with_feedback():
            try:
                # Create crew with the original problem and pass the feedback
                crew = CustomCrew(
                    tasks_store[task_id].step_messages[0].replace("Task created: ", ""), 
                    task_id
                )
                
                # Run the appropriate agent with feedback
                result = crew.run_with_feedback(agent, request.feedback)
                
                # Store the result
                tasks_store[task_id].agent_outputs[agent] = str(result)
                
                # Mark as awaiting user approval again
                tasks_store[task_id].awaiting_user_approval = True
                
                # Update status
                update_task_status(
                    task_id,
                    f"{agent.capitalize()} revision completed. Awaiting user approval.",
                    5,
                    agent,
                    "awaiting_approval"
                )
                
            except Exception as e:
                error_msg = f"Error restarting {agent} with feedback: {str(e)}"
                print(error_msg)
                if task_id in tasks_store:
                    update_task_status(
                        task_id,
                        error_msg,
                        0,
                        agent,
                        "error"
                    )
                    tasks_store[task_id].error = str(e)
        
        # Start the background task
        background_tasks.add_task(restart_with_feedback)
        
        return {"message": f"{agent.capitalize()} work requires revision. Restarting with feedback."}

@app.post("/pause/{task_id}")
async def pause_task(task_id: str, request: PauseRequest):
    """Pause a running task"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_store[task_id]
    
    if task.paused:
        raise HTTPException(status_code=400, detail="Task is already paused")
    
    if task.complete:
        raise HTTPException(status_code=400, detail="Cannot pause a completed task")
    
    task.paused = True
    task.pause_reason = request.reason
    task.pause_timestamp = time.time()
    
    # Add message to step messages
    update_task_status(
        task_id,
        f"Task paused by user: {request.reason}",
        0,
        task.current_agent,
        "paused"
    )
    
    return {"message": "Task paused successfully"}

@app.post("/resume/{task_id}")
async def resume_task(task_id: str, request: ResumeRequest, background_tasks: BackgroundTasks):
    """Resume a paused task"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_store[task_id]
    if not task.paused:
        raise HTTPException(status_code=400, detail="Task is not paused")
    
    # Reset pause flags
    task.paused = False
    pause_duration = time.time() - (task.pause_timestamp or 0)
    
    # Add message to step messages
    update_task_status(
        task_id,
        f"Task resumed after being paused for {int(pause_duration)} seconds",
        0,
        task.current_agent,
        task.agent_status.get(task.current_agent, "in_progress")
    )
    
    # Resume operation based on current state
    if task.awaiting_user_approval:
        # Keep waiting for user approval
        return {"message": "Task resumed and awaiting user approval"}
    else:
        # Resume agent execution in background
        async def resume_execution():
            try:
                # Create crew with the original problem
                crew = CustomCrew(
                    tasks_store[task_id].step_messages[0].replace("Task created: ", ""), 
                    task_id
                )
                
                # For now, just restart the current agent - in future could implement checkpointing
                current_agent = task.current_agent
                update_task_status(
                    task_id,
                    f"Resuming execution from agent: {current_agent}",
                    0,
                    current_agent,
                    "in_progress"
                )
                
                # Simple restart logic - could be enhanced
                if current_agent == "project_manager":
                    await start_project_manager(task_id)
                elif current_agent == "architect":
                    await start_architect(task_id)
                elif current_agent == "programmer":
                    await start_programmer(task_id)
                elif current_agent == "tester":
                    await start_tester(task_id)
                elif current_agent == "reviewer":
                    await start_reviewer(task_id)
                
            except Exception as e:
                error_msg = f"Error resuming task: {str(e)}"
                print(error_msg)
                if task_id in tasks_store:
                    update_task_status(
                        task_id,
                        error_msg,
                        0,
                        task.current_agent,
                        "error"
                    )
                    task.error = str(e)
        
        # Start the background task
        background_tasks.add_task(resume_execution)
        return {"message": "Task resumed and continuing execution"}

@app.post("/feedback/{task_id}/{agent}")
async def submit_feedback(task_id: str, agent: str, request: FeedbackRequest, background_tasks: BackgroundTasks):
    """Submit feedback for a specific agent's work on a task (legacy endpoint)"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if agent not in ["project_manager", "architect", "programmer", "tester", "reviewer"]:
        raise HTTPException(status_code=400, detail="Invalid agent name")
    
    # Store the feedback
    tasks_store[task_id].agent_feedback[agent] = request.feedback
    
    # Update revision count
    tasks_store[task_id].revision_counts[agent] += 1
    
    # Handle approval or rejection
    if request.approved:
        # Proceed to next agent if approved
        next_agent = None
        if agent == "architect":
            next_agent = "programmer"
        elif agent == "programmer":
            next_agent = "tester"
        elif agent == "tester":
            next_agent = "reviewer"
        elif agent == "reviewer":
            # Mark task as complete if reviewer is approved
            tasks_store[task_id].complete = True
            update_task_status(
                task_id,
                f"{agent.capitalize()} work approved. Task completed!",
                5,
                "complete",
                "completed"
            )
            return {"message": f"{agent} work approved. Task completed!"}
        
        # Update status for next agent
        if next_agent:
            tasks_store[task_id].current_agent = next_agent
            update_task_status(
                task_id,
                f"{agent.capitalize()} work approved, proceeding to {next_agent}",
                5,
                next_agent,
                "in_progress"
            )
            return {"message": f"{agent} work approved, proceeding to {next_agent}"}
    else:
        # Mark for revision
        update_task_status(
            task_id,
            f"{agent.capitalize()} work needs revision: {request.feedback}",
            0,
            agent,
            "needs_revision"
        )
        
        # Mark that we're awaiting new results after feedback
        tasks_store[task_id].awaiting_feedback = True
        
        # Start the agent again with feedback in background
        async def restart_agent_with_feedback():
            try:
                # Create crew with the original problem and pass the feedback
                crew = CustomCrew(
                    tasks_store[task_id].step_messages[0].replace("Task created: ", ""), 
                    task_id
                )
                
                # Run the appropriate agent with feedback
                result = crew.run_with_feedback(agent, request.feedback)
                
                # Store the result
                tasks_store[task_id].agent_outputs[agent] = str(result)
                
                # Update status
                update_task_status(
                    task_id,
                    f"{agent.capitalize()} revision completed. Awaiting feedback.",
                    5,
                    agent,
                    "awaiting_feedback"
                )
                
            except Exception as e:
                error_msg = f"Error restarting {agent} with feedback: {str(e)}"
                print(error_msg)
                if task_id in tasks_store:
                    update_task_status(
                        task_id,
                        error_msg,
                        0,
                        agent,
                        "error"
                    )
                    tasks_store[task_id].error = str(e)
        
        # Start the background task
        background_tasks.add_task(restart_agent_with_feedback)
        
        return {"message": f"{agent} work requires revision. Feedback recorded and agent restarted."}

# Helper functions for agent execution
async def start_agent(task_id, agent_name):
    """Start execution of an agent"""
    task = tasks_store.get(task_id)
    if not task:
        return
    
    # Update task status
    update_task_status(
        task_id,
        f"Starting {agent_name} agent...",
        5,
        agent_name,
        "in_progress"
    )
    
    # Call the appropriate agent based on the name
    if agent_name == "project_manager":
        await start_project_manager(task_id)
    elif agent_name == "architect":
        await start_architect(task_id)
    elif agent_name == "security":
        await start_security(task_id)
    elif agent_name == "tester":
        await start_tester(task_id)
    elif agent_name == "reviewer":
        await start_reviewer(task_id)

async def start_project_manager(task_id):
    """Execute the project manager agent"""
    task = tasks_store.get(task_id)
    if not task:
        return
        
    if task.paused:
        return  # Don't proceed if task is paused
    
    try:
        # Get the original problem description
        problem = task.step_messages[0].replace("Task created: ", "")
        
        # Create agents and tasks
        agents = CustomAgents()
        tasks_obj = CustomTasks()
        
        # Create PM agent
        agent = agents.project_manager_agent(project_manager_tools)
        
        # Create task
        pm_task = tasks_obj.project_management_task(agent, project_manager_tools, problem)
        
        # Create mini crew with just this agent
        mini_crew = Crew(
            agents=[agent],
            tasks=[pm_task],
            verbose=True,
        )
        
        # Run the agent
        result = mini_crew.kickoff()
        
        # Store output
        task.agent_outputs["project_manager"] = str(result)
        
        # Mark as awaiting approval
        task.awaiting_user_approval = True
        
        update_task_status(
            task_id,
            "Project Manager has completed work. Awaiting user approval.",
            15,
            "project_manager",
            "awaiting_approval"
        )
        
    except Exception as e:
        error_msg = f"Error during Project Manager execution: {str(e)}"
        print(error_msg)
        update_task_status(
            task_id,
            error_msg,
            0,
            "project_manager",
            "error"
        )
        task.error = str(e)

async def start_architect(task_id):
    """Execute the architect agent"""
    task = tasks_store.get(task_id)
    if not task:
        return
        
    if task.paused:
        return  # Don't proceed if task is paused
    
    try:
        # Get the project management output as input for architect
        pm_output = task.agent_outputs.get("project_manager", "No project specification provided")
        problem = task.step_messages[0].replace("Task created: ", "")
        enhanced_problem = f"{problem}\n\nProject Specification:\n{pm_output}"
        
        # Create agents and tasks
        agents = CustomAgents()
        tasks_obj = CustomTasks()
        
        # Create architect agent
        agent = agents.architect_agent(architect_tools)
        
        # Create architecture task with enhanced problem
        architecture_task = tasks_obj.architecture_task(agent, architect_tools, enhanced_problem)
        
        # Create mini crew with just this agent
        mini_crew = Crew(
            agents=[agent],
            tasks=[architecture_task],
            verbose=True,
        )
        
        # Run the agent
        result = mini_crew.kickoff()
        
        # Store output
        task.agent_outputs["architect"] = str(result)
        
        # Mark as awaiting approval
        task.awaiting_user_approval = True
        
        update_task_status(
            task_id,
            "Architect has completed work. Awaiting user approval.",
            15,
            "architect",
            "awaiting_approval"
        )
        
    except Exception as e:
        error_msg = f"Error during Architect execution: {str(e)}"
        print(error_msg)
        update_task_status(
            task_id,
            error_msg,
            0,
            "architect",
            "error"
        )
        task.error = str(e)

async def start_programmer(task_id):
    """Execute the programmer agent"""
    task = tasks_store.get(task_id)
    if not task:
        return
        
    if task.paused:
        return  # Don't proceed if task is paused
    
    try:
        # Get architect output
        architect_output = task.agent_outputs.get("architect", "No architecture provided")
        
        # Create agents and tasks
        agents = CustomAgents()
        tasks_obj = CustomTasks()
        
        # Create programmer agent
        agent = agents.programmer_agent(programmer_tools)
        
        # Create context task
        context_task = Task(
            description=f"Architecture: {architect_output}",
            agent=agent,
            expected_output="Context information for security analysis."
        )
        
        # Create implementation task based on context
        implementation_task = tasks_obj.implementation_task(agent, programmer_tools, [context_task])
        
        # Create mini crew
        mini_crew = Crew(
            agents=[agent],
            tasks=[implementation_task],
            verbose=True,
        )
        
        # Run the agent
        result = mini_crew.kickoff()
        
        # Store output
        task.agent_outputs["programmer"] = str(result)
        
        # Mark as awaiting approval
        task.awaiting_user_approval = True
        
        update_task_status(
            task_id,
            "Programmer has completed work. Awaiting user approval.",
            15,
            "programmer",
            "awaiting_approval"
        )
        
    except Exception as e:
        error_msg = f"Error during Programmer execution: {str(e)}"
        print(error_msg)
        update_task_status(
            task_id,
            error_msg,
            0,
            "programmer",
            "error"
        )
        task.error = str(e)

async def start_tester(task_id):
    """Execute the tester agent"""
    task = tasks_store.get(task_id)
    if not task:
        return
        
    if task.paused:
        return  # Don't proceed if task is paused
    
    try:
        # Get programmer output
        programmer_output = task.agent_outputs.get("programmer", "No implementation provided")
        
        # Create agents and tasks
        agents = CustomAgents()
        tasks_obj = CustomTasks()
        
        # Create tester agent
        agent = agents.tester_agent(tester_tools)
        
        # Create context task
        context_task = Task(
            description=f"Implementation: {programmer_output}",
            agent=agent,
            expected_output="Context information for testing."
        )
        
        # Create testing task based on context
        testing_task = tasks_obj.testing_task(agent, tester_tools, [context_task])
        
        # Create mini crew
        mini_crew = Crew(
            agents=[agent],
            tasks=[testing_task],
            verbose=True,
        )
        
        # Run the agent
        result = mini_crew.kickoff()
        
        # Store output
        task.agent_outputs["tester"] = str(result)
        
        # Mark as awaiting approval
        task.awaiting_user_approval = True
        
        update_task_status(
            task_id,
            "Tester has completed work. Awaiting user approval.",
            15,
            "tester",
            "awaiting_approval"
        )
        
    except Exception as e:
        error_msg = f"Error during Tester execution: {str(e)}"
        print(error_msg)
        update_task_status(
            task_id,
            error_msg,
            0,
            "tester",
            "error"
        )
        task.error = str(e)

async def start_security(task_id):
    """Execute the security agent"""
    task = tasks_store.get(task_id)
    if not task:
        return
        
    if task.paused:
        return  # Don't proceed if task is paused
    
    try:
        # Get architect output
        architect_output = task.agent_outputs.get("architect", "No architecture provided")
        
        # Create agents and tasks
        agents = CustomAgents()
        tasks_obj = CustomTasks()
        
        # Create security agent
        agent = agents.security_agent(security_tools)
        
        # Create context task
        context_task = Task(
            description=f"Architecture: {architect_output}",
            agent=agent,
            expected_output="Context information for security analysis."
        )
        
        # Create security task based on context
        security_task = tasks_obj.security_task(agent, security_tools, [context_task])
        
        # Create mini crew
        mini_crew = Crew(
            agents=[agent],
            tasks=[security_task],
            verbose=True,
        )
        
        # Run the agent
        result = mini_crew.kickoff()
        
        # Store output
        task.agent_outputs["security"] = str(result)
        
        # Mark as awaiting approval
        task.awaiting_user_approval = True
        
        update_task_status(
            task_id,
            "Security specialist has completed work. Awaiting user approval.",
            15,
            "security",
            "awaiting_approval"
        )
        
    except Exception as e:
        error_msg = f"Error during Security execution: {str(e)}"
        print(error_msg)
        update_task_status(
            task_id,
            error_msg,
            0,
            "security",
            "error"
        )
        task.error = str(e)

async def start_reviewer(task_id):
    """Execute the reviewer agent"""
    task = tasks_store.get(task_id)
    if not task:
        return
        
    if task.paused:
        return  # Don't proceed if task is paused
    
    try:
        # Get previous outputs
        architecture = task.agent_outputs.get("architect", "No architecture provided")
        implementation = task.agent_outputs.get("programmer", "No implementation provided")
        tests = task.agent_outputs.get("tester", "No tests provided")
        
        # Create agents and tasks
        agents = CustomAgents()
        tasks_obj = CustomTasks()
        
        # Create reviewer agent
        agent = agents.reviewer_agent(reviewer_tools)
        
        # Create context tasks
        arch_context = Task(
            description=f"Architecture: {architecture}",
            agent=agent,
            expected_output="Context information for architecture review."
        )
        
        impl_context = Task(
            description=f"Implementation: {implementation}",
            agent=agent,
            expected_output="Context information for implementation review."
        )
        
        test_context = Task(
            description=f"Tests: {tests}",
            agent=agent,
            expected_output="Context information for test results review."
        )
        
        # Create reviewing task based on all contexts
        reviewing_task = tasks_obj.reviewing_task(
            agent,
            reviewer_tools,
            [arch_context, impl_context, test_context]
        )
        
        # Create mini crew
        mini_crew = Crew(
            agents=[agent],
            tasks=[reviewing_task],
            verbose=True,
        )
        
        # Run the agent
        result = mini_crew.kickoff()
        
        # Store output
        task.agent_outputs["reviewer"] = str(result)
        
        # Mark as awaiting approval
        task.awaiting_user_approval = True
        
        update_task_status(
            task_id,
            "Reviewer has completed work. Awaiting user approval.",
            15,
            "reviewer",
            "awaiting_approval"
        )
        
    except Exception as e:
        error_msg = f"Error during Reviewer execution: {str(e)}"
        print(error_msg)
        update_task_status(
            task_id,
            error_msg,
            0,
            "reviewer",
            "error"
        )
        task.error = str(e)

@app.get("/")
async def get_root():
    return {"message": "Welcome to the Triage AI API", "version": "1.0.0", "status": "running","docs": "/docs", "uptime": time.time() - start_time}

# Keep CLI functionality or run API server
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        # Start API server
        import uvicorn
        port = 8000  # Use a different port to avoid conflicts
        print(f"Starting Devyan API server at http://0.0.0.0:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Run CLI version (original functionality)
        print("\n####### Welcome to Devyan #######")
        print("---------------------------------")
        user_input = input("What problem do you want me to solve?\n")
        crew = CustomCrew(user_input)
        result = crew.run()
        
        print("\n\n########################")
        print("## Here is your crew run result:")
        print("########################\n")
        print(result)
