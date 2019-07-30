# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt
import pytest
from app.user.models import User
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
        user = User.create(password="foobarbaz123")
        assert user.verify_password("foobarbaz123") is True
        assert user.verify_password("barfoobaz") is False

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