from flask import Flask
from flask import request
from flask import json
from flask import Response
from flask import send_file
import qrcode
import random
import string
import json
from io import StringIO
from io import BytesIO
from sqlitedict import SqliteDict


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route("/api/bookmarks", methods=['POST'])
def handle_request_params():
    if request.method=='POST':
        data = request.get_json()
        name = data['name']
        url = data['url']
        description = data['description']
        etag_dict={"etag":0}
        data.update(etag_dict)
        exist=False
        with SqliteDict('./dbbookmark.sqlite', autocommit=True) as mydict: 
            for key, value in mydict.iteritems():
                if value['url']==url:
                    exist=True
                    break
            if exist :
                return Response('{"reason" : "The given URL already existed in the system."}',status="400 Bad Request", mimetype='application/json')
            else :
                if mydict:
                    id_old=list(mydict.keys())[-1]
                    id_old_digitpart=id_old[3:]
                    id_old_digitpart=int(id_old_digitpart)+1
                    id_new=''.join(random.choices(string.ascii_lowercase, k=3))+str(id_old_digitpart)
                else :
                    id_new=''.join(random.choices(string.ascii_lowercase, k=3))+"111"
                mydict[id_new] = data
                return Response('{"id":"'f'{id_new}''"}',status="201 Created", mimetype='application/json')


@app.route("/api/bookmarks/<id>", methods=['GET','DELETE'])
def get_bookmark_details(id):
        with SqliteDict('./dbbookmark.sqlite', autocommit=True) as mydict: 
            if id in mydict: 
                if request.method=='GET':
                    old_etag=mydict[id]["etag"]
                    new_etag=old_etag+1
                    bookmark_details=mydict[id]
                    bookmark_details["etag"]=new_etag
                    mydict[id]=bookmark_details
                    id_dict={"id":f"{id}"}
                    id_dict.update(bookmark_details)
                    del id_dict["etag"]
                    return id_dict
                elif request.method=='DELETE':
                    del mydict[id]
                    return Response("No Content", status=204, mimetype='application/json')
                else :
                    return "Unidentified method"
            else :
                return Response("Not Found", status=404, mimetype='application/json')

    
@app.route("/api/bookmarks/<id>/qrcode")
def get_qrcode(id):
    with SqliteDict('./dbbookmark.sqlite', autocommit=True) as mydict: 
            if id in mydict: 
                #old_etag=mydict[id]["etag"]
                #new_etag=old_etag+1
                bookmark_details=mydict[id]
                #bookmark_details["etag"]=new_etag
                #mydict[id]=bookmark_details
                url=bookmark_details["url"]
                app.logger.info(url)
                qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
                qr.add_data(url)
                qr.make(fit=True)
                img = qr.make_image()
                img_buf = BytesIO()
                img.save(img_buf)
                img_buf.seek(0)
                return send_file(img_buf, mimetype='image/png')
            else :
                return Response("Not Found", status=404, mimetype='application/json')


@app.route("/api/bookmarks/<id>/stats")
def get_statistics(id):
    with SqliteDict('./dbbookmark.sqlite', autocommit=True) as mydict: 
            if id in mydict: 
                etag=mydict[id]["etag"]
                request_etag=request.headers.get('ETag')
                if request_etag is None:
                    request_etag=-1
                if int(etag)==int(request_etag):
                    return Response("", status="304 Not Modified, ETag: "f"{etag}", mimetype='application/json')
                else :
                    return Response(f"{etag}", status="200 OK, ETag: "f"{etag}", mimetype='application/json')
            else :
                return Response("Not Found", status=404, mimetype='application/json')







        
    
  
  