from flask import make_response, abort
from config import db
from models import User, UserSchema

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    user = User.query.filter(User.email == email).one_or_none()
    if not user or not User.verify_password(email, password):
        return False
    #g.user = user
    return True   



def read_all():
    """
    This function responds to a request for /api/people
    with the complete lists of people
    :return:        json string of list of people
    """
    # Create the list of products from our data
    users = User.query.order_by(User.user_id).all()

    # Serialize the data for the response
    user_schema = UserSchema(many=True)
    data = user_schema.dump(users)
    return data

def log_in(user):
    email = user.get("email")
    password = user.get("password")

    target = User.query.filter(User.email == email) \
        .filter(User.password == SHA1(password)) \
        .one_or_none()

    data = user_schema.dump(target)
    return data

def create(user):
    email = user.get("email")

    existing_user = User.query \
        .filter(User.email == email) \
        .one_or_none()

    if existing_user is None:
        
        schema = UserSchema()
        new_user = schema.load(user, session=db.session)
        new_user.password = new_user.hash_password(new_user.password)
        db.session.add(new_user)
        db.session.commit()

        return schema.dump(new_user), 201

    else:
        abort(404)

    

@auth.login_required
def update(user_id, user):

    update_user = User.query.filter(
        User.user_id == user_id
    ).one_or_none()

    email = user.get("email")

    existing_user = User.query \
        .filter(User.email == email) \
        .one_or_none()

    if update_user is None:
        abort(
            404
            #"User not found for Id: {user_id}".format(user_id=user_id),
        )

    elif (
        existing_user is not None and existing_user.user_id != user_id
    ):
        abort(
            404
        )

    else:

       schema = UserSchema()
       update = schema.load(user, session=db.session)
       
       update.user_id = update_user.user_id

       db.session.merge(update)
       db.session.commit()

       data = schema.dump(update_user)
        

       return data,200

@auth.login_required
def delete(user_id):

    user = User.query.filter(User.user_id == user_id).one_or_none()


    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return make_response(
            "User {user_id} deleted".format(user_id=user_id), 200
        )

    else:
        abort(
            404,
            "Product not found for Id: {user_id}".format(user_id=user_id),
        )


