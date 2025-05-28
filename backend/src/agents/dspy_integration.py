import dspy
import os
import warnings
from typing import List, Dict, Any
from decouple import config
from agents.custom_llm import BedrockCustomLLM  # Make sure this returns a *string* from .invoke()

warnings.filterwarnings("ignore")

# ------------------------------------------------------------------
# 🔑  Load Bedrock / Claude API credentials
# ------------------------------------------------------------------
api_key = config("BEDROCK_API_KEY")          # your Bedrock/Claude key (if needed)
base_url = config("BEDROCK_BASE_URL")           # rename if it's not actually OpenAI

# ------------------------------------------------------------------
# 🔧  Custom DSPy LLM wrapper (Bedrock Claude-3)
# ------------------------------------------------------------------
class DSPyLLM(dspy.LM):
    """DSPy wrapper that routes every prompt to Bedrock and returns a *string*."""

    def __init__(self, model: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        super().__init__(model=model)
        self.llm = BedrockCustomLLM(  # must expose .invoke(prompt:str)->str
            model_name=model,
            temperature=0.7,
            max_tokens=800,
            request_timeout=60,
            api_key=api_key,
            base_url=base_url,
        )

    # --------------------------------------------------------------
    # Low-level Bedrock request
    # --------------------------------------------------------------
    def basic_request(self, prompt: str, **kwargs) -> str:
        """Send prompt to Bedrock and return a raw *string* response."""
        try:
            # --- normalise prompt coming from DSPy/Predict
            if isinstance(prompt, dspy.Example):
                prompt = prompt.user_input
            elif isinstance(prompt, dict):
                prompt = prompt.get("user_input") or prompt.get("prompt") or str(prompt)
            elif not isinstance(prompt, str):
                prompt = str(prompt)

            if not prompt:
                raise ValueError("Empty prompt received")

            raw = self.llm.invoke(prompt)  # <-- should already be a string
            print("[basic_request] Raw Bedrock response received (first 500 chars):\n", raw[:500])
            return raw  # IMPORTANT: return *string* – DSPy will parse it

        except Exception as e:
            print("Error in basic_request:", e)
            raise

    # DSPy interface ------------------------------------------------
    def generate(self, prompt: str, **kwargs) -> str:
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        return self.basic_request(prompt, **kwargs)

    def __call__(self, *args, **kwargs):
        # Allow positional, keyword, or messages list
        prompt = None
        if args:
            prompt = args[0]
        elif "prompt" in kwargs:
            prompt = kwargs["prompt"]
        elif "user_input" in kwargs:
            prompt = kwargs["user_input"]
        elif "messages" in kwargs:
            user_msgs = [m["content"] for m in kwargs["messages"] if m["role"] == "user"]
            prompt = "\n".join(user_msgs)

        if not prompt:
            raise ValueError("No prompt provided to DSPyLLM")

        return self.generate(prompt, **kwargs)

# Tell DSPy to use this wrapper
dspy.configure(lm=DSPyLLM())

# ------------------------------------------------------------------
# 🧠  DSPy Signature for project specs
# ------------------------------------------------------------------
class ProjectManagementSignature(dspy.Signature):
    user_input: str = dspy.InputField(desc="Original user request")

    project_name: str = dspy.OutputField(desc="Concise name of the project")
    executive_summary: str = dspy.OutputField(desc="Brief overview")
    requirements: List[str] = dspy.OutputField(desc="Functional & non-functional requirements")
    features: Dict[str, List[str]] = dspy.OutputField(desc="Features grouped by category")
    scope: Dict[str, Any] = dspy.OutputField(desc="Scope inclusions & exclusions")
    milestones: List[Dict[str, str]] = dspy.OutputField(desc="Key milestones")
    technical_considerations: List[str] = dspy.OutputField(desc="Tech considerations")
    challenges: List[str] = dspy.OutputField(desc="Risks & mitigations")
    success_criteria: List[str] = dspy.OutputField(desc="How to measure success")

# ------------------------------------------------------------------
# 🤖  DSPy Module
# ------------------------------------------------------------------
class ProjectManagerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_spec = dspy.Predict(ProjectManagementSignature)

    def forward(self, user_input: str):
        if isinstance(user_input, dspy.Example):
            user_input = user_input.user_input
        return self.generate_spec(user_input=user_input)

# ------------------------------------------------------------------
# 📝  Markdown formatter
# ------------------------------------------------------------------

def format_dspy_output_as_markdown(spec) -> str:
    md = [f"# {spec.project_name}\n"]
    md += ["## Executive Summary", spec.executive_summary, "\n## Requirements"]
    md += [f"{i+1}. {req}" for i, req in enumerate(spec.requirements)]

    md += ["\n## Features"]
    for cat, feats in spec.features.items():
        md += [f"### {cat}"]
        md += [f"- {f}" for f in feats]

    md += ["\n## Scope", "### Inclusions"]
    md += [f"- {inc}" for inc in spec.scope.get("inclusions", [])]
    md += ["### Exclusions"]
    md += [f"- {exc}" for exc in spec.scope.get("exclusions", [])]

    md += ["\n## Milestones"]
    for ms in spec.milestones:
        md += [f"- **{ms.get('name', 'Unnamed')}**: {ms.get('description', '')}"]

    md += ["\n## Technical Considerations"]
    md += [f"- {t}" for t in spec.technical_considerations]

    md += ["\n## Challenges and Mitigations"]
    md += [f"- {c}" for c in spec.challenges]

    md += ["\n## Success Criteria"]
    md += [f"- {s}" for s in spec.success_criteria]

    return "\n".join(md)

# ------------------------------------------------------------------
# 🌟  Public helper
# ------------------------------------------------------------------

def process_with_dspy(user_input: str) -> str:
    if not user_input:
        raise ValueError("User input cannot be empty")

    spec = ProjectManagerModule()(user_input)
    return format_dspy_output_as_markdown(spec)
