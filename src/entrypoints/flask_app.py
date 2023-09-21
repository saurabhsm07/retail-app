from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters import orm
from adapters.repository import BatchRepository
from domain.models.order_line import OrderLine
from domain.models.batch import OutOfStockException
from service_layer.services import allocate, InvalidSkuException
from config import get_db_url

orm.start_mappers()

get_session = sessionmaker(bind=create_engine(get_db_url()))

app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()

    order_line = OrderLine(request.json['order_id'], request.json['sku'], request.json['qty'])

    try:
        batch_ref = allocate(order_line, BatchRepository(session), session)
    except OutOfStockException as e:
        return jsonify({'message': str(e)}), 400
    except InvalidSkuException as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batch_ref': batch_ref}), 201
