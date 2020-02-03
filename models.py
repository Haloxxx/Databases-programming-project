from datetime import datetime
from config import db, ma
import hashlib
from hmac import compare_digest\


class Product(db.Model):
    __tablename__ = "product"
    idproduct = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    create_time = db.Column(
        db.DateTime, default=datetime.utcnow
    )
    last_change = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    status = db.Column(db.String(10), default = 'toBuy')
    list_list_id = db.Column(db.Integer)
    user_user_id = db.Column(db.Integer)


class ProductSchema(ma.ModelSchema):
    class Meta:
        model = Product
        sqla_session = db.session

class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16))
    email = db.Column(db.String(255))
    password = db.Column(db.String(40))
    create_time = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def hash_password(self, password):
        ps = hashlib.sha1()
        password = str(password).encode('utf-8')
        ps.update(password)
        return ps.hexdigest().encode('utf-8')

    def verify_password(email, password):
        user = User.query.filter(User.email == email).one_or_none()
        ps = hashlib.sha1()
        password = password.encode('utf-8')
        ps.update(password)
        ooo = ps.hexdigest().encode('utf-8')
        return compare_digest(str.encode(user.password), ooo)

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        sqla_session = db.session

class List(db.Model):
    __tablename__ = "list"
    list_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    user_user_id = db.Column(db.Integer)

class ListSchema(ma.ModelSchema):
    class Meta:
        model = List
        sqla_session = db.session

class Subscription(db.Model):
    __tablename__ = "subscription"
    user_user_id = db.Column(db.Integer, primary_key=True)
    list_list_id = db.Column(db.Integer, primary_key=True)

class SubscriptionSchema(ma.ModelSchema):
    class Meta:
        model = Subscription
        sqla_session = db.session

"""
class UsersDemand(db.Model):
    username = db.Column(db.String(16))
    name = db.Column(db.String(30))

class UsersDemandSchema(ma.ModelSchema):
    class Meta:
        model = UsersDemand
        sqla_session = db.session
"""