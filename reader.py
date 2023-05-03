import PyPDF2
import csv
import os
import pandas as pd
import json
from langchain.document_loaders import TextLoader

def csv_to_txt(csv_file, db_path):
    csv_filename = os.path.splitext(csv_file.name)[0]
    txt_filename = csv_filename + '.txt'
    csv_path = os.path.join(db_path, csv_file.name)
    txt_path = os.path.join(db_path, txt_filename) 
    with open(csv_path, 'wb') as f:
        f.write(csv_file.read())
    with open(csv_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        with open(txt_path, 'w') as txtfile:
            for row in csvreader:
                txtfile.write('\t'.join(row) + '\n')
    loader = TextLoader(txt_path)
    documents = loader.load()
    return documents

def pdf_to_txt(pdf_file, db_path):
    pdf_filename = os.path.splitext(pdf_file)[0]
    txt_filename = pdf_filename + '.txt'
    txt_path = os.path.join(db_path, txt_filename)
    with open(pdf_file, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        with open(txt_path, 'w') as txt_file:
            for page_num in range(pdf_reader.numPages):
                currPage = pdf_reader.getPage(page_num)
                page_content = currPage.extractText()
                txt_file.write(page_content)
    loader = TextLoader(txt_path)
    documents = loader.load()
    return documents

def excel_to_txt(excel_file, db_path):
    excel_filename = os.path.splitext(excel_file)[0]
    txt_filename = excel_filename + '.txt'
    excel_path = os.path.join(db_path, excel_file)
    txt_path = os.path.join(db_path, txt_filename)
    df = pd.read_excel(excel_path)
    values = df.values.tolist()
    text = '\n'.join([str(row) for row in values])
    with open(txt_path, 'w') as f:
        f.write(text)
    loader = TextLoader(txt_path)
    documents = loader.load()
    return documents

def json_to_txt(json_file, db_path):
    json_filename = os.path.splitext(json_file.name)[0]
    txt_filename = json_filename + '.txt'
    json_path = os.path.join(db_path, json_file.name)
    txt_path = os.path.join(db_path, txt_filename)
    with open(json_path, 'r') as f:
        data = json.load(f)
    with open(txt_path, 'w') as f:
        for item in data:
            text = item['text']
            f.write(text + '\n')
    loader = TextLoader(txt_path)
    documents = loader.load()
    return documents