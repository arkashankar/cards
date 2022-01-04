# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 15:26:18 2020

@author: isev113
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from flask import Flask,render_template,url_for,request
import pandas as pd 
import pickle
import ijson
import pandas as pd
from fuzzywuzzy import process
import re
from werkzeug import secure_filename
import os
import json
dictionary = {}
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
app = Flask(__name__)

#@app.route('/')
#def home():
    #return render_template('home.html')
#app.config["IMAGE_UPLOADS"]=(r"D:\NUS_code\cards")
@app.route('/predict',methods=['POST', "GET"])
def predict():

    df = pd.read_json(r'D:\NUS_code\cards\cards.json', lines= True)
    df2 = pd.DataFrame(df, columns=['emails','addresses','phoneNumbers','company', 'title', 'name'])
    list_email =[]
    for i in range(len(df['emails'])):
        list_email.append(df['emails'][i])
    list_email_list = []
    for i in list_email:
        if i == []:
            i= ''
        else:
            list_email_list.append(i[0])
    df_emails = pd.DataFrame(list_email_list)
    df_emails.columns = ['data']
    list_addresses =[]
    for i in range(len(df['addresses'])):
        list_addresses.append(df['addresses'][i])
    list_addresses_list = []
    for i in list_addresses:
        if i == []:
            i= ''
        else:
            list_addresses_list.append(i[0])
    df_addresses = pd.DataFrame(list_addresses_list)
    df_addresses.columns = ['data']
    df_phoneNumbers = pd.DataFrame(df, columns = ['phoneNumbers'])
    df_phoneNumbers.columns = ['data']
    df_company = pd.DataFrame(df, columns=['company'])
    df_company.columns = ['data']
    df_title = pd.DataFrame(df, columns=['title'])
    df_title.columns = ['data']
    df_name = pd.DataFrame(df, columns=['name'])
    df_name.columns = ['data']
    frames = [df_company,df_title,df_name,df_phoneNumbers,df_addresses ]
    df_labeled = pd.concat(frames, ignore_index =True)
    df_labeled['data'].replace('', np.nan, inplace=True)
    df_labeled.dropna(subset=['data'], inplace=True)
    X = np.array((df_labeled['data']).values)
    X_LIST=list(X)
    read=''
    email=[]
    if request.method == 'POST':
        file =request.files['imagefile']
        filename = secure_filename(file.filename) # save file 
        filepath = os.path.join(app.config['IMAGE_UPLOADS'], filename);
        file.save(filepath)
        image = cv2.imread(filepath)
        text = pytesseract.image_to_string(image)
        read= (text.splitlines())
        text = text.strip()
        read = text.splitlines()
        text=text.replace("\n ","")
        text= ("".join([s for s in text.strip().splitlines(True) if s.strip("\r\n").strip()]))
        read = text.splitlines()
        for i in range (len(read)):
            if read[i] == '':
                read.pop(i)
    def get_matches(query, choices, limit=10):
        results = process.extract(query, choices,limit=limit)
        return results
    def extract_email_addresses(string):
        r = re.compile(r'[\w\.-]+@[\w\.-]+')
        return r.findall(string)
    match_list=[]
    List_new = ['Andrew lim', '89889887878', 'NUS']
    for i in range(len(List_new)):
        email=extract_email_addresses(List_new[i])
        email=",".join(email)
        for i in List_new:
            if i == email:
                List_new.remove(i)
    for i in List_new:
        match_list.append(get_matches(i, X_LIST))
    check_list =[]
    for i in range(len(match_list)):
        check_list.append(match_list[i][0][0])
    df_address=df2['addresses'].apply(', '.join)
    def column_name(value):
        for i in df_address:
            if i == (value):
                return 'Address'
                break
        for i in df2['phoneNumbers']:
            if i == value:
                return 'PhoneNumber'
                break
        for i in df2['company']:
            if i == value:
                return 'company'
                break
        for i in df2['title']:
            if i == value:
                return 'title'
                break
        for i in df2['name']:
            if i == value:
                return 'name'
                break
    field_name = []
    for i in check_list:
        field_name.append(column_name(i))
    def listToString(s):   
        str1 = ""    
        for ele in s:  
            str1 += ele      
        return str1
    email_str = listToString(email)
    
    field_dic = {}
    field_dic= dict(zip(List_new,field_name))
    if email != []:
        field_dic[email_str] = 'email'
    field_dic
    Table = []
    for key, value in field_dic.items():    # or .items() in Python 3
        temp = []
        temp.extend([key,value])  #Note that this will change depending on the structure of your dictionary
        Table.append(temp)
    
   
   
    return  render_template('result.html',prediction=Table)


@app.route('/save',methods=['POST'])
def save():
    data = request.json
    return jsonify(data)

    
if __name__ == '__main__':
    app.run(debug= True, use_reloader=False)
    