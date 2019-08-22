# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
from app.user.models import User, Role, Tag, Password
from app.auth.forms import LoginForm
from .factories import UserFactory
from flask_login import login_user

class TestLoggingIn:
    """Login."""

    def test_can_log_in_returns_200(self, user, testapp):
        """Login successful."""
        # Goes to homepage
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "Change4me"
        # Submits
        res = form.submit().follow()
        res = testapp.get('/')
        assert res.status_code == 200 
        
    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        res = testapp.get("/login")
        # Fills out login form, password incorrect
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "wrongPassword1"
        # Submits
        res = form.submit()
        # sees error
        assert "Invalid password" in res

    def test_sees_error_message_if_user_is_inactive (self, user, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        res = testapp.get("/login")
        #make user inactive
        user.is_active=False
        # Fills out login form
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "Change4me"
        # Submits
        res = form.submit()
        # sees error
        assert "User not activated" in res

    def test_sees_error_message_if_emails_doesnt_exist(self, user, testapp):
        """Show error if email doesn't exist."""
        # Goes to homepage
        res = testapp.get("/login")
        # Fills out login form, password incorrect
        form = res.forms[0]
        form["email"] = "unknown@records.nyc.gov"
        form["password"] = "Change4me"
        # Submits
        res = form.submit()
        # sees error
        assert "Unknown email" in res

class TestAdminRegistering:
    """Register a user."""

    def test_can_register(self, admin, testapp):
        """Register a new user."""
        Tag.insert_tags()
        old_count = len(User.query.all())
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms[0]
        form["email"] = admin.email
        form["password"] = "Change4me"
        # Goes to homepage
        res = form.submit().follow()
        res = testapp.get("/admin_register")
        #Fills out the form
        Registerform = res.forms[0]
        Registerform["email"] = "test@records.nyc.gov"
        Registerform["first_name"] = "Doris"
        Registerform["last_name"] = "Chambers"
        Registerform["division"] = "Archives"
        Registerform["tag"] = 1
        Registerform["supervisor_email"] = admin.id
        Registerform["is_supervisor"]= False
        Registerform["role"]= "User"
        # Submits
        res = Registerform.submit('Register')
        # # A new user was created
        assert len(User.query.all()) == old_count + 1

class TestChangeUserInfo:
    """Change user's info."""

    def test_change_user(self, admin, user, testapp,db):
        """Change user's info"""
        Tag.insert_tags()
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms[0]
        form["email"] = admin.email
        form["password"] = "Change4me"
        # Goes to homepage
        res = form.submit().follow()
        res = testapp.get("/user/"+str(user.id))
        #Fills out the form
        changeform = res.forms[0]
        changeform["first_name"] = "Doris"
        changeform["last_name"] = "Chambers"
        changeform["division"] = "Archives"
        changeform["tag"] = 1
        changeform["supervisor_email"] = admin.id
        changeform["is_supervisor"]= False
        changeform["is_active"]= True
        changeform["role"]= "User"
        # Submits
        res = changeform.submit('submit', value="Update").follow()
        assert res.status_code == 200
        # User has been updated
    
class TestChangePassword:
    """Change Password"""
    def test_change_successful(self, testapp, user):
        """Change password."""
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "Change4me"
        # Goes to homepage
        res = form.submit().follow()
        res= testapp.get('/change_password')
        assert res.status_code == 200
        form = res.forms[0]
        form["old_password"]="Change4me"
        form["password"]="Munif1234"
        form["password2"]="Munif1234"
        res = form.submit().follow()
        res = testapp.get('/')
        assert res.status_code == 200

    def test_unsuccessful(self, user, testapp, db):
        user.password_list = Password(p1=generate_password_hash('Change4me'), p2=generate_password_hash('Change3me'), p3=generate_password_hash('Change2me'), p4=generate_password_hash('Doris1234'), p5=generate_password_hash('31Chambers'),last_changed=datetime.now())
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "Change4me"
        # Goes to homepage
        res = form.submit().follow()
        res= testapp.get('/change_password')
        assert res.status_code == 200
        form = res.forms[0]
        form["old_password"]="Change4me"
        form["password"]="Doris1234"
        form["password2"]="Doris1234"
        res = form.submit()
        assert 'Your password cannot be the same as the last 5 passwords' in res
        assert res.status_code == 200

class TestRequestTimePunch:
    """Request Time Punch"""

    def test_request_successful(self, testapp, user,admin,db):
        """successful timepunch """
        user.supervisor=admin
        user.supervisor_id=admin.id
        db.session.commit()
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "Change4me"
        # Goes to homepage
        res = form.submit().follow()
        res= testapp.get('/request_timepunch')
        form = res.forms[0]
        form["punch_type"]="In"
        form["punch_date"]="2019-08-22"
        form["punch_time"]="10:00"
        form["note"]="just a test note"
        res =form.submit('submit', value="Submit Request").follow()
        res.mustcontain('<html>')
        assert 'Your timepunch request has been successfully submitted and is pending approval' in res

    def test_request_unsuccessful(self, testapp, user,db):
        """Unsuccessful timepunch(No Supervisor)"""
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "Change4me"
        # Goes to homepage
        res = form.submit().follow()
        res= testapp.get('/request_timepunch')
        form = res.forms[0]
        form["punch_type"]="In"
        form["punch_date"]="2019-08-22"
        form["punch_time"]="10:00"
        form["note"]="just a test note"
        res =form.submit('submit', value="Submit Request")
        res.mustcontain('<html>')
        assert 'You must have a supervisor to request a timepunch. If you believe a supervisor should be assigned to you, please contact the system administrator.' in res