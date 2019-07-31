# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt
import time
import pytest
from app.user.models import User, Password, Role, Permission
from .factories import UserFactory
@pytest.mark.usefixtures("db")
class TestUser:
    """User tests."""

    def test_get_by_id(self):
        """Get user by ID."""
        user = User(email="test1@records.nyc.gov",password="Password1")
        user.save()
        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_password_is_unreadable(self):
        """Test null password."""
        user = User(password="Password1")
        user.save()
        with pytest.raises(AttributeError): user.password 

    def test_verify_password(self):
        """Check password."""
        user = User.create(password="Change4me")
        assert user.verify_password("Change4me") is True
        assert user.verify_password("change4me") is False
    
    def test_reset_password(self):
        """Check password."""
        user = User.create(password="Change4me")
        time.sleep(1)
        token = user.generate_reset_token() 
        assert user.reset_password(token,"Change4me!") is True #should accept symbols
        time.sleep(1) #It must have at least 1 number
        assert user.reset_password(token,"Changeme!") is False 
        time.sleep(1) #It should be at least 8 characters 
        assert user.reset_password(token,"Change4") is False
        time.sleep(1) #It should have at least 1 UpperCase 
        assert user.reset_password(token,"change4me") is False

    def test_full_name(self):
        """User full name."""
        user = User(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"

    def test_supervisor(self):
        """Get user by ID."""
        user = User(email="test@records.nyc.gov")
        user2= User(email="test2@records.nyc.gov")
        user2.supervisor=user
        user.save()
        user2.save()
        assert user2.supervisor_id==user.id
        assert user2.is_supervisor==False
        assert user.is_supervisor==True

    def test_roles(self):
        """Add a role to a users."""
        Role.insert_roles()
        user= Role.query.filter_by(name="User").first()
        admin = Role.query.filter_by(name="Administrator").first()
        moderator=Role.query.filter_by(name="Moderator").first()

        person1 = User.create(email="test1@records.nyc.gov")
        person2= User.create(email="test2@records.nyc.gov")
        person3= User.create(email="test3@records.nyc.gov")

        person1.role=admin
        person2.role=user
        person3.role=moderator

        person1.save()
        person2.save()
        person3.save()
        assert person1.is_administrator() is True and person1.role.permissions == 0xff
        assert person2.is_administrator() is False and person2.role.permissions == 0x01
        assert person3.is_administrator() is False and person3.role.permissions == 0x80
    