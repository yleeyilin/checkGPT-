import os
import reader
from apikey import apikey
from openai.error import OpenAIError
import streamlit as st
from langchain import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.utilities import WikipediaAPIWrapper 
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from redundancy.toolkit import tools, memory, fixed_prompt
from langchain.agents import initialize_agent
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.agents import create_csv_agent


documents = None
uploaded_file = None
docs = None

try:
    # Make available to api server 
    os.environ['OPENAI_API_KEY'] = apikey

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
        template='Write a short exerpt on {topic}'
    ) 
    # conversation_template = PromptTemplate(
    #     input_variables = ['Data', 'ToDo'], 
    #     template='Do a search and plot a line graph on {ToDo}, referencing {Data}'
    # )

    # Create instance of LLM
    llm = OpenAI()
    if documents: 
        chain = load_qa_chain(llm, chain_type="stuff")
        embeddings = OpenAIEmbeddings()
        text_splitter = CharacterTextSplitter(        
            separator = "\n",
            chunk_size = 1000,
            chunk_overlap  = 0,
        )
        splitDocs = text_splitter.split_documents(documents)
        db = FAISS.from_documents(splitDocs, embeddings)
        docs = db.similarity_search(todo)
    topic_chain = LLMChain(llm=llm, prompt=topic_template, verbose=True, output_key='topic')
    # conversation_chain = LLMChain(llm=llm, prompt=conversation_template, output_key='query')
    wiki = WikipediaAPIWrapper()

    conversational_agent = initialize_agent(
        agent="zero-shot-react-description",
        tools=tools,
        llm=llm,
        max_iterations=3,
        memory=memory
    )

# Response (Including Error Handling)
except OpenAIError as error:
    st.write('No output...Write down what you want me to do!')

if data:
    topic = topic_chain.run(data)
    wiki_research = wiki.run(data)  
    st.write(topic)
    with st.expander('Research'): 
        st.info(wiki_research)
if docs and todo:
    fileCheck = chain.run(input_documents=docs, question=todo)
    st.write(fileCheck)
    tools = conversational_agent.run(todo)
    if isinstance(tools, dict):
        st.write(tools)
    elif isinstance(tools, bytes):
        st.image(tools, use_column_width=True)