import hashlib

from app.rag.chroma_client import chroma_client
from app.rag.embedding import embedding_model


class KnowledgeBase:
    def __init__(self, collection=None):
        # Resolve the collection per ingestion run instead of caching a handle
        # across Chroma container restarts. Tests may inject a fake collection.
        self._injected_collection = collection

    @property
    def collection(self):
        if self._injected_collection is not None:
            return self._injected_collection
        return chroma_client.get_collection()

    def add_documents(self, documents):
        if not documents:
            return 0

        texts = [doc.page_content for doc in documents]
        embeddings = embedding_model.get_model().embed_documents(texts)
        metadatas = [doc.metadata or {} for doc in documents]

        # Deterministic IDs make ingestion idempotent: loading the same corpus
        # twice updates existing chunks instead of failing on duplicate IDs.
        ids = []
        for text, metadata in zip(texts, metadatas):
            digest = hashlib.sha256()
            digest.update(str(metadata.get("source", "")).encode("utf-8"))
            digest.update(b"\0")
            digest.update(text.encode("utf-8"))
            ids.append(digest.hexdigest())

        self.collection.upsert(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        return len(texts)


knowledge_base = KnowledgeBase()
