from flask import Blueprint, render_template, request, flash, redirect, url_for,session,g,Response
from .models import Customer, Driver, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from .helperFunc import *
from .camera import VideoCamera
import cv2
import gc

def gen(camera):
    """
    Input - videoframe object
    Output - Frames encoded as jpeg to output on the HTML page
    """
    while True:
        frame = camera.getFrame()
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def getIdentity(camera,name):
    """
    Input - Video frame object, name of the person whose identity is being evaluated
    Function - Capture a frame from the video stream, save it as an image, get the embeddings of the image
                and convert it to bytes
    Output - Image embedding encoded in bytes
    """
    frame = camera.returnFrame()
    cv2.imwrite('./website/static/images/' + name + '.jpg',frame)
    imageName = "./website/static/images/" + name + ".jpg"
    faceEmbedding = get_embeddings([imageName])   
    identity = faceEmbedding[0].tobytes()
    return identity

auth = Blueprint('auth',__name__)

@auth.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        email = request.form.get('email')
        password = request.form.get('password')
        if user == "customer":
            customer = Customer.query.filter_by(email=email).first()
            if customer:
                if check_password_hash(customer.password,password):
                    flash("Logged in successfully!",category='success')
                    #Set all the session variables on successful login
                    session['user'] = customer.email
                    session['role'] = customer.role_id
                    session['email'] = customer.email
                    session['name'] = customer.name
                    del user,email,password,customer
                    gc.collect()
                    return redirect(url_for('views.userDashboard'))
                else:
                    flash("Incorrect password, try again!",category='error')
            else:
                flash('Email does not exist!',category='error')
        elif user == "admin":
            admin = Admin.query.filter_by(email=email).first()
            if admin:
                if check_password_hash(admin.password,password):
                    #Set all the session variables on successful login
                    session['user'] = admin.id
                    session['role'] = admin.role_id
                    session['email'] = admin.email
                    session['name'] = admin.name
                    session['idmatch'] = False
                    flash("Successfully completed the first authentication test!",category='success')
                    #Do not show the dashboard until face is verified, so redirect to face recognition
                    return redirect(url_for('auth.faceRecognition'))
                else:
                    flash("Incorrect password, try again!",category='error')
            else:
                flash('Email does not exist!',category='error')
        elif user == "driver":
            driver = Driver.query.filter_by(email=email).first()
            if driver:
                if check_password_hash(driver.password,password):
                    #Set all the session variables on successful login
                    if driver.status == 1:  #For accepted drivers
                        session['user'] = driver.id
                        session['role'] = driver.role_id
                        session['email'] = driver.email
                        session['name'] = driver.name
                        session['begin'] = ""
                        session['idmatch'] = False
                        flash("Successfully completed the first authentication test!",category='success')
                        #Do not show the dashboard until face is verified, so redirect to face recognition
                        return redirect(url_for('auth.faceRecognition'))
                    elif driver.status == 2: #For drivers waiting approval
                        session['waiting'] = 2
                        return redirect(url_for('views.waitingLobby'))
                    elif driver.status == 0: #For rejected drivers
                        session['waiting'] = 0
                        return redirect(url_for('views.waitingLobby'))

                else:
                    flash("Incorrect password, try again!",category='error')
            else:
                flash('Email does not exist!',category='error')

    return render_template('login.html' )

@auth.route('/faceRecognition',methods=['GET','POST'])
def faceRecognition():
    if request.method == 'POST':
        identity = getIdentity(VideoCamera(),"toMatch")
        identityEnc = encFromByte(identity)
        if session['role'] == 3:  #If user whose identity is to be matched is a driver
            driver = Driver.query.filter_by(email=session['email']).first()
            dbIdentity = encFromByte(driver.identity)  #A helper function
            result = is_match(dbIdentity,identityEnc)  #A helper function
            if result:
                flash('Identity confirmed! Welcome Driver',category="success")
                session['idmatch'] = True
                del identityEnc,identity,driver,dbIdentity,result
                gc.collect()
                return redirect(url_for('views.driverDashboard'))
            else:
                del identityEnc,identity,driver,dbIdentity,result
                gc.collect()
                flash("Identity not matched! Please retry",category='error')
                
        else:   #If user whose identity is to be matched is an admin
            admin = Admin.query.filter_by(email=session['email']).first()
            dbIdentity = encFromByte(admin.identity)  #A helper function
            result = is_match(dbIdentity,identityEnc)  #A helper function
            if result:
                flash('Identity confirmed! Welcome Admin',category="success")
                session['idmatch'] = True
                del identityEnc,identity,admin,dbIdentity,result
                gc.collect()
                return redirect(url_for('views.adminDashboard'))
            else:
                del identityEnc,identity,admin,dbIdentity,result
                gc.collect()
                flash("Identity not matched! Please retry",category="error")

    return render_template('faceRecognition.html')

