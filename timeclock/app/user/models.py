# # -*- coding: utf-8 -*-
# """User models."""
# import datetime as dt

# from flask_login import UserMixin

# from app.extensions import bcrypt


# class Role(SurrogatePK, Model):
#     """A role for a user."""

#     __tablename__ = "roles"
#     name = Column(db.String(80), unique=True, nullable=False)
#     user_id = reference_col("users", nullable=True)
#     user = relationship("User", backref="roles")

#     def __init__(self, name, **kwargs):
#         """Create instance."""
#         db.Model.__init__(self, name=name, **kwargs)

#     def __repr__(self):
#         """Represent instance as a unique string."""
#         return "<Role({name})>".format(name=self.name)


# class User(UserMixin, SurrogatePK, Model):
#     """A user of the app."""

#     __tablename__ = "users"
#     username = Column(db.String(80), unique=True, nullable=False)
#     email = Column(db.String(80), unique=True, nullable=False)
#     #: The hashed password
#     password = Column(db.Binary(128), nullable=True)
#     created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
#     first_name = Column(db.String(30), nullable=True)
#     last_name = Column(db.String(30), nullable=True)
#     active = Column(db.Boolean(), default=False)
#     is_admin = Column(db.Boolean(), default=False)

#     def __init__(self, username, email, password=None, **kwargs):
#         """Create instance."""
#         db.Model.__init__(self, username=username, email=email, **kwargs)
#         if password:
#             self.set_password(password)
#         else:
#             self.password = None

#     def set_password(self, password):
#         """Set password."""
#         self.password = bcrypt.generate_password_hash(password)

#     def check_password(self, value):
#         """Check password."""
#         return bcrypt.check_password_hash(self.password, value)

#     @property
#     def full_name(self):
#         """Full user name."""
#         return "{0} {1}".format(self.first_name, self.last_name)

#     def __repr__(self):
#         """Represent instance as a unique string."""
#         return "<User({username!r})>".format(username=self.username)
import re
from datetime import datetime

from flask import current_app, session
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from app.extensions import login_manager
from app.utils import InvalidResetToken


class Permission:
    """
    Used to provide user permissions and check to ensure users have proper rights.
    """
    USER = 0x01  # 0b00000001
    MODERATOR=0x80  # 0b10000000
    ADMINISTER = 0xff


class Role(SurrogatePK, Model):
    """
    Specifies the roles a user can have (normal User, Department Head(Moderator), Administrator).
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """
        Instantiates the roles column by initializing the User, Moderator, and Administrator rows.
        :return: None
        """
        roles = {
            'User': (Permission.USER, True),
            'Moderator': (Permission.MODERATOR, False),
            'Administrator': (Permission.ADMINISTER, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


# class Budget(db.Model):
#     """
#     Specifies the budget code and the corresponding budget name
#     """
#     __tablename__ = 'budget'
#     id = db.Column(db.Integer, primary_key=True)
#     budget_code = db.Column(db.Integer, default=0)
#     object_id = db.Column(db.Integer, db.ForeignKey('object.id'))
#
#     def __repr__(self):
#         return '<Budget %r' % self.budget_code
#
# class Object(db.Model):
#     """
#     Object codes and names for users
#     """
#     __tablename__ = 'object'
#     id = db.Column(db.Integer, primary_key=True)
#     object_name = db.Column(db.String(64))
#     object_code = db.Column(db.Integer, default=0)
#
#
#     @staticmethod
#     def insert_objects():
#         """
#         Inserts object codes/names into database
#         Call from manage.py with Object.insert_objects()
#         """
#         object_name = {
#             'Contract Services' : 600
#         }
#         for obj in object_name:
#             o = Object(object_name=obj)
#             o.object_code=object_name[obj]
#             db.session.add(o)
#         db.session.commit()
#
#
#
#     def __repr__(self):
#         return '<Object %r>' % self.object_name


