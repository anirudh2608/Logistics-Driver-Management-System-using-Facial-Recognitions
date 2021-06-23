from flask import Blueprint, render_template, request, flash, redirect, session,g,jsonify
from flask.helpers import url_for
from .models import Customer, Order, Admin,Role,Driver,Truck,Checkpoint
from . import db
import json
from .auth import gen, getIdentity
from .helperFunc import *
from .camera import VideoCamera
from sqlalchemy.sql import func
import gc

def verifyUser(User):
    """
    Funtion to verify already authenticated user for its role
    Input - User Title (Admin,Customer,Driver)
    Function - First checks if user is authenticated, then checks that the right user is authenticated or not
                For example, user logged in as driver cannot access admin dashboard, or logged in as customer 
                cannot access the admin dashboard
    Output - If the correct user is accessing the page, return true
    """
    if g.user:
        if User == "Admin":
            if session['role'] == 1:
                return True
        elif User == "Customer":
            if session['role'] == 2:
                return True
        elif User == "Driver":
            if session['role'] == 3:
                return True

views = Blueprint('views',__name__)

@views.route('/')
@views.route('/home')
def HomePage():

    if g.user:
        if session['role'] == 2:
            flash('You need to logout to visit the home page!',category='error')
            return redirect(url_for('views.userDashboard'))
        elif session['role'] == 1:
            flash('You need to logout to visit the home page!',category='error')
            return redirect(url_for('views.adminDashboard'))
        elif session['role'] == 3:
            flash('You need to logout to visit the home page!',category='error')
            return redirect(url_for('views.driverDashboard'))
    else:
        return render_template('home.html')

@views.route('/userDashboard')
def userDashboard():
    if g.user:
        cust = Customer.query.filter_by(email=session['email']).first()
        if cust:
            return render_template('userDashboard.html',customer=cust)
        elif session['role'] == 1:
            flash("You are an admin, not a customer!",category='error')
            return redirect(url_for('views.adminDashboard'))
        else:
            flash("You are a driver, not a customer!",category='error')
            return redirect(url_for('views.driverDashboard'))
    else:
        flash("Please login first as a customer",category='error')
        return redirect(url_for('auth.login'))


@views.route('/adminDashboard')
def adminDashboard():
    if g.user:
        if session['idmatch'] == True:
            admin = Admin.query.filter_by(email=session['email']).first()
            if admin:
                return render_template('adminDashboard.html')
            elif session['role'] == 2:
                flash("You are a customer, not an admin!",category='error')
                return redirect(url_for('views.userDashboard'))
            else:
                flash("You are a driver, not an admin!",category='error')
                return redirect(url_for('views.driverDashboard'))
        else:
            flash("Please confirm your identity!",category="error")
            return redirect(url_for('auth.faceRecognition'))
    else:
        flash("Please login first as an admin",category='error')
        return redirect(url_for('auth.login'))

@views.route('/driverDashboard')
def driverDashboard():
    if g.user:
        if session['idmatch'] == True:
            driver = Driver.query.filter_by(email=session['email']).first()
            if driver:
                return render_template('driverDashboard.html',driver=driver)
            elif session['role'] == 2:
                flash("You are a customer, not a driver!",category='error')
                return redirect(url_for('views.userDashboard'))
            else:
                flash("You are an admin, not a driver!",category='error')
                return redirect(url_for('views.adminDashboard'))
        else:
            flash("Please confirm your identity!",category="error")
            return redirect(url_for('auth.faceRecognition'))
    else:
        flash("Please login first as a driver",category='error')
        return redirect(url_for('auth.login'))

@views.route('/waitingLobby')
def waitingLobby():
    return render_template('waitingLobby.html')   

@views.route('/driverApplications',methods=['GET','POST'])
def driverApplications():
    con = verifyUser("Admin")
    #Only admins can access this page
    if con:
        drivers = Driver.query.filter_by(status=0).all()
        return render_template('driverApplications.html',drivers=drivers)
    else:
        flash("Not an Admin!",category="error")
        return redirect(url_for('auth.logout'))

