from flask import Flask, make_response, abort, g
from config import db
from models import Product, ProductSchema, User, UserSchema, Subscription, List
from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


def read_all():
    
    # Create the list of products from our data
    products = Product.query.order_by(Product.idproduct).all()

    # Serialize the data for the response
    product_schema = ProductSchema(many=True)
    data = product_schema.dump(products)
    return data

@auth.login_required
def read_from_list(list_id):
    
    # Create the list of products from our data
    subscription = Subscription.query.filter(Subscription.user_user_id == g.user.user_id)\
        .filter(Subscription.list_list_id == list_id).one_or_none()

    lists = List.query.filter(List.user_user_id == g.user.user_id)\
        .filter(List.list_id == list_id).one_or_none()

    if(subscription is None and lists is None ): return 404

    products = Product.query.order_by(Product.idproduct).filter(Product.list_list_id == list_id).all()

    # Serialize the data for the response
    product_schema = ProductSchema(many=True)
    data = product_schema.dump(products)
    return data

#def most_recent(list_id, user_id):

 #   product = session.query(User).filter(User.name.like('e%')).\


@auth.verify_password
def verify_password(email, password):
    user = User.query.filter(User.email == email).one_or_none()
    if not user or not User.verify_password(email, password):
        return False
    g.user = user
    return True     


@auth.login_required
def create(product):
    
    subscription = Subscription.query.filter(Subscription.user_user_id == g.user.user_id)\
        .filter(Subscription.list_list_id == product.get("list_list_id")).one_or_none()

    lists = List.query.filter(List.user_user_id == g.user.user_id)\
        .filter(List.list_id == product.get("list_list_id")).one_or_none()

    if(subscription is None and lists is None ): return 404
    
    
    name = product.get("name")

    schema = ProductSchema()
    new_product = schema.load(product, session=db.session)

    db.session.add(new_product)
    db.session.commit()

    data = schema.dump(new_product)

    return data, 201


@auth.login_required
def update(idproduct, product):

    if(idproduct != product.idproduct): return 400

    subscription = Subscription.query.filter(Subscription.user_user_id == g.user.user_id)\
        .filter(Subscription.list_list_id == product.get("list_list_id")).one_or_none()

    lists = List.query.filter(List.user_user_id == g.user.user_id)\
        .filter(List.list_id == product.get("list_list_id")).one_or_none()

    if(subscription is None and lists is None ): return 404

    update_product = Product.quert.filter(
        Product.idproduct == idproduct
    ).one_or_none()

    name = product.get("name")

    existing_product = (
        Product.query.filter(Product.name == name)
        .one_or_none()
    )

    if update_product is None:
        abort(
            404,
            "Product not found for Id: {idproduct}".format(idproduct=idproduct),
        )

    else:

       schema = ProductSchema()
       update = schema.load(product, session=db.session).data
       
       update.idproduct = update_product.idproduct

       db.session.merge(update)
       db.session.commit()

       data = schema.dump(update_product).data
        

       return data,200

@auth.login_required
def delete(idproduct):

    product = Product.query.filter(Product.idproduct == idproduct).one_or_none()


    if product is not None:
        db.session.delete(product)
        db.session.commit()
        return make_response(
            "Product {idproduct} deleted".format(idproduct=idproduct), 200
        )

    else:
        abort(
            404,
            "Product not found for Id: {idproduct}".format(idproduct=idproduct),
        )

@auth.login_required
def bought_procedure(list_id):

    #db.session.execute("CALL bought(:param)", param=list_id)
    #db.session.execute('bought :p1', {'p1':list_id})
    #db.session.execute(func.bought(list_id))

    subscription = Subscription.query.filter(Subscription.user_user_id == g.user.user_id)\
        .filter(Subscription.list_list_id == list_id).one_or_none()

    lists = List.query.filter(List.user_user_id == g.user.user_id)\
        .filter(List.list_id == list_id).one_or_none()

    if(subscription is None and lists is None ): return 404

    try:
        statement = "CALL bought("+str(list_id)+");"
        db.session.execute("START TRANSACTION;")
        db.session.execute(statement)
        db.session.execute("COMMIT;")
    except Exception as inst:
        print (type(inst))

    return 204

@auth.login_required
def to_buy_procedure(list_id):
    #db.session.execute("CALL toBuy(:param)", param=list_id)

    subscription = Subscription.query.filter(Subscription.user_user_id == g.user.user_id)\
        .filter(Subscription.list_list_id == list_id).one_or_none()

    lists = List.query.filter(List.user_user_id == g.user.user_id)\
        .filter(List.list_id == list_id).one_or_none()

    if(subscription is None and lists is None ): return 404



    try:
        statement = "CALL toBuy("+str(list_id)+");"
        db.session.execute("START TRANSACTION;")
        db.session.execute(statement)
        db.session.execute("COMMIT;")
    except Exception as inst:
        print (type(inst))

    return 204

def advert():
    '''
    user = User.query.filter(User.user_id == user_id).one_or_none()
    lists = List.query.filter(List.list_id == list_id).one_or_none()

    products = Product.query.filter(Product.user_user_id == user.user_id)\
        .filter(Product.list_list_id == lists.list_id).all()

    q = db.session.query(User).join(Product).on(Product.user_user_id == User.user_id).\
        filter(User.username.like('e%'))

    q = q.add_entity(User).from_self().\
        options(contains_eager(User.username))

    '''

    q = (db.session.query(User.email, Product.name))\
        .join(List, List.user_user_id == User.user_id)\
        .join(Product, User.user_id == Product.user_user_id)\
        .group_by(User.user_id, Product.idproduct)

    resultlist = []
    for username, name in q:
        resultlist.append({'username': username, 'name': name})

    return resultlist

def most_recent(list_id):

    #x = aliased(Product)
    #s = db.session.query(x.name).filter(x.create_time == func.max(Product.create_time)).label("name")
    #s = db.session.select(Product.name).from(Product p2).where(p2.create_time == func.max(Product.create_time))
    """q = (db.session.query(User.email, Product.name,\
        func.max(Product.create_time)))\
        .filter(Product.list_list_id == list_id)\
        .filter(Product.create_time == func.max(Product.create_time))\
        .join(Product, User.user_id == Product.user_user_id)\
        .group_by(User.user_id, Product.idproduct)
    """
    #db.session.execute("START TRANSACTION;")
    q = (db.session.query(User.username, Product.name, Product.create_time))\
        .join(User, User.user_id == Product.user_user_id)\
        .filter(Product.list_list_id == list_id)\
        .group_by(User.user_id, Product.idproduct)\
        .order_by(Product.create_time.desc()).limit(1)
    #db.session.execute("COMMIT;")

    
    resultlist = []
    for username, name, create_time in q:
       resultlist.append({'username': username, 'name': name, 'create_time': create_time})

    return resultlist

