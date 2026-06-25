"""Provider-agnostic LLM gateway using LiteLLM."""

import json
import logging
from typing import TypeVar, Type

import litellm
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from confidence_scorer.llm.models import LLMConfig, LLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T")

# Suppress LiteLLM's verbose default logging
litellm.suppress_debug_info = True


def _to_api_messages(messages: list[BaseMessage | dict]) -> list[dict]:
    """Turn message objects into plain dicts — the format every LLM API understands."""
    result = []
    for m in messages:
        if isinstance(m, dict):
            result.append(m)
        elif isinstance(m, SystemMessage):
            result.append({"role": "system", "content": str(m.content)})
        elif isinstance(m, HumanMessage):
            result.append({"role": "user", "content": str(m.content)})
        elif isinstance(m, AIMessage):
            msg: dict = {"role": "assistant", "content": str(m.content) if m.content else ""}
            if m.tool_calls:
                msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["args"]),
                        },
                    }
                    for tc in m.tool_calls
                ]
            result.append(msg)
        elif isinstance(m, ToolMessage):
            result.append({
                "role": "tool",
                "content": str(m.content),
                "tool_call_id": m.tool_call_id,
            })
    return result


def _to_ai_message(response) -> AIMessage:
    """Wrap the raw API response in an AIMessage so LangGraph can store it in state."""
    choice = response.choices[0].message
    content = choice.content or ""
    tool_calls = []
    if getattr(choice, "tool_calls", None):
        for tc in choice.tool_calls:
            tool_calls.append({
                "id": tc.id,
                "name": tc.function.name,
                "args": json.loads(tc.function.arguments or "{}"),
                "type": "tool_call",
            })
    return AIMessage(content=content, tool_calls=tool_calls)


class LLMGateway:
    """Provider-agnostic LLM client."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    def _base_kwargs(self) -> dict:
        kwargs: dict = {
            "model": self.config.litellm_model,
            "temperature": self.config.temperature,
        }
        if self.config.max_tokens:
            kwargs["max_tokens"] = self.config.max_tokens
        if self.config.provider == LLMProvider.OLLAMA and self.config.base_url:
            kwargs["api_base"] = self.config.base_url
        return kwargs

    def invoke(self, messages: list) -> AIMessage:
        """Send messages to the LLM and return its reply."""
        messages_dict = _to_api_messages(messages)
        response = litellm.completion(messages=messages_dict, **self._base_kwargs())
        return _to_ai_message(response)

    def structured(self, messages: list, response_model: Type[T]) -> T:
        """Ask the LLM for a validated Pydantic response."""
        messages_dict = _to_api_messages(messages)
        response = litellm.completion(
            messages=messages_dict,
            response_format=response_model,
            **self._base_kwargs(),
        )
        content = response.choices[0].message.content
        return response_model.model_validate_json(content)

    def invoke_with_tools(self, messages: list, tools: list[dict]) -> AIMessage:
        """Let the model choose a tool call from available tools."""
        messages_dict = _to_api_messages(messages)
        formatted_tools = [{"type": "function", "function": t} for t in tools]
        response = litellm.completion(
            messages=messages_dict,
            tools=formatted_tools,
            tool_choice="auto",
            **self._base_kwargs(),
        )
        return _to_ai_message(response)


def get_gateway(config: LLMConfig) -> LLMGateway:
    """Create a gateway from an explicit config."""
    return LLMGateway(config)


def default_gateway() -> LLMGateway:
    """Create a gateway from environment config. Used by all internal callers."""
    from confidence_scorer.config import LLM_CONFIG
    return LLMGateway(LLM_CONFIG)
