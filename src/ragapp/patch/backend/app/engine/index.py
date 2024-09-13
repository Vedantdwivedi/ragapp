import logging
import os

from app.engine.llamacloud_index import IndexConfig as LlamaCloudIndexConfig
from app.engine.llamacloud_index import get_index as get_llama_cloud_index
from app.engine.vectordb import get_vector_store
from llama_index.core.callbacks import CallbackManager
from llama_index.core.indices import VectorStoreIndex
from pydantic import BaseModel, Field

logger = logging.getLogger("uvicorn")


# For compatibility with create-llama code
class IndexConfig:
    def __call__(self, **kwargs):
        if os.getenv("USE_LLAMA_CLOUD", "false").lower() == "true":
            return LlamaCloudIndexConfig
        else:
            return VectorStoreIndexConfig


class VectorStoreIndexConfig(BaseModel):
    callback_manager: CallbackManager = Field(default=CallbackManager())


def get_vector_store_index(config: VectorStoreIndexConfig):
    store = get_vector_store()
    # Load the index from the vector store
    # If you are using a vector store that doesn't store text,
    # you must load the index from both the vector store and the document store
    index = VectorStoreIndex.from_vector_store(
        store, callback_manager=config.callback_manager
    )
    logger.info("Finished load index from vector store.")
    return index


def get_index(**kwargs):
    if os.getenv("USE_LLAMA_CLOUD", "false").lower() == "true":
        config = LlamaCloudIndexConfig(
            callback_manager=kwargs.get("callback_manager"),
            llama_cloud_pipeline_config=kwargs.get("llama_cloud_pipeline_config"),
        )
        return get_llama_cloud_index(config)
    else:
        config = VectorStoreIndexConfig(
            callback_manager=kwargs.get("callback_manager"),
        )
        return get_vector_store_index(config)


# For compatibility with create-llama code (PrivateFileService)
def get_client():
    if os.getenv("USE_LLAMA_CLOUD", "false").lower() == "true":
        from app.engine.llamacloud_index import get_client

        return get_client()
    else:
        return None
