"""
Provider implementations for different LLM and embedder services.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator
import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.llms import Anthropic
from langchain.llms.base import BaseLLM
from langchain.embeddings.base import Embeddings
import requests
import json

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def get_llm(self, config: Dict[str, Any]) -> BaseLLM:
        """Get the LLM instance."""
        pass

class EmbedderProvider(ABC):
    """Base class for embedder providers."""
    
    @abstractmethod
    def get_embedder(self, config: Dict[str, Any]) -> Embeddings:
        """Get the embedder instance."""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def get_llm(self, config: Dict[str, Any]) -> BaseLLM:
        """Get OpenAI LLM instance."""
        return ChatOpenAI(
            model_name=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            openai_api_base=config.get("api_base"),
            openai_api_key=config.get("api_key") or os.getenv("OPENAI_API_KEY")
        )

class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider."""
    
    def get_llm(self, config: Dict[str, Any]) -> BaseLLM:
        """Get Anthropic LLM instance."""
        return Anthropic(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            anthropic_api_key=config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        )

class OpenAIEmbedderProvider(EmbedderProvider):
    """OpenAI embedder provider."""
    
    def get_embedder(self, config: Dict[str, Any]) -> Embeddings:
        """Get OpenAI embedder instance."""
        return OpenAIEmbeddings(
            model=config["model"],
            openai_api_base=config.get("api_base"),
            openai_api_key=config.get("api_key") or os.getenv("OPENAI_API_KEY")
        )

class HuggingFaceEmbedderProvider(EmbedderProvider):
    """HuggingFace embedder provider."""
    
    def get_embedder(self, config: Dict[str, Any]) -> Embeddings:
        """Get HuggingFace embedder instance."""
        return HuggingFaceEmbeddings(
            model_name=config["model"],
            model_kwargs={"device": config.get("device", "cpu")}
        )

