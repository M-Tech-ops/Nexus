"""
Standalone smoke test — confirms the GGUF model loads and generates
correctly before you wire anything up to FastAPI or the Qt frontend.

Usage:
    python test_model.py "path/to/your-model.gguf"
"""

import sys
import time

sys.path.insert(0, "backend")  # so `from ai.ai_manager import AIManager` resolves
from ai.ai_manager import AIManager  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python test_model.py <path-to-gguf>")
        sys.exit(1)

    model_path = sys.argv[1]

    print(f"Loading model from: {model_path}")
    start = time.time()
    ai = AIManager(model_path=model_path)  # bump n_gpu_layers if you have a GPU build
    print(f"Model loaded in {time.time() - start:.1f}s\n")

    prompt = "In one sentence, what is a dynamic island UI?"
    print(f"Prompt: {prompt}\n")

    print("--- Non-streaming ---")
    start = time.time()
    response = ai.chat(prompt)
    print(response)
    print(f"({time.time() - start:.1f}s)\n")

    print("--- Streaming ---")
    start = time.time()
    for chunk in ai.generate_stream(prompt):
        print(chunk, end="", flush=True)
    print(f"\n({time.time() - start:.1f}s)")


if __name__ == "__main__":
    main()