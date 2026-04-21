"""
Base Agent Class for Claim Adjudication System
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import json
import ollama

class AgentResult:
    """Standardized result format for agent outputs"""
    
    def __init__(self, agent_name: str, status: str, data: Dict[str, Any], 
                 confidence: float = 0.0, reasoning: str = ""):
        self.agent_name = agent_name
        self.status = status  # "approved", "rejected", "needs_review", "error"
        self.data = data
        self.confidence = confidence
        self.reasoning = reasoning
        self.timestamp = self._get_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "status": self.status,
            "confidence": self.confidence,
            "data": self.data,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp
        }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

class BaseAgent(ABC):
    """Base class for all claim adjudication agents"""
    
    def __init__(self, name: str, model: str = "mistral"):
        self.name = name
        self.model = model
        self.logger = logging.getLogger(f"agent.{name.lower().replace(' ', '_')}")
        
    @abstractmethod
    def process(self, claim_data: Dict[str, Any]) -> AgentResult:
        """Process claim data and return results"""
        pass
    
    @abstractmethod
    def validate_input(self, claim_data: Dict[str, Any]) -> bool:
        """Validate input data for this agent"""
        pass
    
    def call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call LLM with structured prompts"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content'].strip()
        except Exception as e:
            self.logger.error(f"LLM call failed for {self.name}: {e}")
            raise
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate JSON response from LLM"""
        try:
            # Clean up response
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                if start > 6 and end > start:
                    response = response[start:end].strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing failed for {self.name}: {e}")
            return {"error": "Failed to parse response", "raw_response": response}
    
    def log_processing(self, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """Log processing details for audit trail"""
        self.logger.info(f"{self.name} - Input: {len(str(input_data))} chars")
        self.logger.info(f"{self.name} - Output: {len(str(output_data))} chars")
        
    def create_result(self, status: str, data: Dict[str, Any], confidence: float = 0.0) -> Dict[str, Any]:
        """Create standardized result format"""
        return {
            "agent": self.name,
            "status": status,
            "confidence": confidence,
            "data": data,
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
