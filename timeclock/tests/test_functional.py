# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from flask import url_for

from app.user.models import User, Role, Tag
from app.auth.forms import LoginForm
from .factories import UserFactory

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
        res = testapp.get('/change_password')
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

    def test_can_register(self, user, testapp,db):
        """Register a new user."""
        Role.insert_roles()
        Tag.insert_tags()
        old_count = len(User.query.all())
        user.role=Role.query.filter_by(name="Administrator").first()
        user.save()
        #creating supervisor and increment # of users
        user2= User(email="test2@records.nyc.gov")
        user2.division="Archives"
        user.supervisor=user2
        user.supervisor_id=user2.id
        db.session.commit()
        old_count += 1
        user2.is_supervisor= True
        # assert user.is_administrator() is True
        res = testapp.get('/login')
        # Fills out login form in navbar
        form = res.forms[0]
        form["email"] = user.email
        form["password"] = "Change4me"
        # Goes to homepage
        res = form.submit().follow()
        # res.showbrowser()
        res= testapp.get('/change_password')
        assert res.status_code == 200
        form = res.forms[0]
        form["old_password"]="Change4me"
        form["password"]="Munif1234"
        form["password2"]="Munif1234"
        res = form.submit().follow()
        res = testapp.get('/')
        assert res.status_code == 200
        # res.click(description="Register User",href=url_for('auth.admin_register'))
        res = testapp.get("/admin_register")
        assert res.status_code == 200  
        #Fills out the form
        Registerform = res.forms[0]
        Registerform["email"] = "test@records.nyc.gov"
        Registerform["first_name"] = "Doris"
        Registerform["last_name"] = "Chambers"
        Registerform["division"] = "Archives"
        Registerform["tag"] = 1
        Registerform["supervisor_email"] = user2.id
        Registerform["is_supervisor"]= False
        Registerform["role"]= "User"
        # Submits
        res = Registerform.submit('Register')
        # # A new user was created
        assert len(User.query.all()) == old_count + 1

