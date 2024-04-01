import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    st.title('Ask me relevant questions from your PDF!')

    # Uploading PDF file
    pdf_path = os.path.join("data", "Prediction of fraudulent cryptocurrency transactions using logistic regression.pdf")
    
    # Reading the file
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    # Splitting the text
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Encoding the chunks
    # Pass the OpenAI API key from environment variable
    openai_api_key = os.getenv('OPENAI_API_KEY')
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    doc_to_search_from = FAISS.from_texts(chunks, embeddings)

    # Taking query from user
    query = st.text_input("Enter Your question here")
    if query:
        rel_docs = doc_to_search_from.similarity_search(query)
        llm = OpenAI()
        chain = load_qa_chain(llm, chain_type="stuff")
        result = chain.run(input_documents=rel_docs, question=query)

        # Display answer and additional analysis
        st.subheader("Answer:")
        if isinstance(result, dict) and 'answer' in result:
            st.write(result['answer'])
        else:
            st.write("No answer found.")

        # Provide context or insights related to the answer
        st.subheader("Analysis:")
        st.write("Here are some insights related to the answer:")
        # You can add your analysis here based on the result

if __name__ == '__main__':
    main()