class User(UserMixin, SurrogatePK, Model):
    """
    Specifies properties and functions of a TimeClock User.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    validated = db.Column(db.Boolean, default=False)
    division = db.Column(db.String(128))
    login_attempts = db.Column(db.Integer, default=0)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    old_passwords = db.Column(db.Integer, db.ForeignKey('passwords.id'))
    events = db.relationship('Event', backref='user', lazy='dynamic')
    pays = db.relationship('Pay', backref='user', lazy='dynamic')
    vacations = db.relationship('Vacation', backref='user', lazy='dynamic')
   # created_at = Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Supervisor
    is_supervisor = db.Column(db.Boolean, default=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    supervisor = db.relationship('User', remote_side=[id])

    # Budget/Object Codes
    budget_code = db.Column(db.String)
    object_code = db.Column(db.String)
    object_name = db.Column(db.String)

    def __init__(self, email="test@records.nyc.gov", password=None, **kwargs):
       # super(User, self).__init__(**kwargs)
        db.Model.__init__(self, email=email, **kwargs)
        if password:
            self.password=password
        else:
            self.password = None
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
                self.validated = True
            else:
                self.role = Role.query.filter_by(default=True).first()
        self.password_list = Password(p1='', p2='', p3='', p4='', p5='', last_changed=datetime.now())
    # @property
    # def is_supervisor(self):
    #     """
    #     Checks to see whether the user is a supervisor.
    #     :return: True if the user is a supervisor, False otherwise.
    #     """
    #     supervisors=[value for value, in db.session.query(User.supervisor_id).all()]
    #     return self.id in supervisors
    @property
    def full_name(self):
        """Full user name."""
        return "{0} {1}".format(self.first_name, self.last_name)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    def set_password(self, password):
        """Set password."""
        self.password_hash = generate_password_hash(password)

    @password.setter
    def password(self, password):
        """
        Creates and stores password hash.
        :param password: String to hash.
        :return: None.
        """
        if password:
            self.password_hash = generate_password_hash(password)

    # generates token with default validity for 1 hour
    def generate_reset_token(self, expiration=3600):
        """
        Generates a token users can use to reset their accounts if locked out.
        :param expiration: Seconds the token is valid for after being created (default one hour).
        :return: the token.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        session['reset_token'] = {'token': s, 'valid': True}
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        """
        Resets a user's password.
        :param token: The token to verify.
        :param new_password: The password the user will have after resetting.
        :return: True if operation is successful, false otherwise.
        """
        # checks if the new password is at least 8 characters with at least 1 UPPERCASE AND 1 NUMBER
        if len(new_password) < 8:
            return False
        score = 0
        if re.search('\d+', new_password):
            # If the new password contains a digit, increment score
            score += 1
        if re.search('[a-z]', new_password) and re.search('[A-Z]', new_password):
            # If the new password contains lowercase and uppercase letters, increment score
            score += 1
        if score < 2:
            return False
        # If the password has been changed within the last second, the token is invalid.
        if (datetime.now() - self.password_list.last_changed).seconds < 1:
            current_app.logger.error('User {} tried to re-use a token.'.format(self.email))
            raise InvalidResetToken
        self.password = new_password
        self.password_list.update(self.password_hash)
        db.session.add(self)
        db.session.commit()
        return True

    def verify_password(self, password):
        """
        Checks user-entered passwords against hashes stored in the database.
        :param password: The user-entered password.
        :return: True if user has entered the correct password, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        """
        Checks to see if a user has access to certain permissions.
        :param permissions: An int that specifies the permissions we are checking to see whether or not the user has.
        :return: True if user is authorized for the given permission, False otherwise.
        """
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """
        Checks to see whether the user is an administrator.
        :return: True if the user is an administrator, False otherwise.
        """
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.email

    @staticmethod
    def generate_fake(count=100):
        """
        Used to generate fake users.
        """
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint

        import forgery_py
        seed()
        tag_count = Tag.query.count()
        for i in range(count):
            t = Tag.query.offset(randint(0, tag_count - 1)).first()
            first = forgery_py.name.first_name()
            last = forgery_py.name.last_name()
            e = (first[:1] + last + '@records.nyc.gov').lower()
            u = User(email=e,
                     password=forgery_py.lorem_ipsum.word(),  # change to set a universal password for QA testing
                     first_name=first,
                     last_name=last,
                     tag=t
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    """
    An anonymous user class to simplify user processes in other code.
    """

    @staticmethod
    def can(self, permissions):
        return False

    @staticmethod
    def is_administrator(self):
        return False


class Event(db.Model):
    """
    Model for clock events (in or out).
    """
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Boolean)  # True if clocking in, false if clocking out
    time = db.Column(db.DateTime)  # Time of clock in/out event
    note = db.Column(db.String(120))
    ip = db.Column(db.String(120))

    timepunch = db.Column(db.Boolean, default=False)
    # True if this is a timepunch request, false otherwise

    approved = db.Column(db.Boolean, default=True)
    # ^True if this is an approved timepunch request, false if
    # this is an unapproved timepunch request, Null otherwise

    pending = db.Column(db.Boolean, default=False)
    # True if this is a timepunch request that hasn't been approved or denied yet

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        if not self.note:
            self.note = ""
        in_or_out = "IN" if self.type else "OUT"
        time_string = self.time.strftime("%b %d, %Y %H:%M:%S %p")
        return time_string + " | " + self.user.email + " | " + in_or_out + " | " + self.note

    @staticmethod
    def generate_fake(count=100):
        """
        Generates fake event instances.
        :param count: Number of instances to generate
        :return: None.
        """
        from random import seed, randint
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            # u.clocked_in = not u.clocked_in
            e = Event(user=u,
                      time=datetime(
                          year=randint(2004, 2016),
                          month=randint(1, 6),
                          day=randint(1, 28),
                          hour=randint(0, 23),
                          minute=randint(0, 59),
                      )
                      )
            db.session.add_all([e, u])
            db.session.commit()