@views.route('reject-driver',methods = ['POST'])
def reject_driver():
    driver = json.loads(request.data)
    driverId = driver['driverId']
    driver = Driver.query.get(driverId)
    if driver:
        driver.status = 2
        db.session.commit()
    del driver
    del driverId
    gc.collect()
    return jsonify({})

@views.route('accept-driver',methods = ['POST'])
def accept_driver():
    driver = json.loads(request.data)
    driverId = driver['driverId']
    driver = Driver.query.get(driverId)
    if driver:
        driver.status = 1
        db.session.commit()
    del driver
    del driverId
    gc.collect()
    return jsonify({})

@views.route('/fireDriver',methods=['GET','POST'])
def fireDriver():
    con = verifyUser("Admin")
    if con:
        drivers = Driver.query.limit(10).all()
        return render_template('fireDriver.html',drivers=drivers)
    else:
        flash("Not an Admin!",category="error")
        return redirect(url_for('auth.logout'))

@views.route('fire-driver',methods = ['POST'])
def fire_driver():
    driver = json.loads(request.data)
    driverId = driver['driverId']
    driver = Driver.query.get(driverId)
    if driver:
        db.session.delete(driver)
        db.session.commit()
    del driver
    del driverId
    gc.collect()
    return jsonify({})

@views.route('/manageTrucks',methods=['GET','POST'])
def manageTrucks():
    con = verifyUser("Admin")
    if con:
        trucks = Truck.query.limit(30).all()
        driver = Driver.query.limit(30).all()
        if request.method == "POST":
            truckNo = request.form.get("truckNo")
            driverId = request.form.get('driverId')
            truck = Truck.query.filter_by(truckNumber = truckNo).first()
            driver = Driver.query.filter_by(id = driverId).first()
            if truck:
                flash("Truck already exists!",category='error')
            elif len(truckNo) < 6:
                flash("Invalid Truck Number. It should be greater than 6 characters!",category="error")
            elif driver:
                newTruck = Truck(truckNumber = truckNo)
                db.session.add(newTruck)
                db.session.commit()
                truck = Truck.query.filter_by(truckNumber = truckNo).first()
                driver.truckNumber = truck.id
                db.session.commit()
                flash("New Truck added!",category='success')
                del truckNo, driverId,truck,driver,newTruck
                gc.collect()
                return redirect(url_for('views.manageTrucks'))
            else:
                flash("Driver does not exist!",category='error')
        return render_template('manageTrucks.html',trucks=trucks,driver=driver)
    else:
        flash("Not an Admin!",category="error")
        return redirect(url_for('auth.logout'))

@views.route('delete-truck',methods = ['POST'])
def delete_truck():
    truck = json.loads(request.data)
    truckId = truck['truckId']
    truck = Truck.query.get(truckId)
    if truck:
        db.session.delete(truck)
        db.session.commit()
    del truck,truckId,truck
    gc.collect()
    return jsonify({})

@views.route('delete-checkpoint',methods = ['POST'])
def delete_checkpoint():
    checkpoint = json.loads(request.data)
    checkpointId = checkpoint['checkpointId']
    checkpoint = Checkpoint.query.get(checkpointId)
    if checkpoint:
        db.session.delete(checkpoint)
        db.session.commit()
    return jsonify({})

