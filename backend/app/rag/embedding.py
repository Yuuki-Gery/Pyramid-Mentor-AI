class EmbeddingModel:
    def __init__(self):
        self._model = None

    def get_model(self):
        if self._model is None:
            # Importing/loading the model is deferred until retrieval is
            # actually used, keeping API startup fast and testable.
            from langchain_community.embeddings import HuggingFaceEmbeddings

            self._model = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh-v1.5"
            )
        return self._model


embedding_model = EmbeddingModel()
