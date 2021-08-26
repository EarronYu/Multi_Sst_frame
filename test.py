import pandas as pd
pd.set_option('display.max_columns', None)
ETHUSDT_df = pd.read_hdf('data//Raishiz_15m_4h_indicator.h5', key='ETHUSDT', mode='a')
ETHUSDT_df = pd.DataFrame(ETHUSDT_df)
ETHUSDT_df.drop(ETHUSDT_df.index)
ETHUSDT_df.to_hdf('data//Raishiz_15m_4h_indicator.h5', key='ETHUSDT', mode='w')
DOGEUSDT_df = pd.read_hdf('data//Raishiz_15m_4h_indicator.h5', key='DOGEUSDT', mode='a')
DOGEUSDT_df = pd.DataFrame(DOGEUSDT_df)
DOGEUSDT_df.drop(DOGEUSDT_df.index)
ETHUSDT_df.to_hdf('data//Raishiz_15m_4h_indicator.h5', key='DOGEUSDT', mode='w')
print(ETHUSDT_df)
print(DOGEUSDT_df)

import ccxt
import json
import yaml
import time
import pandas as pd
from decimal import Decimal
from datetime import datetime


# yaml_path = 'data//settings.yaml'
# with open(yaml_path, 'r') as f:
#     st = f.read()
#     data = yaml.load(st, Loader=yaml.FullLoader)
#     f.close()
# # 配置信息
# default_reduce_rate = data['default_reduce_rate']
# pin = data['pin']
# test_info = data['test_info']
# binance_order_types = data['binance_order_types']
# BINANCE_CONFIG = data['BINANCE_CONFIG']
# exchange = ccxt.binance(BINANCE_CONFIG)
# exchange.set_sandbox_mode(True)
# response = exchange.fapiPrivateGetAccount()
# # print(response)
#
#
# def usdt_future_exchange_info(symbol):
#     """
#     获取交易币种的最小下单价格、数量精度
#     """
#     exchange_info = exchange.fapiPublicGetExchangeinfo()
#     # 转化为dataframe
#     df = pd.DataFrame(exchange_info['symbols'])
#     df = df[['symbol', 'pricePrecision', 'quantityPrecision']]
#     df.set_index('symbol', inplace=True)
#     price_precision = int(df.at[symbol, 'pricePrecision'])
#     quantity_precision = df.at[symbol, 'quantityPrecision']
#     # symbol_temp[symbol]['最小下单量精度'] = None if p == 0 else int(p)
#     return price_precision, quantity_precision
#
#
# def modify_order_quantity(symbol, quantity):
#     """
#     根据交易所的精度限制（最小下单单位、量等），修改下单的数量和价格
#     """
#     # 根据每个币种的精度，修改下单数量的精度
#     # 获取每个币对的精度
#     price_precision, quantity_precision = usdt_future_exchange_info(symbol)
#     quantity_precision = '%.0{}f'.format(quantity_precision) % 0
#     quantity = Decimal(quantity).quantize(Decimal(f'{quantity_precision}'))
#     return quantity
#
#
# def post_order(symbol, signal_type, quantity):
#     """
#     发送订单, 处理交易所响应
#     """
#     order = \
#         {
#             'symbol': symbol,
#             'side': binance_order_types[signal_type]['side'],
#             'positionSide': binance_order_types[signal_type]['positionSide'],
#             'quantity': modify_order_quantity(symbol, quantity),
#             'type': 'MARKET',
#             'newOrderRespType': 'RESULT',
#             'timestamp': int(time.time() * 1000)
#         }
#     order['quantity'] = str(order['quantity'])
#     order = exchange.fapiPrivatePostOrder(order)
#     status = order['status']
#     orderId = order['orderId']
#     avgPrice = order['avgPrice']
#     executedQty = order['executedQty']
#     rec01 = f'{status} Order : # {orderId} #'
#     rec02 = f'Executed Quantity {executedQty} at {avgPrice}'
#     print('Order_Info'.center(110))
#     print(f'{rec01}'.center(110))
#     print(f' {rec02}'.center(110))
#     return order
#
#
# post_order('ETHUSDT', 'reduce_LONG', '1.200')
# print(dir(ccxt.binance()))
