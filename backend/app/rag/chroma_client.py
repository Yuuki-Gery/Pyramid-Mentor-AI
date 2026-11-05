import chromadb

from app.core.config import settings


class ChromaClient:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        # Create the HTTP client lazily so importing the app does not require a
        # running Chroma instance during unit tests or health checks.
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
        return self._client

    def get_collection(self, name: str = "pyramid_knowledge"):
        return self.client.get_or_create_collection(name=name)


chroma_client = ChromaClient()
