"""
AI Manager

Wraps llama-cpp-python to load a local GGUF model and run inference.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from llama_cpp import Llama


class AIManager:
    def __init__(
            self,
            model_path: str | Path,
            n_ctx: int = 4096,
            n_gpu_layers: int = 0,
            verbose: bool = True,
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

    def generate(
            self,
            prompt: str,
            max_tokens: int = 2048,
            temperature: float = 0.7,
    ) -> str:
        result = self._llm.create_chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return result["choices"][0]["message"]["content"]

    def generate_stream(
            self,
            prompt: str,
            max_tokens: int = 2048,
            temperature: float = 0.7,
    ) -> Iterator[str]:
        stream = self._llm.create_chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        for chunk in stream:
            delta = chunk["choices"][0]["delta"]

            if "content" in delta:
                yield delta["content"]
