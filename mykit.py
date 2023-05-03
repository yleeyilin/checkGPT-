import requests
import string
import io
from googlesearch import search
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

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

def searchWeb(file):
    df = pd.read_csv(file)
    category_cols = [col for col in df.columns if df[col].dtype == 'object']
    category_info = {}
    for col in category_cols:
        results = thisQuery(f'{col} finance')
        if results:
            category_info[col] = results
    return category_info

#data visualisation 
def makeLineGraph(file):
    df = pd.read_csv(file)
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