from datetime import datetime
from flask import request

from sqlalchemy.ext.hybrid import hybrid_property

import hashlib
import uuid

from .main import db, ma, bcrypt, app


class CRUDModel(db.Model):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(64), default=str(uuid.uuid4()))
    __abstract__ = True

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if isinstance(record_id, (int, float)):
            return cls.query.get(int(record_id))
        return None

    @classmethod
    def get_by_public_id(cls, record_id):
        """Get record by ID."""
        if isinstance(record_id, str):
            return cls.query.filter_by(public_id=str(record_id)).first()
        return None

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()

def reference_col(tablename, nullable=False, pk_name="id", foreign_key_kwargs=None, column_kwargs=None):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return db.Column(
        db.ForeignKey("{0}.{1}".format(tablename, pk_name), **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs
    )

class User(CRUDModel):
    __tablename__ = "users"
    username = db.Column(db.String(64))
    email = db.Column(db.String(128))
    password_hash = db.Column(db.Binary(128))
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    jobs = db.relationship('Job', backref='driver', lazy='dynamic')
    avatar_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)
        if self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()


    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value):
        """Set password."""
        self.password_hash = bcrypt.generate_password_hash(value)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password_hash, value)

    def gravatar(self, size=150, default="identicon", rating="g"):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        return f'{url}/{self.avatar_hash}?s={size}&d={default}&r={rating}'

    def verify(self, password):
        return self.confirmed and self.check_password(password)

class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = ('public_id', 'username', 'last_active', 'avatar_hash', 'jobs', 'confirmed')
    jobs = ma.UrlFor('.get_user_jobs', id='<public_id>')

class UserSchemaMinimal(ma.Schema):
    class Meta:
        model = User
        fields = ('username', 'avatar_hash', 'last_active')
    jobs = ma.UrlFor('.get_user_jobs', id='<public_id>')


class Job(CRUDModel):
    __tablename__ = "jobs"
    number_of_people = db.Column(db.Integer, default=-1)
    _pickup_time = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(64), default="No Name")
    contact_number = db.Column(db.String(64), default="No Contact")
    time_allowed = db.Column(db.Integer, default=30)
    price = db.Column(db.Integer, default=0)
    is_complete = db.Column(db.Boolean, default=False)
    _driver_id = reference_col("users", nullable=True)

    pickup_house = db.Column(db.String(64))
    pickup_road = db.Column(db.String(64))
    pickup_village = db.Column(db.String(64))
    pickup_postcode = db.Column(db.String(64))

    dropoff_house = db.Column(db.String(64))
    dropoff_road = db.Column(db.String(64))
    dropoff_village = db.Column(db.String(64))
    dropoff_postcode = db.Column(db.String(64))

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)
        self.driver_id = None

    @hybrid_property
    def pickup_address(self):
        return {
            'house': self.pickup_house,
            'road': self.pickup_road,
            'village': self.pickup_village,
            'postcode': self.pickup_postcode,
        }
    @pickup_address.setter
    def pickup_address(self, value):
        self.pickup_house = value['house']
        self.pickup_road = value['road']
        self.pickup_village = value['village']
        self.pickup_postcode = value['postcode']

    @hybrid_property
    def dropoff_address(self):
        return {
            'house': self.dropoff_house,
            'road': self.dropoff_road,
            'village': self.dropoff_village,
            'postcode': self.dropoff_postcode,
        }
    @dropoff_address.setter
    def dropoff_address(self, value):
        self.dropoff_house = value['house']
        self.dropoff_road = value['road']
        self.dropoff_village = value['village']
        self.dropoff_postcode = value['postcode']

    @hybrid_property
    def pickup_time(self):
        return self._pickup_time

    @pickup_time.setter
    def pickup_time(self, value):
        """Set password."""
        self._pickup_time = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")

    @hybrid_property
    def driver_id(self):
        if self.driver:
            return self.driver.public_id
        else:
            return None

    @driver_id.setter
    def driver_id(self, value):
        """Set the driver for a job"""
        if value is not None:
            driver = User.get_by_public_id(value)
            self.driver = driver

class JobSchema(ma.ModelSchema):
    class Meta:
        model = Job
        fields = ('public_id', 'number_of_people', 'pickup_time', 'name', 'contact_number', 'time_allowed', 'price', 'is_complete', 'driver', 'dropoff_address', 'pickup_address')
    
    driver = ma.Nested(UserSchemaMinimal)
