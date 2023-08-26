from pymongo import MongoClient
from flask import Flask,request,jsonify
from flask import  render_template
from datetime import datetime


def getDb(client,dbName):
    if dbName is None:
       return client.get_database("VPS")
    return client.get_database(dbName)

def emptyCheck(arr):
    print("checking empty Values",arr)
    for elem in  arr.values():
        if elem == "" or elem is None :
            print("Empty value Found",elem)
            return True
    return  False
def getGdName(dbName):
    if dbName == "VPS2":
        return "SINGRI"
    elif dbName == "VPS3":
        return "Gorden 3"
    else:
        return "CAR SHED"
def getAllItemsFromDB(db):
    db.stock.create_index("uid")
    db.itemDelivery.create_index("uid")
    return db.stock.find().sort("item",1);
def saveItemTodb(db,obj):
    return db.stock.insert_one(obj);
def saveDeliveryEntryToDb(db, obj):
    return db.itemDelivery.insert_one(obj);
def getAllDeliveriesForItem(db,item):
    return db.itemDelivery.find({"uid":item},{"_id":0}).sort("date",-1);
def updateDecQty(db,item,qty):
    item =int(item)
    return db.stock.update_one({"uid": item}, {"$inc":{"qty":qty}});
def findAndModSeq(db):
    res=  db.sequence.find_one_and_update({},{"$inc":{"seq":1}});
    return res['seq']
def updateItem(db,uid,item, itemDisc):
     uid =int(uid)
     return db.stock.update_one({"uid": uid}, {"$set":{"item":item,"itemDescription":itemDisc}});

client = MongoClient("mongodb+srv://vps:vps123@cluster0.tpkcrim.mongodb.net/?retryWrites=true&w=majority",
                     maxPoolSize=20)

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)


@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

@app.route('/favicon.ico')
def favicon():
    return jsonify({"success": "NULL."}), 204

@app.route('/')
@app.route('/<dbName>')
def hello_world(dbName='VPS'):
    db = getDb(client,dbName)
    return render_template('template.html',items=getAllItemsFromDB(db),selectedItem="",itemDeliveries =[],dbL= dbName, gd =getGdName(dbName))


@app.route('/saveItem', methods=['PUT'])
@app.route('/saveItem/<dbName>', methods=['PUT'])
def save_item(dbName):
      try:
        data = request.get_json()  # Get the JSON data from the request
        if emptyCheck(data):
            return  jsonify({"error": "Empty fields."}), 500
        db = getDb(client, dbName)
        data['uid'] = findAndModSeq(db)
        saveItemTodb(db,data)
        print("Item Saved Successfully")
        return jsonify({"success": "Successfully Inserted."}), 200
      except Exception as e:
          print("Exception occured while saving Item",e)
          return jsonify({"error": "An error occurred. Please try again later."}), 500

@app.route('/saveDeliveryEntry/<dbName>', methods=['PUT'])
@app.route('/saveDeliveryEntry', methods=['PUT'])
def save_deliveryEntry(dbName):
      try:
        data = request.get_json()  # Get the JSON data from the request
        if emptyCheck(data):
            return  jsonify({"error": "Empty fields."}), 500
        db = getDb(client,dbName)
        saveDeliveryEntryToDb(db,data)
        print(data)
        updateDecQty(db,data['uid'],int(data['qty'])*-1)
        return jsonify({"success": "Successfully Inserted."}), 200
        print("Delivery Entry Saved Successfully")
      except Exception as e:
          print("Exception occured while saving Delivery Entry", e)
          return jsonify({"error": "An error occurred. Please try again later."}), 500

@app.route('/getDeliveryEntries/<dbName>/<item>')
def get_itemDeliveries(dbName,item):
    db = getDb(client,dbName)
    return jsonify({"item":item,"itemDeliveries":list(getAllDeliveriesForItem(db,item))}), 200

@app.route('/editStockQty/<dbName>', methods=['PUT'])
@app.route('/editStockQty', methods=['PUT'])
def edit_stock_qty(dbName):
      try:
        data = request.get_json() # Get the JSON data from the request)
        if emptyCheck(data):
            return  jsonify({"error": "Empty fields."}), 500
        db = getDb(client,dbName)
        updateDecQty(db,data['uid'],int(data['qty']))
        reqObj = {}
        reqObj['uid'] = str(data['uid'])
        reqObj['qty'] = abs(int(data['qty']))
        reqObj['date'] = data['date']
        if(int(data['qty'])>0):
            reqObj['stockLoaded'] = 'stockLoaded'
            reqObj['deliveredTo'] = 'IN'
            reqObj['deliveredBy'] = '_'
        else:
            reqObj['deliveredTo'] = 'Cash'
            reqObj['deliveredBy'] = '_'
        saveDeliveryEntryToDb(db,reqObj)
        return jsonify({"success": "Successfully Updated Quantity."}), 200
      except Exception as e:
          print("Exception occured while Editing Qty", e)
          return jsonify({"error": "An error occurred. Please try again later."}), 500

@app.route('/editItem/<dbName>', methods=['PUT'])
@app.route('/editItem', methods=['PUT'])
def edit_item(dbName):
    try:
        data = request.get_json()  # Get the JSON data from the request)
        if emptyCheck(data):
            return  jsonify({"error": "Empty fields."}), 500
        db = getDb(client,dbName)
        updateItem(db, data['uid'], data['item'],data['itemDisc'])
        print("Edited Item Successfully")
        return jsonify({"success": "Successfully Updated Quantity."}), 200
    except Exception as e:
        print("Exception occured while Editing Item", e)
        return jsonify({"error": "An error occurred. Please try again later."}), 500





