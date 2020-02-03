from flask import make_response, abort, g
from config import db
from models import Subscription, SubscriptionSchema, User, List

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

    subscriptions = Subscription.query.order_by(Subscription.list_list_id).all()

    # Serialize the data for the response
    subscription_schema = SubscriptionSchema(many=True)
    data = subscription_schema.dump(subscriptions)
    return data


@auth.login_required
def read_users_subscriptions(user_id):
    if(g.user.user_id == user_id):
        subscriptions = Subscription.query.filter(Subscription.user_user_id == user_id).all()

    #print('tescik = ', list)


        subscription_schema = SubscriptionSchema(many=True)
        data = subscription_schema.dump(subscriptions)
        return data
    else: return 404
    
@auth.login_required
def create(subscription):
    
    #user_id = subscription.get("user_user_id")
    lists = List.query.filter(List.user_user_id == g.user.user_id)\
        .filter(List.list_id == subscription.get("list_list_id")).one_or_none()
    if(lists is None): return 404
    list_id = subscription.get("list_list_id")

    existing_subscription = Subscription.query \
        .filter(Subscription.user_user_id == subscription.get("user_id")) \
        .filter(Subscription.list_list_id == subscription.get("list_id")) \
        .one_or_none()

    if existing_subscription is None:

        schema = SubscriptionSchema()
        new_subscription = schema.load(subscription, session=db.session)

        db.session.add(new_subscription)
        db.session.commit()

        return schema.dump(new_subscription), 201

    else:
        abort(409, f'Subscription already exists')

@auth.login_required
def delete(user_id, list_id):


    #subscription = Subscription.query.filter(Subscription.user_user_id == g.user.user_id)\
     #   .filter(Subscription.list_list_id == list_id).one_or_none()


    lists = List.query.filter(List.user_user_id == g.user.user_id)\
        .filter(List.list_id == list_id).one_or_none()

    #if(subscription is None and lists is None ): return 404
    #if(subscription is None and lists is not None)

    subscription = Subscription.query.filter(Subscription.user_user_id == user_id)\
    .filter(Subscription.list_list_id == list_id)\
    .one_or_none()

    if (user_id != g.user.user_id and lists is None): return 404


    if subscription is not None:
        db.session.delete(subscription)
        db.session.commit()
        return make_response(
            "Subscription deleted", 200
        )

    else:
        abort(
            404,
            "Subscription not found",
        )


