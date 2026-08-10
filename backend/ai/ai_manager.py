"""
AI Manager

Wraps llama-cpp-python to load a local GGUF model
and run inference with conversation history.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, List, Dict

from llama_cpp import Llama


class AIManager:

    def __init__(
        self,
        model_path: str | Path,
        n_ctx: int = 8192,
        n_gpu_layers: int = -1,
        verbose: bool = False,
    ) -> None:

        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"GGUF model not found at: {model_path}"
            )

        self._llm = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=verbose,
        )

    # ---------------------------------------------------------
    # Non-streaming generation
    # ---------------------------------------------------------

    def generate(
        self,
        prompt: str,
        history: List[Dict[str, str]] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:

        messages = self._build_messages(
            prompt,
            history,
        )

        result = self._llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return result["choices"][0]["message"]["content"]

    # ---------------------------------------------------------
    # Streaming generation
    # ---------------------------------------------------------

    def generate_stream(
        self,
        prompt: str,
        history: List[Dict[str, str]] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> Iterator[str]:

        messages = self._build_messages(
            prompt,
            history,
        )

        stream = self._llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        for chunk in stream:

            delta = chunk["choices"][0]["delta"]

            if "content" in delta:
                yield delta["content"]

    # ---------------------------------------------------------
    # Build messages
    # ---------------------------------------------------------

    @staticmethod
    def _build_messages(
        prompt: str,
        history: List[Dict[str, str]] | None,
    ) -> List[Dict[str, str]]:

        messages = []

        if history:
            messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        return messages