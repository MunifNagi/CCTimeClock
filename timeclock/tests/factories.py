# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory

from app.database import db
from app.user.models import User


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = PostGenerationMethodCall("set_password", "Change4me")
    is_active = True

    class Meta:
        """Factory configuration."""

        model = User
