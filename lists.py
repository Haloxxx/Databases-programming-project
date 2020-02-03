from flask import make_response, abort, g
from config import db
from models import List, ListSchema, User

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email, password):
    user = User.query.filter(User.email == email).one_or_none()
    if not user or not User.verify_password(email, password):
        return False
    g.user = user
    return True   



def read_all():

    lists = List.query.order_by(List.list_id).all()

    # Serialize the data for the response
    list_schema = ListSchema(many=True)
    data = list_schema.dump(lists)
    return data

@auth.login_required
def read_users_lists(user_id):

    lists = List.query.filter(List.user_user_id == user_id).all()

    #print('tescik = ', list)

    
    list_schema = ListSchema(many = True)
    data = list_schema.dump(lists)
    return data

    
@auth.login_required
def create(list):

    if(g.user.user_id != list.get("user_user_id")): return 404
    
    name = list.get("list")
    user_id = list.get("user_user_id")

    existing_list = List.query \
        .filter(List.user_user_id == user_id) \
        .filter(List.name == name) \
        .one_or_none()

    if existing_list is None:

        schema = ListSchema()
        new_list = schema.load(list, session=db.session)

        db.session.add(new_list)
        db.session.commit()

        return schema.dump(new_list), 201

    else:
        abort(409, f'List {name} already exists')

@auth.login_required
def update(list_id, list):

    if(g.user.user_id != list.get("user_user_id")): return 404

    update_list = List.query.filter(
        List.list_id == list_id
    ).one_or_none()

    name = list.get("list")
    user_id = list.get("user_user_id")

    existing_list = List.query \
        .filter(List.user_user_id == user_id) \
        .filter(List.name == name) \
        .one_or_none()

    if update_list is None:
        abort(
            404,
            "List not found for Id: {list_id}".format(list_id=list_id),
        )

    elif (
        existing_list is not None and existing_list.list_id != list_id
    ):
        abort(
            409,
            "List {name} exists already".format(
                name=name
            ),
        )

@auth.login_required
def delete(list_id):

    list = List.query.filter(List.list_id == list_id).one_or_none()

    if(g.user.user_id != list.get("user_user_id")): return 404


    if list is not None:
        db.session.delete(list)
        db.session.commit()
        return make_response(
            "List {list_id} deleted".format(list_id=list_id), 200
        )

    else:
        abort(
            404,
            "List not found for Id: {list_id}".format(list_id=list_id),
        )
    