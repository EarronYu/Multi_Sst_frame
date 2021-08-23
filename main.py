"""
通过这个模块能够开放主机上的5000端口, 并且接收tradingview传来的post信息
"""
# Yes?

from functions import *
from flask import Flask, request, abort
import ast
import hashlib


# 建立flask app
app = Flask(__name__)


# Create root to easily let us know its on/working.
@app.route('/')
def root():
    return 'RICH'


def parse_webhook(webhook_data):
    """
    这个函数可以将tradingview的json信息转为dict
    """
    data = ast.literal_eval(webhook_data)
    # print('parse_webhook收到信息: ' + 'signal: ' + data['signal'] + '返回给webhook处理')
    return data


def get_token():
    token = hashlib.sha224(pin.encode('utf-8'))
    return token.hexdigest()


def processing_signal(strategy, symbol, time_period, signal_type):
    check_signal(strategy, symbol, time_period)
    update_allocation_statistics(strategy, symbol, time_period)
    processing_trading_action(strategy, symbol, time_period, signal_type)


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    建立出来一个叫做webhook的位置, 专门接收post信息并分拣到不同symbol以及不同time_period
    """
    if request.method == 'POST':
        # Parse the string data from tradingview into a python dict
        data = parse_webhook(request.get_data(as_text=True))  # 将接收到的信息交给action中的parse_webhook函数处理, return给data
        # Check that the key is correct
        if data["signal_type"] == 'schedule_sync':
            schedule_sync()
        if get_token() == data['key']:  # 如果get_token返回来的值等于data数据容器中的'key', 向下执行
            strategy = data["strategy"]
            symbol = data["symbol"]
            time_period = data["time_period"]
            signal_type = data["signal_type"]
            if 'remove' in (strategy + symbol + time_period):
                msg = f'Removing {strategy} {symbol} {time_period}'
                L = len(msg)
                print('>' * 5 + '=' * L + '<' * 5)
                print(msg.center(L + 10))
                print('Processing...'.center(L + 10))
                remove(strategy, symbol, time_period)
                print('Completed!'.center(L + 10))
            else:
                msg = f'Received Trading Information: {strategy} {symbol} {time_period} {signal_type} Signal'
                L = len(msg)
                print('>' * 5 + '=' * L + '<' * 5)
                print(msg.center(L + 10))
                print('Processing...'.center(L + 10))
                processing_signal(strategy, symbol, time_period, signal_type)
                print('Completed!'.center(L + 10))
                print('>' * 5 + '=' * L + '<' * 5)
            return 200
        else:
            abort(403)
    else:
        abort(400)


if __name__ == '__main__':
    app.run()
