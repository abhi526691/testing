
from crypt import methods
import hashlib
from io import BufferedReader
import logging
from re import L
from flask import Flask, Response, redirect, request, jsonify, render_template,make_response
import os
import time
from numpy import single
# import azure.cognitiveservices.speech as speechsdk
import requests, uuid, json
import requests
from flask_pymongo import PyMongo
import certifi
from flask_restful import Resource, Api
from pymongo import MongoClient
ca = certifi.where()
import operator

app = Flask(__name__)
api = Api(app)


mongodb_client = MongoClient(
    'mongodb+srv://fraudcop:fraudcop@fraudcop.bynmf.mongodb.net/test_data?retryWrites=true&w=majority', tlsCAFile=certifi.where())

db = mongodb_client.test_data

@app.route("/", methods=['POST', 'GET'])
def index():
    return Response("Home Page")

@app.route("/add_contact", methods=["POST"])
def add_contact():
    if request.method == 'POST':
        ## Taking input from User
        contact_list = request.form['contact_list']
        contact_list = json.loads(contact_list)
        imei = contact_list['imei']
        unique_id = contact_list['unique_id']
        contactCnt = contact_list['count']
        contact_only = contact_list['contacts']
        ## Checking if imei is passed along with input data
        if imei != "None":
            if db["imeiNumber"].find_one({"imei": imei}):
                if contactCnt <= 0:
                    return "Already in the database"
            else:
                ## if IMEI is not in the database
                ## Insert it as new IMEI number along with count of the contacts
                db.imeiNumber.insert_one(
                    {"unique_id": unique_id , "imei": imei, "count" : contactCnt})
        else:
            if db["imeiNumber"].find_one({"unique_id": unique_id}):
                if contactCnt <= 0:
                    return "Already in the database"
            else:
                ## if Unique id is not in the database
                ## Insert it as new Unique id number along with count of the contacts
                db.imeiNumber.insert_one(
                    {"unique_id": contact_list['unique_id'], "imei": imei, "count" : contactCnt})
        ## Looping over all the contact to save in the database
        for i in contact_only:
            for k, v in i.items():
                hash_pass = hashlib.md5(k.encode("utf-8")).hexdigest()  ## Converting the mobile number in hashcode
                single_contact = db['contact_list'].find_one({"number": hash_pass}) ## Checking if the number is already registered in the database
                ## If the number is already in the database
                if single_contact:
                    nameList = single_contact.get('name')   ## Fetching the list of name of the number found in the database
                    newNameList = {}
                    pointer = 0
                    for key1, value1 in nameList.items():
                        ## Check whether the new Name is already in the name list
                        ## If name is already there increase the count of that name
                        ## if name is not there store it as it is with count 0
                        ## Increase the pointer varaible
                        if key1 == v:
                            value1 = int(value1) + 1
                            newNameList.update({key1:value1})
                            pointer = 1
                        else:
                            newNameList.update({key1:value1})
                    ## depend on the pointer value add the name as a new Name in the database
                    if pointer == 0:
                        newNameList.update({v:0})
                    ## Fetching the data of the input number from database
                    ## and Updating the new Name list in the database
                    filter = { 'number': single_contact.get('number') }
                    newvalues = { "$set": { 'name': newNameList } }
                    db['contact_list'].update_one(filter, newvalues)
                ## If number is not in the database then
                else:
                    ## Add the number and name in the database along with it's unique id or IMEI number
                    db.contact_list.insert_one(
                        {"number": hash_pass, "name": {v:0}, 'imei': imei, 'unique_id': unique_id})
        return Response("success")
@app.route("/fetch_name", methods=['POST'])
def fetch_name():
    ## Taking input number from database
    number = request.form['number']
    ## Converted it into hashcode
    hash_pass = hashlib.md5(number.encode("utf-8")).hexdigest()
    ## checking if number is already in the database
    single_contact = db['contact_list'].find_one({"number": hash_pass})
    if single_contact:
        name = ""
        for key, value in single_contact.items():
            if key == "number":
                nameList = single_contact['name']
                #### Returning the name with highest repetition
                ### if each name has same count return the name which came first
                name = max(nameList.items(), key=operator.itemgetter(1))[0]
        return Response(name)
    ## else return Unkown person as output since the number is not in the database
    else:
        return Response("Unknown Person")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")







