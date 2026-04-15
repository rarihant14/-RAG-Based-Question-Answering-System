from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_chunks(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)