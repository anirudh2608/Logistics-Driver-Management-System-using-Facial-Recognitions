from sqlalchemy.sql.expression import null
from . import db
from flask_login import UserMixin
from datetime import datetime

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerId = db.Column(db.Integer,db.ForeignKey('customer.id')) 
    details = db.Column(db.String(500))
    truckNumber = db.Column(db.Integer,db.ForeignKey('truck.id'))
    status = db.Column(db.String(50),default="Pending")
    origin = db.Column(db.String(50))
    finalStation = db.Column(db.String(50))
    checkPoint = db.Column(db.Integer,db.ForeignKey('checkpoint.id'))
    driverId = db.Column(db.Integer,db.ForeignKey('driver.id'))
    dateOfOrder = db.Column(db.DateTime(timezone=True), default=datetime.now())
    dateDelivered = db.Column(db.DateTime(timezone=True))    

class Customer(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    address = db.Column(db.String(1000))
    contact = db.Column(db.BigInteger)
    order = db.relationship('Order')
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class Admin(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    identity = db.Column(db.BLOB)
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class Driver(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    address = db.Column(db.String(1000))
    contact = db.Column(db.BigInteger)
    license = db.Column(db.String(30))
    truckNumber = db.Column(db.Integer,db.ForeignKey('truck.id'))
    identity = db.Column(db.BLOB)
    checkpoint = db.Column(db.Integer,db.ForeignKey('checkpoint.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
    status = db.Column(db.Integer) #0 -> Pending 1-> Active 2-> Rejected
    order = db.relationship('Order')

class Truck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    truckNumber = db.Column(db.String(30))
    checkpoint = db.Column(db.Integer,db.ForeignKey('checkpoint.id'))
    driver = db.relationship('Driver')
    order = db.relationship('Order')

class Checkpoint(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    location = db.Column(db.String(50),unique=True) 
    order = db.relationship('Order')
    driver = db.relationship('Driver')
    truck = db.relationship('Truck')

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    customer = db.relationship('Customer')
    driver = db.relationship('Driver')
    Admin = db.relationship('Admin')




