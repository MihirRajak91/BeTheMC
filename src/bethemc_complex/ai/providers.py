"""
Provider implementations for different LLM and embedder services.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.llms import Anthropic
from langchain.llms.base import BaseLLM
from langchain.embeddings.base import Embeddings
import requests

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
    """Local Llama 3 API provider."""
    def get_llm(self, config: Dict[str, Any]) -> BaseLLM:
        class LocalLlamaLLM(BaseLLM):
            api_base: str
            model: str
            temperature: float
            max_tokens: int
            def __init__(self, api_base, model, temperature, max_tokens):
                super().__init__(api_base=api_base, model=model, temperature=temperature, max_tokens=max_tokens)
            def invoke(self, messages):
                prompt = "\n".join([m.content for m in messages])
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                }
                response = requests.post(
                    self.api_base,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                class Response:
                    def __init__(self, content):
                        self.content = content
                return Response(result.get("response", result.get("content", "")))

            def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
                results = []
                for prompt in prompts:
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": self.max_tokens
                        }
                    }
                    response = requests.post(
                        self.api_base,
                        json=payload,
                        timeout=60
                    )
                    response.raise_for_status()
                    result = response.json()
                    text = result.get("response", result.get("content", ""))
                    results.append({"text": text})
                return {"generations": [[r] for r in results]}

            @property
            def _llm_type(self):
                return "local-llama"
        return LocalLlamaLLM(
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