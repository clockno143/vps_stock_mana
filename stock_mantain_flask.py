from pymongo import MongoClient
from flask import Flask,request,jsonify
from flask import  render_template
from datetime import datetime

def establishMongoConnectionAndgetDb():
    client = MongoClient("mongodb+srv://vps:vps123@cluster0.tpkcrim.mongodb.net/?retryWrites=true&w=majority")
    db = client.get_database('VPS')
    return  db
def emptyCheck(arr):
    for elem in  arr.values():
        if elem == "" or elem is None :
            return True
    return  False

def getAllItemsFromDB(db):
    return db.stock.find().sort("item",1);
def saveItemTodb(db,obj):
    return db.stock.insert_one(obj);
def saveDeliveryEntryToDb(db, obj):
    return db.itemDelivery.insert_one(obj);
def getAllDeliveriesForItem(db,item):
    return db.itemDelivery.find({"uid":item},{"_id":0});
def updateDecQty(db,item,qty):
    item =int(item)
    return db.stock.update_one({"uid": item}, {"$inc":{"qty":qty}});
def findAndModSeq(db):
    res=  db.sequence.find_one_and_update({},{"$inc":{"seq":1}});
    return res['seq']
def updateItem(db,uid,item, itemDisc):
     uid =int(uid)
     return db.stock.update_one({"uid": uid}, {"$set":{"item":item,"itemDescription":itemDisc}});

db = establishMongoConnectionAndgetDb()
records = db.stock
print(records.count_documents({}))

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)



@app.route('/')
def hello_world():
    return render_template('template.html',items=getAllItemsFromDB(db),selectedItem="",itemDeliveries =[])

@app.route('/saveItem', methods=['PUT'])
def save_item():
      try:
        data = request.get_json()  # Get the JSON data from the request
        if emptyCheck(data):
            return  jsonify({"error": "Empty fields."}), 500
        data['uid'] = findAndModSeq(db)
        saveItemTodb(db,data)
        return jsonify({"success": "Successfully Inserted."}), 200
      except Exception as e:
          return jsonify({"error": "An error occurred. Please try again later."}), 500

@app.route('/saveDeliveryEntry', methods=['PUT'])
def save_deliveryEntry():
      try:
        data = request.get_json()  # Get the JSON data from the request
        if emptyCheck(data):
            return  jsonify({"error": "Empty fields."}), 500
        saveDeliveryEntryToDb(db,data)
        print(data)
        updateDecQty(db,data['uid'],int(data['qty'])*-1)
        return jsonify({"success": "Successfully Inserted."}), 200
      except Exception as e:
          return jsonify({"error": "An error occurred. Please try again later."}), 500

@app.route('/getDeliveryEntries/<item>')
def get_itemDeliveries(item):
    print(list(getAllDeliveriesForItem(db,item)))
    return jsonify({"item":item,"itemDeliveries":list(getAllDeliveriesForItem(db,item))}), 200

@app.route('/editStockQty', methods=['PUT'])
def edit_stock_qty():
      try:
        data = request.get_json() # Get the JSON data from the request)
        if emptyCheck(data):
            return  jsonify({"error": "Empty fields."}), 500
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
          return jsonify({"error": "An error occurred. Please try again later."}), 500


@app.route('/editItem', methods=['PUT'])
def edit_item():
    try:
        data = request.get_json()  # Get the JSON data from the request)
        if emptyCheck(data):
            return  jsonify({"error": "Empty fields."}), 500
        updateItem(db, data['uid'], data['item'],data['itemDisc'])
        return jsonify({"success": "Successfully Updated Quantity."}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred. Please try again later."}), 500





