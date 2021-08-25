# import pandas as pd
# pd.set_option('display.max_columns', None)
# ETHUSDT_df = pd.read_hdf('data//Raishiz_15m_4h_indicator.h5', key='ETHUSDT', mode='a')
# ETHUSDT_df = pd.DataFrame(ETHUSDT_df)
# ETHUSDT_df.drop(ETHUSDT_df.index)
# ETHUSDT_df.to_hdf('data//Raishiz_15m_4h_indicator.h5', key='ETHUSDT', mode='w')
# DOGEUSDT_df = pd.read_hdf('data//Raishiz_15m_4h_indicator.h5', key='DOGEUSDT', mode='a')
# DOGEUSDT_df = pd.DataFrame(DOGEUSDT_df)
# DOGEUSDT_df.drop(DOGEUSDT_df.index)
# ETHUSDT_df.to_hdf('data//Raishiz_15m_4h_indicator.h5', key='DOGEUSDT', mode='w')
# print(ETHUSDT_df)
# print(DOGEUSDT_df)

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
def modify_decimal(n):
    """
    快速调用的将小数做Decimal处理的小功能
    """
    n = float(n)
    n = Decimal(n).quantize(Decimal("0.000"))
    return n


def intTodatetime(intValue):
    intValue = int(intValue)
    if len(str(intValue)) == 10:
        # 精确到秒
        timeValue = time.localtime(intValue)
        tempDate = time.strftime("%Y-%m-%d %H:%M:%S", timeValue)
        datetimeValue = datetime.strptime(tempDate, "%Y-%m-%d %H:%M:%S")
    elif 10 < len(str(intValue)) < 15:
        # 精确到毫秒
        k = len(str(intValue)) - 10
        timestamp = datetime.fromtimestamp(intValue / (1 * 10 ** k))
        datetimeValue = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        return -1
    return datetimeValue


def trading_record(order, strategy, symbol, time_period, signal_type):
    """
    目前功能暂时用于记录allocated_funds的变化, 通过获取的交易所响应, 计算当前订单的realized_PNL信息
    """
    quantity = order['executedQty']
    price = order['avgPrice']
    order_time = order['updateTime']
    side = order['side']
    order_time = intTodatetime(order_time)
    # record = pd.read_csv('data//trading_record.csv')
    # record = pd.DataFrame(record)
    df = \
        {
            'order_time': [f'{order_time}'],
            'strategy': [f'{strategy}'],
            'symbol': [f'{symbol}'],
            'time_period': [f'{time_period}'],
            'side': [f'{side}'],
            'Price': [f'{price}'],
            'quantity': [f'{quantity}']
        }
    df = pd.DataFrame(df).astype(str)
    df.set_index('order_time', inplace=True)
    df.index = pd.DatetimeIndex(df.index)
    # record.append(df)
    df.to_csv('data//trading_record.csv')


def processing_record(strategy, symbol, time_period):
    """
    通过record来计算PNL和allocated_funds
    """
    record = pd.read_csv('data//trading_record.csv')
    df = pd.DataFrame(record).astype(str)
    # df = record.query(f"'strategy'=='{strategy}' and 'symbol'=='{symbol}' and 'time_period'=='{time_period}'")
    df = record[(df[u'strategy'] == f'{strategy}') & (df[u'symbol'] == f'{symbol}') & (df[u'time_period'] == f'{time_period}')]
    df.set_index(df['order_time'])
    if len(df.index) >= 2:
        n_record = df.loc[df.index[-1]]
        o_record = df.loc[df.index[-2]]
        n_funds = Decimal(n_record['quantity']) * Decimal(n_record['Price']) * Decimal(0.9996)
        o_funds = Decimal(o_record['quantity']) * Decimal(n_record['Price']) * Decimal(0.9996)
        pnl = n_funds - o_funds
        trade_info = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
        trade_info = pd.DataFrame(trade_info).astype(str)
        trade_info.loc[f'{time_period}', 'period_allocated_funds'] += pnl
        trade_info = trade_info.astype(str)
        trade_info.to_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
    else:
        n_record = df.loc[df.index[-1]]
        n_funds = Decimal(n_record['quantity']) * Decimal(n_record['Price']) * Decimal(0.9996)
        trade_info = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
        trade_info = pd.DataFrame(trade_info).astype(str)
        print(trade_info)
        o_funds = trade_info.loc[f'{time_period}', 'period_allocated_funds']
        o_funds = modify_decimal(o_funds)
        funds = (o_funds - n_funds) + n_funds * Decimal('0.9996')
        n = trade_info.loc[f'{time_period}', 'period_allocated_funds']
        n = modify_decimal(n)
        n *= Decimal(funds).quantize(Decimal('0.000'))
        trade_info.loc[f'{time_period}', 'period_allocated_funds'] = n
        trade_info = trade_info.astype(str)
        trade_info.to_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')


order = {'orderId': '778904829', 'symbol': 'ETHUSDT', 'status': 'FILLED', 'clientOrderId': 'fwAnJlb9DCtycGCgM8OJm2', 'price': '0', 'avgPrice': '3135.44000',
         'origQty': '4.678', 'executedQty': '4.678', 'cumQty': '4.678', 'cumQuote': '14667.58832', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False,
         'closePosition': False, 'side': 'SELL', 'positionSide': 'SHORT', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False,
         'origType': 'MARKET', 'updateTime': '1629893420176'}
strategy = 'Raishiz_15m_4h_indicator'
symbol = 'ETHUSDT'
time_period = '30m'
signal_type = 'open_LONG'
trading_record(order, strategy, symbol, time_period, signal_type)
processing_record(strategy, symbol, time_period)
