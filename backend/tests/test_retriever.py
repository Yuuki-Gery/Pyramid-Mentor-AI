import pytest

from app.rag.retriever import KnowledgeRetriever


class FakeEmbeddingModel:
    def embed_query(self, query):
        assert query
        return [0.1, 0.2]


class FakeCollection:
    def __init__(self, result=None, error=None):
        self.result = result or {}
        self.error = error
        self.last_kwargs = None

    def query(self, **kwargs):
        self.last_kwargs = kwargs
        if self.error:
            raise self.error
        return self.result


def make_retriever(monkeypatch, collection):
    retriever = KnowledgeRetriever(collection=collection)
    monkeypatch.setattr(
        "app.rag.retriever.embedding_model.get_model",
        lambda: FakeEmbeddingModel(),
    )
    return retriever


def test_search_returns_complete_result_shape(monkeypatch):
    collection = FakeCollection({
        "documents": [["SCQA 是结构化表达方法"]],
        "metadatas": [[{"source": "scqa.pdf"}]],
    })
    retriever = make_retriever(monkeypatch, collection)

    results = retriever.search("SCQA", k=3)

    assert results == [
        {"content": "SCQA 是结构化表达方法", "metadata": {"source": "scqa.pdf"}}
    ]
    assert collection.last_kwargs["n_results"] == 3


def test_search_without_results_returns_empty_list(monkeypatch):
    collection = FakeCollection({"documents": [[]], "metadatas": [[]]})
    retriever = make_retriever(monkeypatch, collection)

    assert retriever.search("unknown") == []


def test_search_handles_missing_metadata(monkeypatch):
    collection = FakeCollection({"documents": [["text"]], "metadatas": None})
    retriever = make_retriever(monkeypatch, collection)

    assert retriever.search("query") == [{"content": "text", "metadata": {}}]


def test_search_propagates_service_error(monkeypatch):
    collection = FakeCollection(error=RuntimeError("chroma unavailable"))
    retriever = make_retriever(monkeypatch, collection)

    with pytest.raises(RuntimeError, match="chroma unavailable"):
        retriever.search("query")


def test_search_empty_query_short_circuits(monkeypatch):
    collection = FakeCollection({"documents": [["text"]]})
    retriever = make_retriever(monkeypatch, collection)

    assert retriever.search("   ") == []
    assert collection.last_kwargs is None
