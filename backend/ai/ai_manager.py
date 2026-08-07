"""
AI Manager

Wraps llama-cpp-python to load a local GGUF model and run inference.
This is the Python-side equivalent of the llama.cpp integration you built
directly in C++ for the hackathon build — same underlying engine, Python
bindings instead of linking the library directly.
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
        verbose: bool = False,
    ) -> None:
        """
        model_path: path to your Llama 3.2 3B Instruct GGUF file.
        n_ctx: context window size in tokens.
        n_gpu_layers: number of layers to offload to GPU. Leave at 0 for
            CPU-only. If you have an NVIDIA GPU and built llama-cpp-python
            with CUDA support (see backend/README.md), set this to 99 to
            offload as many layers as possible — same idea as the -ngl flag
            you used with the raw llama.cpp CLI.
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"GGUF model not found at: {model_path}")

        self._llm = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=verbose,
        )

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7) -> str:
        """One-shot generation, non-streaming. Good for a first smoke test."""
        result = self._llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return result["choices"][0]["message"]["content"]
    def generate_stream(
        self, prompt: str, max_tokens: int = 256, temperature: float = 0.7
    ) -> Iterator[str]:
        """
        Streaming generation — yields text chunks as they're produced.
        This is what you'll want for the FastAPI WebSocket endpoint later,
        so the Qt widget can render tokens as they arrive instead of
        waiting for the full response.
        """
        stream = self._llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]