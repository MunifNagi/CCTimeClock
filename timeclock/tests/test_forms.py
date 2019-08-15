# -*- coding: utf-8 -*-
"""Test forms."""

from app.auth.forms import LoginForm
from app.auth.forms import AdminRegistrationForm
from app.utils import tags, divisions, roles
from app.user.models import User
class TestLoginForm:
    """Login form."""

    def test_validate_success(self, user):
        """Login successful."""
        user.set_password("31Ch@mbers")
        user.save()
        form = LoginForm(email=user.email, password="31Ch@mbers")
        assert form.validate() is True
        assert form.user == user

    def test_validate_unknown_email(self, db):
        """Unknown email."""
        form = LoginForm(email="unknown@records.nyc.gov", password="31Ch@mbers")
        assert form.validate() is False
        assert "Unknown email" in form.email.errors
        assert form.user is None

    def test_validate_invalid_password(self, user):
        """Invalid password."""
        user.set_password("31Ch@mbers")
        user.save()
        form = LoginForm(email=user.email, password="Wrong1234")
        assert form.validate() is False
        assert "Invalid password" in form.password.errors

    def test_validate_inactive_user(self, user):
        """Inactive user."""
        user.is_active = False
        user.set_password("31Ch@mbers")
        user.save()
        # Correct username and password, but user is not activated
        form = LoginForm(email=user.email, password="31Ch@mbers")
        assert form.validate() is False
        assert "User not activated" in form.email.errors

class TestAdminRegisterForm:
    """Admin Register form."""

    def test_validate_user_already_registered(self, user):
        """Enter email that is already registered."""
        form = AdminRegistrationForm(
            email=user.email,
            first_name="doris",
            last_name="chambers",
        )
        assert form.validate_email(form.email) is False
        assert "An account with this email address already exists" in form.email.errors

    def test_validate_email_success(self, db):
        """Register with success."""
        form = AdminRegistrationForm(
            email="new@records.nyc.gov",
            first_name="doris",
            last_name="chambers",
            division="Archives"
        )
        assert form.validate_email(form.email) is True
        assert form.validate_on_submit() is False
        assert "All users must have a tag" in form.tag.errors
        user = User(email="test1@records.nyc.gov")
        supervisor= User(email="test2@records.nyc.gov")
        user.supervisor_id=supervisor.id
        user.save()
        supervisor.save()
        form = AdminRegistrationForm(
            email="new@records.nyc.gov",
            first_name="doris",
            last_name="chambers",
            division="Archives",
            tag=1,
            supervisor_email=supervisor.id
        )
        assert form.validate_on_submit() is True
        form = AdminRegistrationForm(
            email="new@records.nyc.gov",
            first_name="doris",
            last_name="chambers",
            division="Archives",
            tag=1,
            supervisor_email=0
        )
        assert form.validate_on_submit() is False
        assert "Invalid supervisor" in form.supervisor_email.errors
