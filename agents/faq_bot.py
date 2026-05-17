from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from agents.base import get_gemini
from agents.vector_store import load_store

SYSTEM_PROMPT = """You are a school information assistant for KALNET School.
You ONLY answer questions using the provided school documents below.
If the answer is not found in the documents, you MUST respond with:
"I do not have that information — please contact the school office directly."
Never make up or guess any information.

Context from school documents:
{context}

Question: {question}

Answer:"""

prompt = PromptTemplate(
    template=SYSTEM_PROMPT,
    input_variables=["context", "question"]
)

def get_faq_chain():
    llm = get_gemini()
    store = load_store()
    retriever = store.as_retriever(search_kwargs={"k": 4})
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return chain

def chat_with_bot(question: str, conversation_history: list = []):
    chain = get_faq_chain()
    result = chain.invoke({"query": question})
    answer = result["result"]
    sources = list(set([
        doc.metadata.get("source_file", "unknown")
        for doc in result["source_documents"]
    ]))
    return {"answer": answer, "sources": sources}
