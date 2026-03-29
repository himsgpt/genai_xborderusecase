"""
Agents layer — AI/LLM-powered intelligence.

Uses Groq (Llama 3.1 70B) to enhance deterministic analysis with:
- Contextual explanations
- Dynamic, data-driven recommendations
- Portfolio-level pattern detection
- Anomaly flagging

The core product works WITHOUT LLM. Agents add differentiated intelligence.
"""
from .analysis_agent import enhance_single_analysis, enhance_batch_analysis
from .llm_client import call_llm

__all__ = ["enhance_single_analysis", "enhance_batch_analysis", "call_llm"]
