from langchain_community.document_loaders import PyPDFLoader, TextLoader


class DocumentLoader:

    def load_pdf(
        self,
        path: str
    ):

        loader = PyPDFLoader(path)

        documents = loader.load()


        for doc in documents:

            doc.metadata = {
                "source": "scqa.pdf",
                "category": "thinking_framework",
                "chapter": "SCQA"
            }


        return documents


    def load_text(
        self,
        path: str,
        source: str = "pyramid_principle",
        category: str = "pyramid_principle",
        chapter: str = "全书"
    ):

        loader = TextLoader(
            path,
            encoding="utf-8"
        )

        documents = loader.load()


        for doc in documents:

            doc.metadata = {
                "source": source,
                "category": category,
                "chapter": chapter
            }


        return documents



document_loader = DocumentLoader()
