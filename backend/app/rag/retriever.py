from app.rag.chroma_client import chroma_client
from app.rag.embedding import embedding_model


class KnowledgeRetriever:
    def __init__(self, collection=None):
        # Production always resolves the current collection from the server;
        # a cached collection handle becomes stale if Chroma is recreated.
        # Tests can inject a fake collection through this argument.
        self._injected_collection = collection

    @property
    def collection(self):
        if self._injected_collection is not None:
            return self._injected_collection
        return chroma_client.get_collection()

    def search(self, query: str, k: int = 3):
        """Return a list of ``{content, metadata}`` dictionaries.

        Connection and embedding errors are allowed to propagate so callers can
        decide whether to degrade gracefully; ``BaseAgent.safe_retrieval`` does
        exactly that for the chat pipeline.
        """
        if not query or not query.strip():
            return []

        query_embedding = embedding_model.get_model().embed_query(query)
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max(1, k),
            include=["documents", "metadatas"],
        )

        documents = (result.get("documents") or [[]])[0] or []
        metadatas = (result.get("metadatas") or [[]])[0] or []
        if not metadatas:
            metadatas = [{} for _ in documents]

        return [
            {"content": doc, "metadata": metadata or {}}
            for doc, metadata in zip(documents, metadatas)
        ]


retriever = KnowledgeRetriever()
