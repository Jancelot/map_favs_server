#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import request
from flask import make_response
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Response
import json

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

        
# !!!!!
# Model class
# !!!!!
class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(30), unique=False)
	address = db.Column(db.String(250), unique=False)
	lat = db.Column(db.Float, unique=False)
	lng = db.Column(db.Float, unique=False)
	
	def __init__(self, nickname, address, lat, lng):
		self.nickname = nickname
		self.address = address
		self.lat = lat
		self.lng = lng
		
	def __repr__(self):
		return '<Location %r>' % self.nickname

	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'        : self.id,
			'nickname'	: self.nickname,
			'address'	: self.address,
			'lat'		: self.lat,
			'lng'		: self.lng,
		}
       
               
#
# 404 error handler
#
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

#
# GET - read all locations
#
#return jsonify( { 'locations': locations } )
@app.route('/ubertest/api/v1.0/locations', methods = ['GET'])
def get_locations():
	locsresult = Location.query.all()
	locations = [i.serialize for i in locsresult]
	return Response(json.dumps(locations),  mimetype='application/json')

#
# GET - read location specified by id
#
@app.route('/ubertest/api/v1.0/locations/<int:location_id>', methods = ['GET'])
def get_location(location_id):
	locresult = Location.query.get(location_id)  
	if locresult is None:
		abort(404)
	location = [locresult.serialize]
	return Response(json.dumps(location),  mimetype='application/json')

#
# POST - create location
#        
@app.route('/ubertest/api/v1.0/locations', methods = ['POST'])
def create_location():
	if not request.json:
		abort(400)
	if not 'address' in request.json or type(request.json['address']) != unicode:
		abort(400)
	if not 'nickname' in request.json or type(request.json['nickname']) is not unicode:
		abort(400)
	if not 'lat' in request.json or type(request.json['lat']) is not float:
		abort(400)
	if not 'lng' in request.json or type(request.json['lng']) is not float:
		abort(400)	
	loc = Location(request.json['nickname'], request.json['address'], request.json['lat'], request.json['lng'])
	db.session.add(loc)
	db.session.commit()
	return Response(json.dumps(loc.serialize),  mimetype='application/json')

#
# PUT - update location
#   
@app.route('/ubertest/api/v1.0/locations/<int:location_id>', methods = ['PUT'])
def update_location(location_id):
	locresult = Location.query.get(location_id)
	if locresult is None:
		abort(404)
	if not request.json:
		abort(400)
	if 'address' in request.json and type(request.json['address']) != unicode:
		abort(400)
	if 'nickname' in request.json and type(request.json['nickname']) is not unicode:
		abort(400)
	if 'lat' in request.json and type(request.json['lat']) is not float:
		abort(400)
	if 'lng' in request.json and type(request.json['lng']) is not float:
		abort(400)
	print request.json.get('address')
	locresult.nickname = request.json.get('nickname', locresult.nickname)
	locresult.address = request.json.get('address', locresult.address)
	locresult.lat = request.json.get('lat', locresult.lat)
	locresult.lng = request.json.get('lng', locresult.lng)
	db.session.commit()
	return Response(json.dumps(locresult.serialize),  mimetype='application/json')

#
# DELETE - delete location
#
@app.route('/ubertest/api/v1.0/locations/<int:location_id>', methods = ['DELETE'])
def delete_location(location_id):
	locresult = Location.query.get(location_id)
	if locresult is None:
		abort(404)
	db.session.delete(locresult)
	db.session.commit()    
	return jsonify( { 'result': True } )


#
# modify response headers
#
@app.after_request
def after_request(data):
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,Authorization,Accept,Origin,Content-Type'
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response


#
# run the application
# 
if __name__ == '__main__':
    app.run(debug = True)
