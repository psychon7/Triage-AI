from crewai import Task

class CustomTasks:
    def project_management_task(self, agent, tools, problem):
        return Task(
            description=f"""Analyze the following problem and create a detailed project specification:
            {problem}
            
            Include:
            1. Project scope and objectives
            2. Key requirements
            3. Technical constraints
            4. Success criteria
            5. Timeline estimates
            """,
            agent=agent,
            expected_output="A comprehensive project specification document"
        )

    def architecture_task(self, agent, tools, problem):
        return Task(
            description=f"""Design the system architecture based on:
            {problem}
            
            Include:
            1. System components and their interactions
            2. Technology stack recommendations
            3. Data flow diagrams
            4. Security considerations
            5. Scalability approach
            """,
            agent=agent,
            expected_output="A detailed system architecture design document"
        )

    def implementation_task(self, agent, tools, context_tasks):
        return Task(
            description="""Implement the system based on the architecture design.
            
            Include:
            1. Code implementation
            2. Documentation
            3. Setup instructions
            4. Dependencies
            """,
            agent=agent,
            expected_output="Complete implementation with documentation",
            context=context_tasks
        )

    def testing_task(self, agent, tools, context_tasks):
        return Task(
            description="""Create and execute test cases for the implementation.
            
            Include:
            1. Unit tests
            2. Integration tests
            3. Test results
            4. Coverage report
            """,
            agent=agent,
            expected_output="Comprehensive test suite and results",
            context=context_tasks
        )

    def security_task(self, agent, tools, context_tasks):
        return Task(
            description="""Perform security analysis of the architecture.
            
            Include:
            1. Threat modeling
            2. Security vulnerabilities
            3. Mitigation strategies
            4. Best practices compliance
            """,
            agent=agent,
            expected_output="Security analysis report",
            context=context_tasks
        )

    def reviewing_task(self, agent, tools, context_tasks):
        return Task(
            description="""Review the entire project implementation.
            
            Include:
            1. Code review
            2. Architecture review
            3. Test coverage review
            4. Security review
            5. Recommendations
            """,
            agent=agent,
            expected_output="Comprehensive project review report",
            context=context_tasks
        ) 