@auth.route('/logout')
def logout():
    if g.user and session['user']:
        g.user = None
        # Free all session variables
        session.pop('user',None)
        session.pop('role',None)
        session.pop('email',None)
        session.pop('name',None)
        session.pop('waiting',None)
        session.pop('idmatch',None)
        flash("You have been logged out successfully")
        return redirect(url_for('views.HomePage'))

@auth.route('/userSignUp', methods = ['GET','POST'])
def userSignUp():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        name = str(firstName) + " " + str(lastName)
        email = request.form.get('email')
        password = request.form.get('password')
        Cpassword = request.form.get('confirmPassword')
        address = request.form.get('address')
        contact = str(request.form.get('contact'))

        customer = Customer.query.filter_by(email=email).first()
        admin = Admin.query.filter_by(email=email).first()
        driver = Driver.query.filter_by(email=email).first()
        if customer:
            flash('Email already exist!',category="error")
        elif admin:
            flash('You are already an admin!',category="error")
        elif driver:
            flash('You are already a driver!',category="error")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password != Cpassword:
            flash('Passwords don\'t match.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif len(address) < 10:
            flash('Address must be atleast 10 characters', category='error')
        elif len(contact) < 10 or len(contact) > 10:
            flash('Contact should be 10 digits only')
        else:
            newCustomer = Customer(email=email,password=generate_password_hash(password,method='sha256'),
            name=name,address=address,contact=int(contact),role_id=2)
            db.session.add(newCustomer)
            db.session.commit()
            customer = Customer.query.filter_by(email=email).first()
            session['user'] = customer.id
            session['role'] = customer.role_id
            session['email'] = customer.email
            session['name'] = customer.name
            flash('Account created successfully',category='success')
            del firstName,lastName,name,email,password,Cpassword,address,contact,customer,admin,driver,newCustomer
            gc.collect()
            return redirect(url_for('views.userDashboard'))

    return render_template('userSignUp.html')

"""
@auth.route('/adminSignUp', methods = ['GET','POST'])
def adminSignUp():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        name = str(firstName) + " " + str(lastName)
        email = request.form.get('email')
        password = request.form.get('password')
        Cpassword = request.form.get('confirmPassword')
        identity = getIdentity(VideoCamera(),firstName)

        customer = Customer.query.filter_by(email=email).first()
        admin = Admin.query.filter_by(email=email).first()
        driver = Driver.query.filter_by(email=email).first()
        if admin:
            flash('Email already exist!',category="error")
        elif driver:
            flash('You are already a driver!',category="error")
        elif customer:
            flash('You are already a customer!',category="error")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password != Cpassword:
            flash('Passwords don\'t match.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            newAdmin = Admin(email=email,password=generate_password_hash(password,method='sha256'),
            name=name,identity = identity,role_id=1)
            db.session.add(newAdmin)
            db.session.commit()
            admin = Admin.query.filter_by(email=email).first()
            session['user'] = admin.id
            session['role'] = admin.role_id
            session['email'] = admin.email
            session['name'] = admin.name
            session['idmatch'] = True
            flash('Account created successfully',category='success')
            del firstName,lastName,email,name,password,Cpassword,identity,customer,admin,driver,newAdmin
            gc.collect()
            return redirect(url_for('views.adminDashboard'))

    return render_template('adminSignUp.html')
"""
@auth.route('/driverSignUp',methods = ['GET','POST'])
def driverSignUp():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        name = str(firstName) + " " + str(lastName)
        email = request.form.get('email')
        password = request.form.get('password')
        Cpassword = request.form.get('confirmPassword')
        address = request.form.get('address')
        contact = str(request.form.get('contact'))
        licence = request.form.get('licence')
        identity = getIdentity(VideoCamera(),firstName)

        customer = Customer.query.filter_by(email=email).first()
        admin = Admin.query.filter_by(email=email).first()
        driver = Driver.query.filter_by(email=email).first()
        if driver:
            flash('Email already exist!',category="error")
        elif admin:
            flash('You are already an admin!',category="error")
        elif customer:
            flash('You are already a customer!',category="error")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password != Cpassword:
            flash('Passwords don\'t match.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif len(address) < 10:
            flash('Address must be atleast 10 characters', category='error')
        elif len(contact) < 10 or len(contact) > 10:
            flash('Contact should be 10 digits only!')
        elif len(licence) < 8:
            flash("Enter a valid licence number!")
        else:
            newDriver = Driver(email=email,password=generate_password_hash(password,method='sha256'),
            name=name,address=address,contact=contact,license=licence,identity = identity,role_id=3,status=0)
            db.session.add(newDriver)
            db.session.commit()
            flash('Account submitted for review!',category='success')
            session['waiting'] = 0
            del firstName,lastName,email,name,password,Cpassword,identity,customer,admin,driver,newDriver
            gc.collect()
            return redirect(url_for('views.waitingLobby'))


    return render_template('driverSignUp.html')

@auth.route('/videoFeed')
def videoFeed():
    # Return video stream captured from webcam
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace;boundary=frame')

@auth.route('/changePass',methods = ['GET','POST'])
def changePass():
    if g.user:
        if request.method == "POST":
            oldPass = request.form.get('oldPassword')
            newPass = request.form.get('newPassword')
            cnewPass = request.form.get('confirmNewPassword')
            if newPass != cnewPass:
                flash('New passwords do not match!',category='error')
            elif len(newPass) < 7:
                flash('Password must be at least 7 characters.', category='error')
            elif session['role'] == 1:
                admin = Admin.query.filter_by(email=session['email']).first()
                if check_password_hash(admin.password,oldPass):
                    admin.password = generate_password_hash(newPass,method='sha256')
                    db.session.commit()
                    flash('Password changed successfully',category='success')
                    del oldPass,newPass,cnewPass
                    gc.collect()
                    return redirect(url_for('views.adminDashboard'))
                else:
                    flash('Old password do not match!',category='error')
            elif session['role'] == 2:
                customer = Customer.query.filter_by(email=session['email']).first()
                if check_password_hash(customer.password,oldPass):
                    customer.password = generate_password_hash(newPass,method='sha256')
                    db.session.commit()
                    flash('Password changed successfully',category='success')
                    del oldPass,newPass,cnewPass
                    gc.collect()
                    return redirect(url_for('views.userDashboard'))
                else:
                    flash('Old password do not match!',category='error')
            elif session['role'] == 3:
                driver = Driver.query.filter_by(email=session['email']).first()
                if check_password_hash(driver.password,oldPass):
                    driver.password = generate_password_hash(newPass,method='sha256')
                    db.session.commit()
                    flash('Password changed successfully',category='success')
                    del oldPass,newPass,cnewPass
                    gc.collect()
                    return redirect(url_for('views.driverDashboard'))
                else:
                    flash('Old password do not match!',category='error')
        return render_template("changePass.html")
    else:
        flash("Not Logged In!",category='error')
        return redirect(url_for('views.HomePage'))

@auth.route('/changeAddress',methods = ['GET','POST'])
def changeAddress():
    if g.user:
        if request.method == "POST":
            password = request.form.get("password")
            address = request.form.get("newAddress")
            customer = Customer.query.filter_by(email=session['email']).first()
            if len(address) < 10:
                flash('Address must be atleast 10 characters', category='error')
            elif check_password_hash(customer.password,password):
                customer.address = address
                db.session.commit()
                flash("Address changed successfully!",category='success')
                del password,address,customer
                gc.collect()
                return redirect(url_for("views.userDashboard"))
            else:
                flash("You entered the wrong password!",category='error')

        return render_template("changeAddress.html")
    else:
        flash("Not Logged In!",category='error')
        return redirect(url_for('views.HomePage'))