class LocalLlamaProvider(LLMProvider):
    """Enhanced Local Ollama API provider with streaming support."""
    
    def get_llm(self, config: Dict[str, Any]) -> BaseLLM:
        class EnhancedOllamaLLM(BaseLLM):
            """Enhanced Ollama LLM with proper streaming support."""
            
            api_base: str = ""
            model: str = ""
            temperature: float = 0.8
            max_tokens: int = 1500
            
            def __init__(self, api_base, model, temperature, max_tokens):
                super().__init__()
                self.api_base = api_base
                self.model = model
                self.temperature = temperature
                self.max_tokens = max_tokens
            
            class Config:
                """Pydantic config to allow arbitrary types."""
                arbitrary_types_allowed = True
                extra = "allow"
            
            def invoke(self, messages):
                """Invoke the LLM with enhanced prompt formatting."""
                # Handle different message formats
                if hasattr(messages, 'format_messages'):
                    # This is a prompt template
                    prompt = str(messages)
                elif isinstance(messages, list):
                    # List of messages
                    prompt = "\n".join([
                        str(m.content) if hasattr(m, 'content') else str(m) 
                        for m in messages
                    ])
                else:
                    # Simple string
                    prompt = str(messages)
                
                return self._generate_response(prompt)
            
            def _generate_response(self, prompt: str, stream: bool = False):
                """Generate response using the Ollama API."""
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": stream,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                }
                
                try:
                    response = requests.post(
                        self.api_base,
                        json=payload,
                        timeout=120,  # Increased timeout for larger models
                        stream=stream
                    )
                    response.raise_for_status()
                    
                    if stream:
                        return self._handle_streaming_response(response)
                    else:
                        result = response.json()
                        content = result.get("response", result.get("content", ""))
                        
                        class Response:
                            def __init__(self, content):
                                self.content = content
                        
                        return Response(content)
                
                except requests.exceptions.RequestException as e:
                    print(f"Error calling Ollama API: {e}")
                    class ErrorResponse:
                        def __init__(self, error):
                            self.content = f"Error: {error}"
                    return ErrorResponse(str(e))
            
            def _handle_streaming_response(self, response) -> str:
                """Handle streaming response from Ollama API."""
                full_content = ""
                
                try:
                    for line in response.iter_lines():
                        if line:
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                if 'response' in chunk:
                                    full_content += chunk['response']
                                    # Optional: yield chunk for real-time display
                                if chunk.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                
                except Exception as e:
                    print(f"Error processing streaming response: {e}")
                
                class StreamResponse:
                    def __init__(self, content):
                        self.content = content
                
                return StreamResponse(full_content)
            
            def generate_enhanced_story(self, enhanced_context: Dict[str, Any]) -> str:
                """Generate story using enhanced context."""
                prompt = self._build_enhanced_prompt(enhanced_context)
                response = self._generate_response(prompt)
                return response.content
            
            def _build_enhanced_prompt(self, context: Dict[str, Any]) -> str:
                """Build an enhanced prompt using our rich context data."""
                prompt_parts = []
                
                # Base instruction
                prompt_parts.append("You are creating an anime-style Pokémon adventure story. ")
                prompt_parts.append("Use the following rich context to create an immersive, character-driven narrative:")
                prompt_parts.append("")
                
                # Location context
                if context.get('location_atmosphere'):
                    prompt_parts.append(f"🏞️ LOCATION: {context['location_atmosphere']}")
                    prompt_parts.append("")
                
                # Character personalities
                if context.get('character_personalities'):
                    prompt_parts.append("👥 CHARACTERS:")
                    for char in context['character_personalities']:
                        prompt_parts.append(f"   • {char}")
                    prompt_parts.append("")
                
                # Pokémon personalities
                if context.get('pokemon_personalities'):
                    prompt_parts.append("🐾 POKÉMON:")
                    for pokemon in context['pokemon_personalities']:
                        prompt_parts.append(f"   • {pokemon}")
                    prompt_parts.append("")
                
                # Seasonal atmosphere
                if context.get('seasonal_atmosphere'):
                    prompt_parts.append(f"🌸 SEASON: {context['seasonal_atmosphere']}")
                    prompt_parts.append("")
                
                # Recent events
                if context.get('recent_events'):
                    prompt_parts.append("📖 RECENT EVENTS:")
                    for event in context['recent_events']:
                        prompt_parts.append(f"   • {event}")
                    prompt_parts.append("")
                
                # Story generation instructions
                prompt_parts.append("Create a compelling 2-3 paragraph scene that:")
                prompt_parts.append("• Shows character personalities through actions and dialogue")
                prompt_parts.append("• Incorporates the location's unique atmosphere")
                prompt_parts.append("• Reflects the seasonal mood and events")
                prompt_parts.append("• Uses anime-style emotional storytelling")
                prompt_parts.append("• Ends with meaningful choices for the player")
                prompt_parts.append("")
                prompt_parts.append("Begin the story:")
                
                return "\n".join(prompt_parts)

            def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
                """Generate responses for multiple prompts."""
                results = []
                for prompt in prompts:
                    response = self._generate_response(prompt)
                    results.append({"text": response.content})
                return {"generations": [[r] for r in results]}

            @property
            def _llm_type(self):
                return "enhanced-ollama"
        
        return EnhancedOllamaLLM(
            api_base=config["api_base"],
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"]
        )

def get_llm_provider(provider_name: str) -> LLMProvider:
    """Get LLM provider by name."""
    providers = {
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
        "local": LocalLlamaProvider(),
    }
    if provider_name not in providers:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    return providers[provider_name]

def get_embedder_provider(provider_name: str) -> EmbedderProvider:
    """Get embedder provider by name."""
    providers = {
        "openai": OpenAIEmbedderProvider(),
        "sentence-transformers": HuggingFaceEmbedderProvider(),
    }
    if provider_name not in providers:
        raise ValueError(f"Unknown embedder provider: {provider_name}")
    return providers[provider_name] 