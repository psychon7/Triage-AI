from crewai import Agent
from textwrap import dedent
from agents.custom_llm import BedrockCustomLLM


class CustomAgents:
    def __init__(self):
        # Using our custom Bedrock LLM implementation that works with the proxy
        # Main model with higher token limit for complex tasks
        self.OpenAIGPT4 = BedrockCustomLLM(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=800,
            request_timeout=60
        )
        
        # Secondary model with lower token limit for simpler tasks
        self.OpenAIGPT35 = BedrockCustomLLM(
            model_name="gpt-3.5-turbo", 
            temperature=0.7,
            max_tokens=500,
            request_timeout=60
        )
        #self.Ollama = ChatOpenAI(model_name="devainllama3", base_url="http://localhost:11434/v1")
    
    def project_manager_agent(self, tools):
        return Agent(
            role="Project Manager",
            backstory=dedent(f"""\
            As a seasoned project manager with years of experience leading software projects,
            you excel at gathering requirements, defining features, and creating detailed specifications.
            You understand how to translate user needs into clear, actionable project plans."""),
            goal=dedent(f"""\
            Define the project requirements and create a detailed feature specification
            for the requested problem, ensuring all user needs are clearly captured."""),
            tools=tools,
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT4,
        )
        
    def architect_agent(self, tools):
        return Agent(
            role="Software Architect",
            backstory=dedent(f"""\
            With years of experience in system design, 
            you excel at breaking down complex problems into manageable solutions,
            providing a solid foundation for implementation."""),
            goal=dedent(f"""\
            Provide a high-level solution overview for a given problem"""),
            tools=tools,
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT4,
        )

    def programmer_agent(self, tools):
        return Agent(
            role="Software Programmer",
            backstory=dedent(f"""\
            You havea keen eye for detail and a knack for translating high-level design solutions into robust,
            efficient code."""),
            goal=dedent(f"""Implement the solution provided by the architect"""),
            tools=tools,
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT4,
        )
    
    def security_agent(self, tools):
        return Agent(
            role="Security Specialist",
            backstory=dedent(f"""\
            With years of experience in cybersecurity and secure software development practices,
            you excel at identifying security vulnerabilities and recommending mitigations to ensure 
            applications are resistant to common attacks."""),
            goal=dedent(f"""\
            Analyze the architecture for security vulnerabilities and recommend comprehensive security mitigations."""),
            tools=tools,
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,  # Using the smaller model for security agent
        )

    def tester_agent(self, tools):
        return Agent(
            role="Software Tester",
            backstory=dedent(f"""\
            Your passion for quality ensures that every piece of code meets the highest
            standards through rigorous testing."""),
            goal = dedent("""\
            Write and run test cases for the code implemented by the programmer"""),
            tools=tools,
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,  # Using the smaller model for tester agent
        )

    def reviewer_agent(self, tools):
        return Agent(
            role="Software Reviewer",
            backstory=dedent("""\
            With a critical eye, you review each step of the development process, ensuring quality and consistency."""),
            goal=dedent("""\
            Review the work of each agent at each step"""),
            tools=tools,            
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,  # Using the smaller model for reviewer agent
        )
