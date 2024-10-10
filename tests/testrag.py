from rich.markdown import Markdown
import warnings
warnings.filterwarnings(action='ignore')
from typing import List

from langchain.text_splitter import TokenTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import LlamaCppEmbeddings
from llama_cpp import Llama
from langchain_text_splitters import CharacterTextSplitter


modelpath = "models/llama-3.2-1b-instruct-q4_k_m.gguf"
repo_id = "hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF"
filename= "*q4_k_m.gguf"

class LlamaCppEmbeddings_(LlamaCppEmbeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using the Llama model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings = [self.client.embed(text)[0] for text in texts]
        return [list(map(float, e)) for e in embeddings]

    def embed_query(self, text: str) -> List[float]:
        """Embed a query using the Llama model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        embedding = self.client.embed(text)[0]
        return list(map(float, embedding))


# Use the updated LlamaCppEmbeddingsWithFix
embeddings = LlamaCppEmbeddings_(model_path=modelpath, n_gpu_layers=0, verbose=False)

qwen05b = Llama(
    model_path=modelpath,
    n_gpu_layers=0,
    temperature=0.1,
    top_p = 0.5,
    n_ctx=8192,
    max_tokens=600,
    repeat_penalty=1.7,
    stop=["<|im_end|>", "Instruction:", "### Instruction:", "###", ""],
    verbose=False,
)

# Load a TXT document
loader = TextLoader("tests/text.txt")
documents = loader.load()

# Create a document and split into chunks
text_splitter = TokenTextSplitter(chunk_size=250, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Create the vector store
vectorstore = FAISS.from_documents(documents=texts, embedding=embeddings)

# Default is similarity search
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 3})

# Invoke the retriever with a query
docs = retriever.invoke("what is the document about?")
print(docs)

query = "what is the document about?"

# pack all the text from the retriever hits and remove carriage return
context = ''
for i in docs:
    context += i.page_content
contesto = context.replace('\n\n','')


#create the prompt template
template = f"""Answer the question based only on the following context:

[context]
{contesto}
[end of context]

Question: {query}

"""
#structure the prompt into a chat template

messages=[{"role": "user", "content": template}]
output = qwen05b.create_chat_completion(
            messages=messages
            )

print(f"Question: {query}")
print(output["choices"][0]["message"]["content"])
     