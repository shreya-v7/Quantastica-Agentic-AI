from ai.app.agents.trade_execution.trade_execution_agent.subagents.cancel_order_agent.cancel_order_tool import \
    cancel_order_by_id
from ai.app.agents.trade_execution.trade_execution_agent.subagents.place_order_agent.place_order_tool import place_order
from ai.app.agents.trade_execution.trade_execution_agent.subagents.update_order_agent.update_order_tool import update_order

app = Flask(__name__)

@app.route('/place_order', methods=['POST'])
def place_order_api():
    data = request.json
    try:
        response = place_order(
            symbol=data['symbol'],
            qty=data['qty'],
            side=data['side'],
            order_type=data['order_type'],
            limit_price=data.get('limit_price'),
            stop_price=data.get('stop_price')
        )
        return jsonify({'message': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/update_order', methods=['PUT'])
def update_order_api():
    data = request.json
    try:
        response = update_order(
            symbol=data['symbol'],
            new_qty=data['new_qty'],
            new_price=data.get('new_price'),
            order_type=data.get('order_type', 'market')
        )
        return jsonify({'message': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/cancel_order', methods=['DELETE'])
def cancel_order_api():
    data = request.json
    try:
        response = cancel_order_by_id(order_id=data.get('order_id'))
        return jsonify({'message': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
