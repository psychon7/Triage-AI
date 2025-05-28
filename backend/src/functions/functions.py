from tools.crew_tools import architect_tools, programmer_tools, tester_tools, reviewer_tools, security_tools, search_web, read_file, write_file, create_directory
from agents.agents import CustomAgents
from tasks.tasks import CustomTasks
from tools.search_utils import CachedSearch
import time
from crewai import Crew, Task
import os


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
        if agent == "project_manager":
            return self.run_project_manager_with_feedback(feedback)
        elif agent == "architect":
            return self.run_architect_with_feedback(feedback)
        elif agent == "programmer":
            return self.run_programmer_with_feedback(feedback)
        elif agent == "tester":
            return self.run_tester_with_feedback(feedback)
        elif agent == "reviewer":
            return self.run_reviewer_with_feedback(feedback)
        else:
            return f"Invalid agent: {agent}"

    def run_project_manager_with_feedback(self, feedback):
        """Run project manager agent with feedback"""
        try:
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id, 
                    f"Restarting project manager agent with feedback: {feedback}", 
                    5, 
                    "project_manager", 
                    "in_progress"
                )
            
            # Get the original problem description
            problem = tasks_store[self.task_id].step_messages[0].replace("Task created: ", "")
            
            try:
                # First try with DSPy
                from agents.dspy_integration import process_with_dspy
                
                update_task_status(
                    self.task_id,
                    "Processing with DSPy framework with feedback...",
                    5,
                    "project_manager",
                    "in_progress"
                )
                
                # Enhanced problem with feedback
                enhanced_problem = f"{problem}\n\nPrevious feedback: {feedback}"
                
                # Process with DSPy
                result = process_with_dspy(enhanced_problem)
                
                update_task_status(
                    self.task_id,
                    "DSPy processing completed successfully",
                    5,
                    "project_manager",
                    "in_progress"
                )
                
            except Exception as dspy_error:
                # Log the DSPy error
                print(f"Error using DSPy with feedback: {str(dspy_error)}. Falling back to CrewAI.")
                update_task_status(
                    self.task_id,
                    f"DSPy processing failed: {str(dspy_error)}. Falling back to CrewAI.",
                    0,
                    "project_manager",
                    "in_progress"
                )
                
                # Fall back to CrewAI
                from agents.agents import CustomAgents
                from tasks.tasks import CustomTasks
                from tools.crew_tools import project_manager_tools
                
                agents = CustomAgents()
                tasks_obj = CustomTasks()
                
                # Create PM agent
                pm_agent = agents.project_manager_agent(project_manager_tools)
                
                # Create task with feedback
                modified_problem = f"{problem}\n\nPrevious feedback: {feedback}"
                pm_task = tasks_obj.project_management_task(pm_agent, project_manager_tools, modified_problem)
                
                # Create mini crew with just the PM task
                mini_crew = Crew(
                    agents=[pm_agent],
                    tasks=[pm_task],
                    verbose=True,
                )
                
                # Run the workflow
                result = mini_crew.kickoff()
            
            # Update task status
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    "Project Management revised based on feedback.",
                    5,
                    "project_manager",
                    "awaiting_feedback"
                )
                tasks_store[self.task_id].agent_outputs["project_manager"] = str(result)
                tasks_store[self.task_id].awaiting_feedback = True
                
            return result
        except Exception as e:
            error_msg = f"Error during project manager revision: {str(e)}"
            print(error_msg)
            if self.task_id and self.task_id in tasks_store:
                update_task_status(
                    self.task_id,
                    f"Error during revision: {str(e)}",
                    0,
                    "project_manager",
                    "error"
                )
                tasks_store[self.task_id].error = str(e)
            return error_msg
            
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
