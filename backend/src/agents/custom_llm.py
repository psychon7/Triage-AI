import os
from typing import Any, List, Mapping, Optional, Dict
import requests
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from decouple import config

class BedrockCustomLLM(LLM):
    """Custom LLM implementation for Amazon Bedrock proxy"""
    
    base_url: str = config("BEDROCK_BASE_URL")
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 500
    request_timeout: int = 60
    
    @property
    def _llm_type(self) -> str:
        return "bedrock-custom"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Bedrock API with error handling and retries"""
        
        # Important: Based on test_auth.py results, we should use ANTHROPIC_API_KEY
        # which works with the proxy, instead of OPENAI_API_KEY which fails
        api_key = config("ANTHROPIC_API_KEY")
        endpoint = f"{self.base_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        if stop is not None:
            data["stop"] = stop
            
        try:
            print(f"Making API request to {endpoint} with {self.model_name}")
            
            response = requests.post(
                endpoint, 
                headers=headers, 
                json=data,
                timeout=self.request_timeout
            )
            
            # Print status code to help with debugging
            print(f"API response status code: {response.status_code}")
            
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"API response success: received {len(content)} chars")
                return content
            else:
                error_msg = f"Error: Unexpected response structure: {result}"
                print(error_msg)
                return error_msg
                
        except Exception as e:
            # Log the error for debugging
            print(f"Bedrock API error: {str(e)}")
            # Return a graceful error message
            return f"Error: Failed to get response from Bedrock API: {str(e)}"

# Example usage
if __name__ == "__main__":
    llm = BedrockCustomLLM()
    response = llm("What is an authentication system?")
    print(response)