@views.route('/driverLocation',methods=['GET','POST'])
def driverLocation():
    con = verifyUser("Admin")
    if con:
        drivers = Driver.query.filter_by(status=1).all()
        checkp = Checkpoint.query.limit(10).all()
        if request.method == "POST":
            checkpoint = request.form.get("checkpoint")
            check = Checkpoint.query.filter_by(location=checkpoint).first()
            if check:
                flash("Checkpoint already exists!",category='error')
            elif len(checkpoint) < 4:
                flash("Checkpoint name must be greater than 4 characters!",category='error')
            else:
                newCheckpoint = Checkpoint(location = checkpoint)
                db.session.add(newCheckpoint)
                db.session.commit()
                flash("Checkpoint added successfully!",category='success')
                del drivers,checkp,checkpoint,check
                gc.collect()
                return redirect(url_for('views.driverLocation'))

        return render_template('driverLocation.html',drivers=drivers,checkpoints = checkp)
    else:
        flash("Not an Admin!",category="error")
        return redirect(url_for('auth.logout'))

@views.route("/manageOrder",methods = ['GET','POST'])
def manageOrder():
    con = verifyUser("Admin")
    if con:
        orders = Order.query.limit(30).all()
        truck = Truck.query.limit(30).all()
        driver = Driver.query.limit(30).all()
        cust = Customer.query.limit(30).all()
        checkpoint = Checkpoint.query.limit(10).all()
        if request.method == "POST":
            details = request.form.get("details")
            truckId = request.form.get("truckId")
            customerId = request.form.get("customerId")
            origin = request.form.get("origin")
            final = request.form.get("final")
            if (origin == "Banglore" or origin == "Mumbai" or origin == "Delhi") and (final == "Banglore" or final == "Mumbai" or final == "Delhi"):
                driverID = Driver.query.filter_by(truckNumber = truckId).first()
                newOrder = Order(customerId = customerId,details=details,truckNumber=truckId,origin=origin,finalStation=final,driverId=driverID.id)
                db.session.add(newOrder)
                db.session.commit()
                flash("Order created successfully!",category="success")
                del details,truckId,customerId,origin,final
                gc.collect()
                return redirect(url_for('views.manageOrder'))
            else:
                flash("Select the correct origin and final station!",category='error')
        return render_template('manageOrder.html',orders=orders,trucks=truck,checkp = checkpoint,cust=cust,driver=driver)
    else:
        flash("Not an Admin!",category="error")
        return redirect(url_for('auth.logout'))

@views.route('delete-order',methods = ['POST'])
def delete_order():
    order = json.loads(request.data)
    orderId = order['orderId']
    order = Order.query.get(orderId)
    if order:
        db.session.delete(order)
        db.session.commit()
    del order,orderId
    gc.collect()
    return jsonify({})

@views.route('/pendingOrder',methods = ['GET','POST'])
def pendingOrder():
    con = verifyUser("Driver")
    if con:
        #Check if driver has already started a previous journey before logging out
        order = Order.query.filter_by(driverId=session["user"]).all()
        if order:
            for o in order:
                if o.status == "Enroute":
                    flash("Please continue with the previous journey!",category='error')
                    return redirect(url_for('views.dFaceRecognition'))
        else: 
            order = Order.query.filter_by(driverId=session["user"]).all()
        return render_template('pendingOrder.html',orders=order)
    else:
        flash("Not a Driver!",category="error")
        return redirect(url_for('auth.logout'))


@views.route('start-journey',methods = ['POST'])
def start_journey():
    order = json.loads(request.data)
    orderId = order['orderId']
    order = Order.query.get(orderId)
    if order:
        #Store oder info in session variable
        session['porder'] = order.id
    del order,orderId
    gc.collect()
    return jsonify({})

@views.route('/dFaceRecognition',methods=['GET','POST'])
def dFaceRecognition():
    #Function to begin journey by recognizing the face
    con = verifyUser("Driver")
    if con:
        if request.method == 'POST':
            identity = getIdentity(VideoCamera(),"toMatch")
            identityEnc = encFromByte(identity)
            driver = Driver.query.filter_by(email=session['email']).first()
            dbIdentity = encFromByte(driver.identity)
            result = is_match(dbIdentity,identityEnc)
            if result:
                flash('Identity confirmed! Happy Journey!',category="success")
                order = Order.query.filter_by(id = session['porder']).first()
                cp = Checkpoint.query.filter_by(location = order.origin).first()
                order.status = "Enroute"
                order.checkPoint = cp.id
                db.session.commit()
                #Store delivery stations in session variables
                session['begin'] = order.origin
                session['final'] = order.finalStation
                del identity,identityEnc,driver,dbIdentity,result
                gc.collect()
                return redirect(url_for('views.journey'))
            else:
                flash("Identity not matched! Please retry",category='error')

        return render_template('dFaceRecognition.html',Type = "begin")
    else:
        flash("Not a Driver!",category="error")
        return redirect(url_for('auth.logout'))

