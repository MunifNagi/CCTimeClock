# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from webtest import TestApp

from app.app import create_app
from app.database import db as _db

from .factories import UserFactory
from app.user.models import User, Role
from flask_login import login_user

@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app("tests.settings")
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """Create Webtest app."""
    return TestApp(app)


@pytest.fixture
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """Create user for the tests."""
    user = UserFactory(password="Change4me")
    db.session.commit()
    return user

@pytest.fixture
def admin(db):
    Role.insert_roles()
    """Create admin for the tests."""
    admin = UserFactory(password="Change4me")
    admin.role = Role.query.filter_by(name="Administrator").first()
    admin.is_supervisor= True
    db.session.commit()
    return admin

@pytest.fixture
def authenticated_request(app):
    with app.test_request_context():
        return login_user(User(email="test@records.nyc.gov",password="Change4me"))