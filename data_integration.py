# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 00:36:11 2021
Last Updated on Sun 12 00:40:15 2021

@author: Vaibhav
"""
import os
import pandas as pd
import datetime
from pprint import pprint
import pymongo


def read_file(path_to_file,file):
    """Reading the Data file from the folder here we are trying to read both the file csv as well as excel"""
    if file=='':
        for file_name in os.listdir():
            if file_name.endswith(".csv"):
                data_file=pd.read_csv(path_to_file+'\\'+file_name)
            elif file_name.endswith(".xlsx"):
                data_file=pd.read_excel(path_to_file+'\\'+file_name)
            else:
                print('No File Found')
                data_file=pd.DataFrame()
    else:
        if file.endswith(".csv"):
            data_file=pd.read_csv(path_to_file+'\\'+file)
        elif file.endswith(".xlsx"):
            data_file=pd.read_excel(path_to_file+'\\'+file)
        else:
            print('No File Found')
            data_file=pd.DataFrame()
    return data_file



def connect_mongo_db(username,password,database):
    """Connecting atlas mongodb with python """ 
    client = pymongo.MongoClient("mongodb+srv://"+username+":"+password+"@cluster0.utt9p.mongodb.net/po_data?retryWrites=true&w=majority")
    db = client[database]
    return db



def convert_data_type(dataframe,col_dictionary):
    """This function willl convert the data type into "int","Str","Datetime64" Validating the Datatype"""
    for key in col_dictionary:
        col=key
        dtype=col_dictionary[key]
        if dtype=='int':
            dataframe[col]=pd.to_numeric(dataframe[col], errors='coerce')
        elif dtype=='str':
            dataframe[col]=dataframe[col].astype(dtype)
        elif dtype=='datetime64[ns]':
            dataframe[col]=pd.to_datetime(dataframe[col], errors='coerce')
            dataframe[col]=dataframe[col].apply(lambda x: x.strftime('%d-%m-%Y'))
    dataframe=dataframe.dropna()
    return dataframe



def write_to_db(dataframe,db_access,collection_name):    
    """Creating a collection"""
    supp_po_no=list(dataframe['Supplier PO number'])
    supp_po_order=list((dataframe['Supplier PO Order date']))
    po_status=list((dataframe['Supplier PO status']))
    po_fulfilled_date=list((dataframe['Supplier PO Fulfilled Date']))
    po_original_delivery=list((dataframe['Supplier PO original Delivery Date:']))
    po_tracking=list(dataframe['Supplier PO tracking number:'])
    expected_delay=list(dataframe['Expected Delay:'])
    db_access[collection_name].remove({})
    
    for x in range(0, len(dataframe)):
        shipping_details = {
            'Supplier_PO_number':supp_po_no[x], 
            'Supplier_PO_Order_date':supp_po_order[x], 
            'Supplier_PO_status':po_status[x],
           'Supplier_PO_Fulfilled_Date':po_fulfilled_date[x], 
           'Supplier_PO_original_Delivery_Date':po_original_delivery[x],
           'Supplier_PO_tracking_number':po_tracking[x], 
           'Expected_Delay':expected_delay[x]
        }
        
        result=db_access[collection_name].insert_one(shipping_details)
        
        print('Created {0} of {1} as {2}'.format(x,len(dataframe),result.inserted_id))
   
    print('finished creating '+str(len(dataframe))+' shipping scenario')
    return True


def get_sap_data(db,collection_name,column_name):
    """Retrieving only one column"""
    mycol = db[collection_name]
    sap_result=[]
    for x in mycol.find({}, {"_id":0, column_name: 1}):
        print(x)
        sap_result.append(x)
    return sap_result


def get_sap_data2(db,collection_name):
    """Retrieving the overall collection"""
    mycol = db[collection_name]
    sap_result=[]
    for x in mycol.find({}, {"_id":0 }):
        print(x)
        sap_result.append(x)
    return sap_result



def get_expected_deliver_date(db,collection_name,po_number):
    """Fetching the Expected Delivery Date"""
    mycol = db[collection_name]
    for x in mycol.find({"Supplier_PO_number":po_number}):
        print(x)
        expected_delivery=x['Supplier_PO_original_Delivery_Date']
    return expected_delivery



def calculate_expected_delay(db,collection_name,expected_delivery,po_number):
    """Calculating the Expected_delay by Subtracting the Delivery and fullfilled column"""
    mycol = db[collection_name]
    for x in mycol.find({"Supplier_PO_number":po_number}):
        print(x)
        print("Orginal Expexted_delay",str(x['Expected_Delay']))
        fulfilled_date=x['Supplier_PO_Fulfilled_Date']
        ###caluatiing the expected delay in date using different beween dates
        mdate1 = datetime.datetime.strptime(fulfilled_date, "%d-%m-%Y").date()
        rdate1 = datetime.datetime.strptime(expected_delivery, "%d-%m-%Y").date()
        #calculating the difference between two dates
        expected_delay=(mdate1 - rdate1).days
        print("Expexted_delay in dates",str(expected_delay))
        doc_id=x['_id']
        myquery = { "_id": doc_id}
        newvalues = { "$set": { "Expected_Delay": expected_delay } }
        mycol.update_one(myquery, newvalues)
        expected_delay=0
    return expected_delay

"""Step1=Reading the file"""
data_file=read_file(r'C:\Users\vaibhavm\Downloads\data_integration','Book.xlsx')

"""Step2=Connecting with mongodb """
db_access=connect_mongo_db('dbUser','dbUser','po_data')

"""Ste3#=Cleaning the file by dropping the Null values"""
data_file=data_file.dropna()

"""Step4=Fetching the datatype of each and every column"""
dtype_values=dict({'Supplier PO number': 'int', 'Supplier PO Order date': 'datetime64[ns]',
                   'Supplier PO status': 'str', 'Supplier PO Fulfilled Date': 'datetime64[ns]',
                   'Supplier PO original Delivery Date:': 'datetime64[ns]',
                   'Supplier PO tracking number:': 'int', 'Expected Delay:': 'int'})

"""Step5=Validating the data type using convert_data_type Function """
data_file=convert_data_type(data_file,dtype_values)

"""Appending the Cleaned and validated data into the collection named Test data"""
COLLECTION_NAME='test_data'
check_write_status=write_to_db(data_file,db_access,COLLECTION_NAME)

result_set=get_sap_data(db_access,COLLECTION_NAME,"Supplier_PO_number")
pprint(result_set)
result_set=get_sap_data2(db_access,COLLECTION_NAME)
pprint(result_set)

"""Step6=Fetching the Expected Delivery by using get_expected_deliver_date" Function"""
expected_delivery=get_expected_deliver_date(db_access,COLLECTION_NAME,114)
print(expected_delivery)
                        
"""Step7=Final Task Calculating the Expected_delay"""
expected_delay_calculated=calculate_expected_delay(db_access,COLLECTION_NAME,expected_delivery,114)
print(expected_delay_calculated)

"""Generating the cleaned Data file"""
data_file.to_excel(r'C:\Users\vaibhavm\Downloads\data_integration\Cleaned_file.xlsx',index=True)
