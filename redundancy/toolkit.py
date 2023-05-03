from langchain.agents import Tool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
import requests
import string
import io
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import os

db_path = "/Users/leeyilin/Documents/checkBOT/db"

#surf the internet for relevant current data and contextualise categories 
def thisQuery(query):
    fallback = ""
    result = ''
    try:
        search_result_list = list(search(query))
        page = requests.get(search_result_list[0])
        soup = BeautifulSoup(page.content, features="lxml")
        article_text = ''
        article = soup.findAll('p')
        for element in article:
            article_text += '\n' + ''.join(element.findAll(text = True))
        article_text = article_text.replace('\n', '')
        first_sentence = article_text.split('.')
        first_sentence = first_sentence[0].split('?')[0]
        chars_without_whitespace = first_sentence.translate(
            { ord(c): None for c in string.whitespace }
        )
        if len(chars_without_whitespace) > 0:
            result = first_sentence
        else:
            result = fallback
        return result
    except Exception as e:
        print(f"An error occurred: {e}")

def searchWeb(query):
    filename = "/Users/leeyilin/Documents/checkBOT/db/FS_sp500_addstats.csv" # provide the full path of the file here
    df = pd.read_csv(filename)
    category_cols = [col for col in df.columns if df[col].dtype == 'object']
    category_info = {}
    for col in category_cols:
        results = thisQuery(f'{col} finance')
        if results:
            category_info[col] = results
    return category_info

searchTool = Tool(
        name = "search",
        func= searchWeb,
        description="Useful for when you need to answer questions about current events or when you need to understand the context clearer."
    )

#data visualisation 
def makeLineGraph(query):
    filename = "/Users/leeyilin/Documents/checkBOT/db/FS_sp500_addstats.csv" # provide the full path of the file here
    df = pd.read_csv(filename)
    category_cols = [col for col in df.columns if df[col].dtype == 'object']
    df_categories = df[category_cols].astype(str)
    plt.figure(figsize=(10,6))
    for col in df_categories.columns:
        plt.plot(df_categories[col], label=col)
    plt.legend()
    plt.title('Category Line Graph')
    plt.xlabel('X-axis label')
    plt.ylabel('Y-axis label')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    # Return PNG image as bytes
    return buffer.getvalue()

# def makeLineGraph(query):
#     for filename in os.listdir(db_path):
#         if os.path.isfile(os.path.join(db_path, filename)):
#             df = pd.read_csv(filename)
#             category_cols = [col for col in df.columns if df[col].dtype == 'object']
#             df_categories = df[category_cols]
#             plt.figure(figsize=(10,6))
#             for col in df_categories.columns:
#                 plt.plot(df_categories[col], label=col)
#             plt.legend()
#             plt.title('Category Line Graph')
#             plt.xlabel('X-axis label')
#             plt.ylabel('Y-axis label')
#             buffer = io.BytesIO()
#             plt.savefig(buffer, format='png')
#             plt.close()
#             # Return PNG image as bytes
#             return buffer.getvalue()

lineGraph_tool = Tool(
    name='LinePlot',
    func= makeLineGraph,
    description="Useful for data visualisation of all categories when a csv file is parsed in when doing data analysis"
)

tools = [searchTool, lineGraph_tool]

fixed_prompt = '''Answer the following questions as best you can. You have access to the following tools:
searchTool: useful for webscraping to gain a contextual idea of the dataset 
lineGraph_tool: useful for data analysis and to demonstrate your findings

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [searchTool, lineGraph_tool]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=3,
    return_messages=True
)