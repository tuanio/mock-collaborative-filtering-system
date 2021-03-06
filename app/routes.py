from app.models import *
from app import app, db
from app.utils import make_response
from flask_cors import cross_origin
from sqlalchemy.sql import func
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


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

        list_user_code = order["user_code"].unique()
        list_product_code = order["product_code"].unique()

        user_item = np.zeros((len(list_user_code), len(list_product_code)))
        for user_idx, user_code in enumerate(list_user_code):
            for item_idx, product_code in enumerate(list_product_code):
                user_item[user_idx, item_idx] = order[
                    (order.user_code == user_code) & (order.product_code == product_code)
                ].rating.values[0]

        # ma tr???n similarity (len user) x (len user)
        similarity_matrix = cosine_similarity(user_item)

        # t??m index c???a user theo id
        user_idx = np.where(list_user_code == query_user_code)[0][0]
        
        list_product_recommendation = []
        # l???p qua t???t c??? s???n ph???m hi???n c??
        for product_idx, product_code in enumerate(list_product_code):
            # t??m t???t c??? user ???? rate s???n ph???m ????
            user_rated_product = np.where(user_item[:, product_idx] > 0)[0]
            # n???u user hi???n t???i ???? rate th?? b??? ra
            user_rated_product = user_rated_product[user_rated_product != user_idx]

            # t??m c??c h??? s??? t????ng quan gi???a user mong mu???n v?? t???t c??? user ???? rate
            sim = similarity_matrix[user_idx, user_rated_product]
            sim = sim[sim < 1] # lo???i b??? gi?? tr??? c?? t????ng quan l?? 1, v?? n?? t????ng quan v???i ch??nh n??
            rating = user_item[user_rated_product, product_idx] # l???y list rating c???a nh???ng user ???? rate

            # t??nh h??? s??? rating d??? ??o??n, t???ng tr???ng s??? gi???a rating v?? ????? t????ng quan
            r = (rating * sim).sum() / sim.sum()

            # ????a v??o tuple (product id, rating) -> t?? n???a s???p x???p gi???m d???n
            list_product_recommendation.append((product_code, r))

        # s???p x???p gi???m d???n theo rating d??? ??o??n
        list_product_recommendation = sorted(list_product_recommendation, key=lambda x: x[1], reverse=True)
        list_product_recommendation = [pack[0] for pack in list_product_recommendation]

    except Exception as e:
        return make_response(dict(stauts="FAIL", detail=str(e)))

    return make_response(dict(status="SUCCESS", list_product_recommend_id=list_product_recommendation))
