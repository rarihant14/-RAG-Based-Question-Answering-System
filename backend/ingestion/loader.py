from langchain_community.document_loaders import PyPDFLoader, TextLoader

def load_docs(path):
    if path.endswith(".pdf"):
        loader = PyPDFLoader(path)
    else:
        loader = TextLoader(path)

    return loader.load()