class Pay(db.Model):
    """
    A model for user pay rates.
    """
    __tablename__ = 'pays'
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Float)
    start = db.Column(db.Date)
    end = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return 'User: {} with rate {} from {} to {}'.format(self.user.email, self.rate, self.start, self.end)


class Tag(db.Model):
    """
    A model for different user tags.
    """
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='tag', lazy='dynamic')

    @staticmethod
    def insert_tags():
        tags = ['Intern', 'Contractor', 'SYEP', 'PENCIL', 'Employee', 'Volunteer', 'Other']
        for t in tags:
            tag = Tag.query.filter_by(name=t).first()
            if tag is None:
                tag = Tag(name=t)
            db.session.add(tag)
        db.session.commit()

    def __repr__(self):
        return '<Tag %r>' % self.name


class Password(db.Model):
    __tablename__ = 'passwords'
    id = db.Column(db.Integer, primary_key=True)
    p1 = db.Column(db.String(128))
    p2 = db.Column(db.String(128))
    p3 = db.Column(db.String(128))
    p4 = db.Column(db.String(128))
    p5 = db.Column(db.String(128))
    last_changed = db.Column(db.DateTime)
    users = db.relationship('User', backref='password_list', lazy='dynamic')

    def update(self, password_hash):
        self.p5 = self.p4
        self.p4 = self.p3
        self.p3 = self.p2
        self.p2 = self.p1
        self.p1 = password_hash
        self.last_changed = datetime.now()


class ChangeLog(db.Model):
    """
    A model that contains a list of changes made to a user account.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    changer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys=[user_id])
    changer = db.relationship('User', foreign_keys=[changer_id])
    timestamp = db.Column(db.DateTime)
    old = db.Column(db.String(128))
    new = db.Column(db.String(128))
    category = db.Column(db.String(128))


class Vacation(db.Model):
    """
    Model that stores vacation requests and status
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    approved = db.Column(db.Boolean, default=False)
    pending = db.Column(db.Boolean, default=True)


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
