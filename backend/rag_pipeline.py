from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

# Initialize the open-source embedding model (FREE & Fast)
# This will download a small model on the first run, making subsequent runs instant.
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def build_vector_store(video_a_data, video_b_data):
    """
    Takes the extracted data, chunks the transcripts, tags them with A or B, 
    and saves them into a local Chroma Vector DB.
    """
    documents = []
    
    # Helper function to process each video
    def process_transcript(video_data, video_tag):
        if video_data.get("status") == "success" and video_data.get("transcript"):
            text = video_data["transcript"]
            # Tag the chunk so the LLM knows which video it belongs to
            meta = {
                "video_tag": video_tag,
                "creator": video_data["metadata"].get("creator", "Unknown"),
                "platform": video_data["metadata"].get("platform", "Unknown")
            }
            documents.append(Document(page_content=text, metadata=meta))

    process_transcript(video_a_data, "A")
    process_transcript(video_b_data, "B")

    if not documents:
        return {"status": "error", "message": "No valid transcripts to chunk."}

    # Chunking Strategy: 
    # Using 500 characters so the LLM gets enough context, with 50 chars overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunked_docs = text_splitter.split_documents(documents)

    # Make sure database directory exists
    db_dir = "./database/chroma_db"
    os.makedirs(db_dir, exist_ok=True)

    # Initialize ChromaDB and store vectors
    vector_store = Chroma.from_documents(
        documents=chunked_docs,
        embedding=embeddings,
        persist_directory=db_dir
    )
    
    return {
        "status": "success", 
        "message": f"Vectorized {len(chunked_docs)} chunks into ChromaDB.",
        "db_path": db_dir
    }
    
def ask_question(question: str):
    """Queries the ChromaDB and uses an LLM to answer based on the context using modern LCEL."""
    try:
        # Check if API Key exists before doing anything
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            return {"status": "error", "message": "Bhai, OpenAI API Key is missing! Please add it to your .env file."}

        # Initialize LLM
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2, api_key=api_key)
        
        # Connect to the local Vector DB
        db_dir = "./database/chroma_db"
        vector_store = Chroma(persist_directory=db_dir, embedding_function=embeddings)
        
        # Retrieve top 4 most relevant chunks
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        
        # Set up the modern AI Prompt
        template = """You are an expert content analytics assistant for creators. 
        Use the following retrieved context to answer the user's question about two videos. 
        If the information is not in the context, just say you don't know based on the provided videos. 
        Always try to cite your sources (e.g., 'According to Video A...', 'Based on Video B').

        Context: {context}

        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        # Format documents so LLM knows which chunk belongs to which video
        def format_docs(docs):
            return "\n\n".join(f"[{doc.metadata.get('video_tag', 'Unknown')}] {doc.page_content}" for doc in docs)
        
        # Build the modern LCEL chain
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # 1. Invoke the chain to get the answer
        answer = rag_chain.invoke(question)
        
        # 2. Get the sources separately to display in the UI
        retrieved_docs = retriever.invoke(question)
        source_list = []
        for doc in retrieved_docs:
            source_list.append({
                "video_tag": doc.metadata.get("video_tag"),
                "creator": doc.metadata.get("creator"),
                "text_snippet": doc.page_content[:100] + "..." # First 100 chars
            })
            
        return {
            "status": "success",
            "answer": answer,
            "sources": source_list
        }
    except Exception as e:
        return {"status": "error", "message": f"Server Error: {str(e)}"}