import os

from app.engine.constants import DEFAULT_RERANK_TOP_K
from llama_index.core.postprocessor.types import BaseNodePostprocessor


def get_cohere_reranker():
    from llama_index.postprocessor.cohere_rerank import CohereRerank

    api_key = os.getenv("COHERE_API_KEY")
    rerank_top_k = int(os.getenv("RERANK_TOP_K", DEFAULT_RERANK_TOP_K))
    if api_key is None:
        raise ValueError(
            "Please set your COHERE_API_KEY. Get it from https://dashboard.cohere.com/api-keys"
        )

    return CohereRerank(
        api_key=api_key,
        top_n=rerank_top_k,
    )


def get_reranker() -> BaseNodePostprocessor:
    rerank_provider = os.getenv("RERANK_PROVIDER")
    if rerank_provider is None:
        raise ValueError("RERANK_PROVIDER is not set")

    if rerank_provider == "cohere":
        return get_cohere_reranker()
    else:
        raise ValueError(f"Unknown rerank provider: {rerank_provider}")
