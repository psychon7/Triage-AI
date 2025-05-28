import warnings
warnings.filterwarnings("ignore")
import os
import asyncio
import time
from crewai import Task, Crew

# Record start time for uptime tracking
start_time = time.time()

from agents.agents import CustomAgents
from tasks.tasks import CustomTasks
from agents.dspy_integration import process_with_dspy


# FastAPI imports
from fastapi import APIRouter, BackgroundTasks, HTTPException
import uuid
from models.schema import ProblemRequest, StatusResponse, AgentOutputResponse, ResultResponse, FeedbackRequest, ApprovalRequest, PauseRequest, ResumeRequest, TaskResponse
from tools.crew_tools import file_read_tool, architect_tools, programmer_tools, tester_tools, reviewer_tools, security_tools, search_web, read_file, write_file, create_directory
from functions.functions import update_task_status, generate_full_plan,tasks_store,TaskStatus,CustomCrew
from fastapi.middleware.cors import CORSMiddleware


# Create router instead of FastAPI app
router = APIRouter()

# Tool lists for project manager
project_manager_tools = [
    search_web,
    read_file,
    write_file,
    create_directory
]


# API Endpoints
@router.post("/run", response_model=TaskResponse)
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

@router.get("/status/{task_id}", response_model=StatusResponse)
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

@router.get("/agent_output/{task_id}/{agent}", response_model=AgentOutputResponse)
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

@router.get("/results/{task_id}", response_model=ResultResponse)
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

@router.post("/approve/{task_id}/{agent}")
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

@router.post("/pause/{task_id}")
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

@router.post("/resume/{task_id}")
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

@router.post("/feedback/{task_id}/{agent}")
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
    """Execute the project manager agent with DSPy framework"""
    task = tasks_store.get(task_id)
    if not task:
        return
        
    if task.paused:
        return  # Don't proceed if task is paused
    
    try:
        # Get the original problem description
        problem = task.step_messages[0].replace("Task created: ", "")
        
        update_task_status(
            task_id,
            "Processing with DSPy framework for optimized prompt generation...",
            5,
            "project_manager",
            "in_progress"
        )
        
        # Use DSPy to process the user input and get structured output
        try:
            # Process with DSPy first
            dspy_result = process_with_dspy(problem)
            result = dspy_result
            
            update_task_status(
                task_id,
                "DSPy processing completed successfully",
                5,
                "project_manager",
                "in_progress"
            )
        except Exception as dspy_error:
            # Log the DSPy error
            print(f"Error using DSPy: {str(dspy_error)}. Falling back to CrewAI.")
            update_task_status(
                task_id,
                f"DSPy processing failed: {str(dspy_error)}. Falling back to CrewAI.",
                0,
                "project_manager",
                "in_progress"
            )
            
            # Fall back to CrewAI if DSPy fails
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
