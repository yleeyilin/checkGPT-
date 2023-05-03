import os
import io
import reader
from apikey import apikey
import streamlit as st
from langchain import HuggingFaceHub, OpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.utilities import WikipediaAPIWrapper 
from langchain.document_loaders import TextLoader
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
import pandas as pd

documents = None

# Make available to api server 
os.environ['HUGGINGFACEHUB_API_TOKEN'] = apikey

# Title of APP 
st.title('checkGPT')
st.markdown("<h1 style='text-align: left; font-size:20px;'>Data insights at your fingertips</h1>", unsafe_allow_html=True)

# Create a file uploader in Streamlit
file_type = st.sidebar.selectbox('Select file type', ['CSV', 'Excel', 'PDF'])
db_path = "/Users/leeyilin/Documents/checkBOT/db"
if file_type == 'CSV':
    uploaded_file = st.file_uploader('Upload CSV file', type='csv')
    if uploaded_file is not None:
        documents = reader.csv_to_txt(uploaded_file, db_path)
elif file_type == 'Excel':
    uploaded_file = st.file_uploader('Upload Excel file', type='xlsx')
    if uploaded_file is not None:
        excel_data = uploaded_file.read()
        documents = reader.excel_to_txt(excel_data, db_path)
elif file_type == 'PDF':
    uploaded_file = st.file_uploader('Upload PDF file', type='pdf')
    if uploaded_file is not None:
        documents = reader.pdf_to_txt(uploaded_file, db_path)

# Prompt 
data = st.text_input('What is this dataset about?')
todo = st.text_input('What do you need me to do?')

#Prompt Template
topic_template = PromptTemplate(
    input_variables = ['topic'], 
    template='Summarise {topic}'
) 

# Create instance of LLM
llm=HuggingFaceHub(repo_id="google/flan-t5-xl", model_kwargs={"temperature":0, "max_length":512})
if documents: 
    print(documents)
    chain = load_qa_chain(llm, chain_type="stuff")
    embeddings = HuggingFaceEmbeddings()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    db = FAISS.from_documents(docs, embeddings)
    docs = db.similarity_search(todo)
topic_chain = LLMChain(llm=llm, prompt=topic_template, verbose=True, output_key='topic')
wiki = WikipediaAPIWrapper()

# Return a response 
if data and todo:
    topic = topic_chain.run(data)
    wiki_research = wiki.run(data) 
    if docs:
        fileCheck = chain.run(input_documents=docs, question=todo)
        st.write(fileCheck)
    with st.expander('Research'): 
        st.info(wiki_research)