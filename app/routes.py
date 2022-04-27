from app.models import *
from app import app, db
from app.utils import make_response
from flask_cors import cross_origin
from sqlalchemy.sql import func
import pandas as pd
import numpy as np


@app.route("/", methods=["GET"])
@cross_origin()
def index():
    return make_response(dict(name="any"))


@app.route("/add-user", methods=["POST"])
@cross_origin()
def add_user():
    try:
        user_code = request.get_json(force=True).get("userId")
        user = User(user_code)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return make_response(dict(stauts="FAIL", detail=str(e)))
    return make_response(dict(status="SUCCESS"))


@app.route("/add-product", methods=["POST"])
@cross_origin()
def add_product():
    try:
        product_code = request.get_json(force=True).get("productId")
        product = Product(product_code)
        db.session.add(product)
        db.session.commit()
    except Exception as e:
        return make_response(dict(stauts="FAIL", detail=str(e)))
    return make_response(dict(status="SUCCESS"))


@app.route("/add-order", methods=["POST"])
@cross_origin()
def add_order():
    try:
        data = request.get_json(force=True)
        user_code = data.get("userId")
        product_code = data.get("productId")
        rating = int(data.get("rating"))
        order = Order(user_code, product_code, rating)
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        return make_response(dict(stauts="FAIL", detail=str(e)))
    return make_response(dict(status="SUCCESS"))


@app.route("/get-recommendation/<path:query_user_code>", methods=["GET"])
@cross_origin()
def get_recommendation(query_user_code: str):

    try:
        order = (
            db.session.query(
                Order.user_code, Order.product_code, func.avg(Order.rating).label("rating")
            )
            .group_by(Order.user_code, Order.product_code)
            .all()
        )

        order = [dict(item) for item in order]
        order = pd.DataFrame(order)

        query = order[order.user_code == query_user_code].drop('user_code', axis=1)
        query = query.sort_values(by='rating', ascending=False).head(10)
        recommend = query['product_code'].values.tolist()

        # list_user_code = order["user_code"].unique()
        # list_product_code = order["product_code"].unique()

        # user_item = np.zeros((len(list_user_code), len(list_product_code)))
        # for user_idx, user_code in enumerate(list_user_code):
        #     for item_idx, product_code in enumerate(list_product_code):
        #         user_item[user_idx, item_idx] = order[
        #             (order.user_code == user_code) & (order.product_code == product_code)
        #         ].rating.values[0]

        # idx = np.where(list_user_code == query_user_code)[0][0]
        # user_item[]
    except Exception as e:
        return make_response(dict(stauts="FAIL", detail=str(e)))

    return make_response(dict(status="SUCCESS", list_product_recommend_id=recommend))
