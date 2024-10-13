import os
import re
import bs4
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import LlamaCppEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings

from VirAsst.template.templates import Template

embedding_list = {
     
     "all-MiniLM-L6-v2.F16": 
     {
            "model_path": "../models/all-MiniLM-L6-v2.F16.gguf",
            "embedding": LlamaCppEmbeddings
        },
    "gpt-4o": OpenAIEmbeddings(model="gpt-4o"),
     "gpt-4": OpenAIEmbeddings(model="gpt-4"),
}

class EmbeddingHandler:
    def __init__(self, model_name):
        self.model_name = model_name
        self.embedding = self.get_embedding()

    def get_embedding(self):
        if self.model_name == "all-MiniLM-L6-v2.F16":
            return embedding_list[self.model_name]["embedding"](model_path=embedding_list[self.model_name]["model_path"])
        elif 'gpt' in self.model_name:
            return embedding_list[self.model_name]

class VectorDB:
    def __init__(self, num_web, embedding_name, **kwargs):
            self.num_web = num_web
            self.template = Template()
            self.get_splitter()
            self.get_embedding(embedding_name)
            self.vector_store_path = kwargs.get("vector_store_path", "vectorstore")

    def parse_links(self, search_results: str):
            print("-----------------------------------")
            print("Parsing links ...")
            return re.findall(r'link:\s*(https?://[^\],\s]+)', search_results)

    def save_file(self, content: str, filename: str):
            print("-----------------------------------")
            print("Saving file in blogs ...")
            directory = "blogs"
            if not os.path.exists(directory):
                os.makedirs(directory)
            filepath = os.path.join(directory, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f" 🥳 File saved as {filepath}")

    def get_links(self, keyword, additional_links=None):
            links = []
            try:
                print("-----------------------------------")
                print("Getting links ...")

                wrapper = DuckDuckGoSearchAPIWrapper(max_results=self.num_web, source="text")
                search = DuckDuckGoSearchResults(api_wrapper=wrapper)
                results = search.run(tool_input=keyword)

                for link in self.parse_links(results):
                    links.append(link)

            except Exception as e:
                print(f"An error occurred while getting links: {e}")

            if additional_links:
                for link in additional_links:
                    links.append(link)

            return links

    def get_splitter(self):
        # Define splitter variable
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=400,
            add_start_index=True,
        )
        
    def get_embedding(self, model_name):
        self.embedding = EmbeddingHandler(model_name=model_name).embedding
    
    def collect_docs_from_url(self, keyword, additional_links=None):
        links = self.get_links(keyword=keyword,
                                       additional_links=additional_links)
        print(f"Links: {links}")

        docs = []

        # Load documents
        bs4_strainer = bs4.SoupStrainer(('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'))

        document_loader = WebBaseLoader(web_path=(links))

        docs = document_loader.load()

        # docs = format_docs(docs)
        return docs
    
    def collect_docs_from_pdf(self, pdf_file):
        loader=PyPDFLoader(pdf_file)
           
        return loader.load()

    
    def collect_docs_from_text(self, text_file):
        return TextLoader(text_file).load()
    
    def create_vectorDB(self, keyword, additional_links=None, localfiles=None):
        try:
            print("-----------------------------------")
            print("Creating blog post ...")

            doc_urls = self.collect_docs_from_url(keyword=keyword, 
                                                    additional_links=additional_links)
            if localfiles:
                print("Local files found ...")
                print(localfiles)
                for filepath in localfiles:
                    if filepath.endswith(".pdf"):
                        doc_urls.extend(self.collect_docs_from_pdf(filepath))
                    elif filepath.endswith(".txt"):
                        doc_urls.extend(self.collect_docs_from_text(filepath))
                    print('Local files loaded ...')
            
            docs = doc_urls

            print(f"Number of documents: {len(docs)}")
            print("Splitting documents ...")
            splits = self.splitter.split_documents(docs)

            # step 3: Indexing and vector storage
            print("Indexing and vector storage ...")
            vector_store = FAISS.from_documents(documents=splits, embedding=self.embedding)
            
            print("Saving vectorDB ...")
            self.save_vectorDB(keyword, vector_store)
            print("VectorDB created successfully!")

        except Exception as e:
            print(f"An error occurred while creating vectorDB: {e}")
            return e
        return
            
    def save_vectorDB(self, keyword, vector_store):

        if os.path.exists(f"{self.vector_store_path}/{keyword}"):
            print("Merging vectorDB ...")
            local_index=FAISS.load_local(f'{self.vector_store_path}/{keyword}', self.embedding,
                                             allow_dangerous_deserialization=True)
            local_index.merge_from(vector_store)
            local_index.save_local(f'{self.vector_store_path}/{keyword}')
        else:
            print('Creating new vectorDB ...')
            vector_store.save_local(folder_path=f'{self.vector_store_path}/{keyword}')
        return
    
    def load_vectorDB(self, keyword):
        self.vector_store = FAISS.load_local(f'{self.vector_store_path}/{keyword}', self.embedding,
                                             allow_dangerous_deserialization=True)
    
    def retrieve(self, query):
        retriever = self.vector_store.as_retriever(search_type="similarity", 
                                                   search_kwargs={"k": 10})
        return retriever.invoke(query)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

if __name__ == "__main__":
    creator = VectorDB(num_web=10, embedding_name="all-MiniLM-L6-v2.F16")

    # if os.path.exists("./vectorstore/python"):
    #     print("Loading vectorDB for Python ...")
    #     creator.load_vectorDB("python")
    # else:
    print("Creating vectorDB for Python ...")
    creator.create_vectorDB(keyword="python", additional_links=["https://www.python.org"])

    creator.load_vectorDB("python")
    query = "What is Python?"
    response = creator.retrieve(query)
    print(response)