"""
Multi-provider LLM client factory
Supports: Groq, OpenAI, Ollama
"""
from abc import ABC, abstractmethod
from typing import Optional
import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from ...config import settings, get_llm_config


class LLMClient(ABC):
    """Abstract LLM client"""
    
    @abstractmethod
    def get_chat_model(self, temperature: float = 0.7) -> BaseChatModel:
        """Get chat model instance"""
        pass


class GroqLLMClient(LLMClient):
    """Groq LLM client (FREE and FAST)"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        # Set env var for LangChain
        os.environ["GROQ_API_KEY"] = api_key
    
    def get_chat_model(self, temperature: float = 0.7) -> BaseChatModel:
        """Get Groq chat model"""
        return ChatGroq(
            model=self.model,
            temperature=temperature,
            groq_api_key=self.api_key,
        )


class OpenAILLMClient(LLMClient):
    """OpenAI LLM client"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        # Set env var for LangChain
        os.environ["OPENAI_API_KEY"] = api_key
    
    def get_chat_model(self, temperature: float = 0.7) -> BaseChatModel:
        """Get OpenAI chat model"""
        return ChatOpenAI(
            model=self.model,
            temperature=temperature,
            openai_api_key=self.api_key,
        )


class OllamaLLMClient(LLMClient):
    """Ollama LLM client (local, completely free)"""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
    
    def get_chat_model(self, temperature: float = 0.7) -> BaseChatModel:
        """Get Ollama chat model"""
        from langchain_community.chat_models import ChatOllama
        
        return ChatOllama(
            base_url=self.base_url,
            model=self.model,
            temperature=temperature,
        )


def create_llm_client() -> LLMClient:
    """Factory function to create LLM client based on configuration"""
    config = get_llm_config()
    provider = config["provider"]
    
    if provider == "groq":
        return GroqLLMClient(
            api_key=config["api_key"],
            model=config["model"],
        )
    elif provider == "openai":
        return OpenAILLMClient(
            api_key=config["api_key"],
            model=config["model"],
        )
    elif provider == "ollama":
        return OllamaLLMClient(
            base_url=config["base_url"],
            model=config["model"],
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get global LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = create_llm_client()
    return _llm_client
