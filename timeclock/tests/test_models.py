# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt
import time
import pytest
from app.user.models import User, Password
from .factories import UserFactory
@pytest.mark.usefixtures("db")
class TestUser:
    """User tests."""

    def test_get_by_id(self):
        """Get user by ID."""
        user = User(email="test@records.nyc.gov",password="Password1")
        user.save()
        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    # def test_created_at_defaults_to_datetime(self):
    #     """Test creation date."""
    #     user = User(email="test@records.nyc.gov",password="Password1")
    #     user.save()
    #     assert bool(user.created_at)
    #     assert isinstance(user.created_at, dt.datetime)

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