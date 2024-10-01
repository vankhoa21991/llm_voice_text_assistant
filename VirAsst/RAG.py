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

from VirAsst.template.templates import Template
        
class ContentCreator:
    def __init__(self, num_web):
            self.num_web = num_web
            self.template = Template()
            self.get_splitter()
            self.get_llm()

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
            try:
                print("-----------------------------------")
                print("Getting links ...")

                wrapper = DuckDuckGoSearchAPIWrapper(max_results=self.num_web, source="text")
                search = DuckDuckGoSearchResults(api_wrapper=wrapper)
                results = search.run(tool_input=keyword)

                links = []
                for link in self.parse_links(results):
                    links.append(link)

                if additional_links:
                    for link in additional_links:
                        links.append(link)

                return links

            except Exception as e:
                print(f"An error occurred while getting links: {e}")

    def get_splitter(self):
        # Define splitter variable
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=400,
            add_start_index=True,
        )

    def get_llm(self):
        self.llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # api_key="...",  # if you prefer to pass api key in directly instaed of using env vars
                # base_url="...",
                # organization="...",
                # other params...
            )

    def create_blog_post(self, keyword, additional_links=None):
            try:
                print("-----------------------------------")
                print("Creating blog post ...")

                links = self.get_links(keyword=keyword,
                                       additional_links=additional_links)
                print(f"Links: {links}")

                docs = []

                # Load documents
                bs4_strainer = bs4.SoupStrainer(('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'))

                document_loader = WebBaseLoader(web_path=(links))

                docs = document_loader.load()

                # Split documents
                splits = self.splitter.split_documents(docs)

                # step 3: Indexing and vector storage
                vector_store = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())

                # step 4: retrieval
                retriever = vector_store.as_retriever(search_type="similarity", search_kwards={"k": 10})

                # step 5 : Generation
                prompt = PromptTemplate.from_template(template=self.template.get_template())

                chain = (
                    {"context": retriever | format_docs, "keyword": RunnablePassthrough()}
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )
                
                return chain.invoke(input=keyword)

            except Exception as e:
                return e

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)