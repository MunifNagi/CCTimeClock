# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from flask import flash

"""
.. module:: utils.

   :synopsis: Utility functions used throughout the application.
"""

divisions = [
    ('', ''),
    ('Administration', 'Administration'),
    ('Archives', 'Archives'),
    ('Grants', 'Grants'),
    ('Library', 'Library'),
    ('Records Management', 'Records Management'),
    ('Reference Room', 'Reference Room'),
    ('Social Media', 'Social Media'),
    ('Tech', 'Tech'),
]

roles = [
    ('User', 'User'),
    ('Administrator', 'Administrator')
]

tags = [
    (0, ''),
    (1, 'Intern'),
    (2, 'Contractor'),
    (3, 'SYEP'),
    (4, 'PENCIL'),
    (5, 'Employee'),
    (6, 'Volunteer'),
    (7, 'Other')
]


class InvalidResetToken(Exception):
    pass

def eval_request_bool(val, default=False):
    """
    Evaluates the boolean value of a request parameter.
    :param val: the value to check
    :param default: bool to return by default
    :return: Boolean
    """
    assert isinstance(default, bool)
    if val is not None:
        val = val.lower()
        if val in ['False', 'false', '0', 'n', 'no', 'off']:
            return False
        if val in ['True', 'true', '1', 'y', 'yes', 'on']:
            return True
    return default
def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}".format(getattr(form, field).label.text, error), category)