@views.route('/eFaceRecognition',methods=['GET','POST'])
def eFaceRecognition():
    #Function to end journey by recognizing the face
    con = verifyUser("Driver")
    if con:
        if request.method == 'POST':
            identity = getIdentity(VideoCamera(),"toMatch")
            identityEnc = encFromByte(identity)
            driver = Driver.query.filter_by(email=session['email']).first()
            dbIdentity = encFromByte(driver.identity)
            result = is_match(dbIdentity,identityEnc)
            if result:
                flash('Identity confirmed! Order delivered successfully!',category="success")
                order = Order.query.filter_by(id = session['porder']).first()
                order.status = "Delivered"
                order.dateDelivered = func.now()
                cp = Checkpoint.query.filter_by(location = session['final']).first()
                order.checkPoint = cp.id
                db.session.commit()
                #Pop session variables since order is delivered
                session["porder"] = ""
                session['begin'] = ""
                session.pop('final',None)
                del identity,identityEnc,driver,dbIdentity,result
                gc.collect()
                return redirect(url_for('views.driverDashboard'))
            else:
                flash("Identity not matched! Please retry",category='error')

        return render_template('dFaceRecognition.html',Type = "end")
    else:
        flash("Not a Driver!",category="error")
        return redirect(url_for('auth.logout'))

@views.route('/journey',methods = ['GET','POST'])
def journey():
    con = verifyUser("Driver")
    if con:
        img = "static/images/" + session['begin'][0] + "2" + session['final'][0] + ".png"
        if request.method == "POST":
            return redirect(url_for('views.eFaceRecognition'))
        return render_template('journey.html',img=img)
    else:
        flash("Not a Driver!",category="error")
        return redirect(url_for('auth.logout'))

@views.route('/completedOrder',methods = ['GET','POST'])
def completedOrder():
    con = verifyUser("Driver")
    if con:
        currentDriver = Driver.query.filter_by(email = session['email']).first()
        order = Order.query.filter_by(truckNumber = currentDriver.truckNumber).all()
        return render_template('completedOrder.html',orders=order)
    else:
        flash("Not a Driver!",category="error")
        return redirect(url_for('auth.logout'))

@views.route("/userOrder",methods = ['GET','POST'])
def userOrder():
    con = verifyUser("Customer")
    if con:
        cust = Customer.query.filter_by(email = session['email']).first()
        if cust:
            order = Order.query.filter_by(customerId = cust.id).all()
            return render_template('userOrder.html',orders=order)
    else:
        flash("Not a Customer!",category="error")
        return redirect(url_for('auth.logout'))        

@views.route('track-order',methods = ['POST'])
def track_order():
    order = json.loads(request.data)
    orderId = order['orderId']
    order = Order.query.get(orderId)
    if order:
        session['porder'] = order.id
    del order,orderId
    gc.collect()
    return jsonify({})

@views.route('/trackOrder')
def trackOrder():
    con = verifyUser("Customer")
    if con:
        order = Order.query.filter_by(id = session['porder']).first()
        checkpoint = Checkpoint.query.filter_by(id = order.checkPoint).first()
        return render_template('trackOrder.html',order=order,cp = checkpoint)
    else:
        flash("Not a Customer!",category="error")
        return redirect(url_for('auth.logout'))
    
@views.route('/knowMore')
def knowMore():
    return render_template('knowMore.html')