"""
Capability Detection Service for Hive Agents

This service automatically detects agent capabilities and specializations based on
the models installed on each Ollama endpoint. It replaces hardcoded specializations
with dynamic detection based on actual model capabilities.
"""

import httpx
import asyncio
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModelCapability(str, Enum):
    """Model capability categories based on model characteristics"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review" 
    REASONING = "reasoning"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    VISUAL_ANALYSIS = "visual_analysis"
    GENERAL_AI = "general_ai"
    KERNEL_DEV = "kernel_dev"
    PYTORCH_DEV = "pytorch_dev"
    PROFILER = "profiler"


class AgentSpecialty(str, Enum):
    """Dynamic agent specializations based on model capabilities"""
    ADVANCED_CODING = "advanced_coding"      # starcoder2, deepseek-coder-v2, devstral
    REASONING_ANALYSIS = "reasoning_analysis" # phi4-reasoning, granite3-dense
    CODE_REVIEW_DOCS = "code_review_docs"    # codellama, qwen2.5-coder
    GENERAL_AI = "general_ai"                # llama3, gemma, mistral
    MULTIMODAL = "multimodal"                # llava, vision models
    LIGHTWEIGHT = "lightweight"             # small models < 8B


# Model capability mapping based on model names and characteristics
MODEL_CAPABILITIES = {
    # Advanced coding models
    "starcoder2": [ModelCapability.CODE_GENERATION, ModelCapability.KERNEL_DEV],
    "deepseek-coder": [ModelCapability.CODE_GENERATION, ModelCapability.CODE_REVIEW],
    "devstral": [ModelCapability.CODE_GENERATION, ModelCapability.PROFILER],
    "codellama": [ModelCapability.CODE_GENERATION, ModelCapability.CODE_REVIEW],
    "qwen2.5-coder": [ModelCapability.CODE_GENERATION, ModelCapability.CODE_REVIEW],
    "qwen3": [ModelCapability.CODE_GENERATION, ModelCapability.REASONING],
    
    # Reasoning and analysis models
    "phi4-reasoning": [ModelCapability.REASONING, ModelCapability.PROFILER],
    "phi4": [ModelCapability.REASONING, ModelCapability.GENERAL_AI],
    "granite3-dense": [ModelCapability.REASONING, ModelCapability.PYTORCH_DEV],
    "deepseek-r1": [ModelCapability.REASONING, ModelCapability.CODE_REVIEW],
    
    # General purpose models
    "llama3": [ModelCapability.GENERAL_AI, ModelCapability.DOCUMENTATION],
    "gemma": [ModelCapability.GENERAL_AI, ModelCapability.TESTING],
    "mistral": [ModelCapability.GENERAL_AI, ModelCapability.DOCUMENTATION],
    "dolphin": [ModelCapability.GENERAL_AI, ModelCapability.REASONING],
    
    # Multimodal models
    "llava": [ModelCapability.VISUAL_ANALYSIS, ModelCapability.DOCUMENTATION],
    
    # Tool use models
    "llama3-groq-tool-use": [ModelCapability.CODE_GENERATION, ModelCapability.TESTING],
}

# Specialization determination based on capabilities
SPECIALTY_MAPPING = {
    frozenset([ModelCapability.CODE_GENERATION, ModelCapability.KERNEL_DEV]): AgentSpecialty.ADVANCED_CODING,
    frozenset([ModelCapability.CODE_GENERATION, ModelCapability.PROFILER]): AgentSpecialty.ADVANCED_CODING,
    frozenset([ModelCapability.REASONING, ModelCapability.PROFILER]): AgentSpecialty.REASONING_ANALYSIS,
    frozenset([ModelCapability.REASONING, ModelCapability.PYTORCH_DEV]): AgentSpecialty.REASONING_ANALYSIS,
    frozenset([ModelCapability.CODE_REVIEW, ModelCapability.DOCUMENTATION]): AgentSpecialty.CODE_REVIEW_DOCS,
    frozenset([ModelCapability.VISUAL_ANALYSIS]): AgentSpecialty.MULTIMODAL,
}


class CapabilityDetector:
    """Detects agent capabilities by analyzing available models"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get_available_models(self, endpoint: str) -> List[Dict]:
        """Get list of available models from Ollama endpoint"""
        try:
            # Handle endpoints with or without protocol
            if not endpoint.startswith(('http://', 'https://')):
                endpoint = f"http://{endpoint}"
            
            # Ensure endpoint has port if not specified
            if ':' not in endpoint.split('//')[-1]:
                endpoint = f"{endpoint}:11434"
            
            response = await self.client.get(f"{endpoint}/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except Exception as e:
            logger.error(f"Failed to get models from {endpoint}: {e}")
            return []
    
    def analyze_model_capabilities(self, model_name: str) -> List[ModelCapability]:
        """Analyze a single model to determine its capabilities"""
        capabilities = []
        
        # Normalize model name for matching
        normalized_name = model_name.lower().split(':')[0]  # Remove version tags
        
        # Check for exact matches first
        for pattern, caps in MODEL_CAPABILITIES.items():
            if pattern in normalized_name:
                capabilities.extend(caps)
                break
        
        # If no specific match, determine by model size and type
        if not capabilities:
            if any(size in normalized_name for size in ['3b', '7b']):
                capabilities.append(ModelCapability.LIGHTWEIGHT)
            capabilities.append(ModelCapability.GENERAL_AI)
        
        return list(set(capabilities))  # Remove duplicates
    
    def determine_agent_specialty(self, all_capabilities: List[ModelCapability]) -> AgentSpecialty:
        """Determine agent specialty based on combined model capabilities"""
        capability_set = frozenset(all_capabilities)
        
        # Check for exact specialty matches
        for caps, specialty in SPECIALTY_MAPPING.items():
            if caps.issubset(capability_set):
                return specialty
        
        # Fallback logic based on dominant capabilities
        if ModelCapability.CODE_GENERATION in all_capabilities:
            if ModelCapability.REASONING in all_capabilities:
                return AgentSpecialty.ADVANCED_CODING
            elif ModelCapability.CODE_REVIEW in all_capabilities:
                return AgentSpecialty.CODE_REVIEW_DOCS
            else:
                return AgentSpecialty.ADVANCED_CODING
        
        elif ModelCapability.REASONING in all_capabilities:
            return AgentSpecialty.REASONING_ANALYSIS
        
        elif ModelCapability.VISUAL_ANALYSIS in all_capabilities:
            return AgentSpecialty.MULTIMODAL
        
        else:
            return AgentSpecialty.GENERAL_AI
    
    async def detect_agent_capabilities(self, endpoint: str) -> Tuple[List[str], AgentSpecialty, List[ModelCapability]]:
        """
        Detect agent capabilities and determine specialty
        
        Returns:
            Tuple of (model_names, specialty, capabilities)
        """
        models = await self.get_available_models(endpoint)
        
        if not models:
            return [], AgentSpecialty.GENERAL_AI, [ModelCapability.GENERAL_AI]
        
        model_names = [model['name'] for model in models]
        all_capabilities = []
        
        # Analyze each model
        for model in models:
            model_caps = self.analyze_model_capabilities(model['name'])
            all_capabilities.extend(model_caps)
        
        # Remove duplicates and determine specialty
        unique_capabilities = list(set(all_capabilities))
        specialty = self.determine_agent_specialty(unique_capabilities)
        
        return model_names, specialty, unique_capabilities
    
    async def scan_cluster_capabilities(self, endpoints: List[str]) -> Dict[str, Dict]:
        """Scan multiple endpoints and return capabilities for each"""
        results = {}
        
        tasks = []
        for endpoint in endpoints:
            task = self.detect_agent_capabilities(endpoint)
            tasks.append((endpoint, task))
        
        # Execute all scans concurrently
        for endpoint, task in tasks:
            try:
                models, specialty, capabilities = await task
                results[endpoint] = {
                    'models': models,
                    'model_count': len(models),
                    'specialty': specialty,
                    'capabilities': capabilities,
                    'status': 'online' if models else 'offline'
                }
            except Exception as e:
                logger.error(f"Failed to scan {endpoint}: {e}")
                results[endpoint] = {
                    'models': [],
                    'model_count': 0,
                    'specialty': AgentSpecialty.GENERAL_AI,
                    'capabilities': [],
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Convenience function for quick capability detection
async def detect_capabilities(endpoint: str) -> Dict:
    """Quick capability detection for a single endpoint"""
    detector = CapabilityDetector()
    try:
        models, specialty, capabilities = await detector.detect_agent_capabilities(endpoint)
        return {
            'endpoint': endpoint,
            'models': models,
            'model_count': len(models),
            'specialty': specialty.value,
            'capabilities': [cap.value for cap in capabilities],
            'status': 'online' if models else 'offline'
        }
    finally:
        await detector.close()


if __name__ == "__main__":
    # Test the capability detector
    async def test_detection():
        endpoints = [
            "192.168.1.27:11434",  # WALNUT
            "192.168.1.113:11434", # IRONWOOD  
            "192.168.1.72:11434",  # ACACIA
        ]
        
        detector = CapabilityDetector()
        try:
            results = await detector.scan_cluster_capabilities(endpoints)
            for endpoint, data in results.items():
                print(f"\n{endpoint}:")
                print(f"  Models: {data['model_count']}")
                print(f"  Specialty: {data['specialty']}")
                print(f"  Capabilities: {data['capabilities']}")
                print(f"  Status: {data['status']}")
        finally:
            await detector.close()
    
    asyncio.run(test_detection())