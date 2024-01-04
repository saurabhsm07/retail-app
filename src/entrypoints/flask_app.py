from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters import orm
from adapters.repository import BatchRepository, OrderLineRepository, ProductRepository
from domain.models.order_line import OrderLine
from domain.models.product import OutOfStockException
from service_layer.services import allocate, InvalidSkuException, deallocate
from config import get_db_url

orm.start_mappers()

get_session = sessionmaker(bind=create_engine(get_db_url()))

app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()

    order_line = OrderLine(request.json['order_id'], request.json['sku'], request.json['qty'])

    try:
        batch_ref = allocate(order_line, ProductRepository(session), session)
    except OutOfStockException as e:
        return jsonify({'message': str(e)}), 400
    except InvalidSkuException as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batch_ref': batch_ref}), 201


@app.route('/deallocate', methods=["get"])
def deallocate_endpoint():
    session = get_session()

    order_id = request.args.get('order_id')
    sku = request.args.get('sku')
    qty = int(request.args.get('qty'))
    batch_ref = request.args.get('batch_ref')

    try:
        status = deallocate(batch_ref, OrderLine(order_id, sku, qty), ProductRepository(session), session)

        if status:
            return jsonify({'message': f'Order line of order : {order_id}'
                                       f'successfully deallocated from batch : {batch_ref}'}), 204
        else:
            return jsonify({'message': f'cannot deallocate unallocated order line'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'message': str(e)}), 400
