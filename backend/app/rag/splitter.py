from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )


    def split(
        self,
        documents
    ):

        return self.splitter.split_documents(
            documents
        )


text_splitter = TextSplitter()