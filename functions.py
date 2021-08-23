import pandas as pd
from decimal import Decimal
import ccxt
import yaml
import json
import time
import h5py


pd.set_option('display.max_rows', 1000)
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.unicode.ambiguous_as_wide', True)  # 设置命令行输出时的列对齐功能
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)
pd.set_option('mode.chained_assignment', None)


# 从配置文件中加载各种配置
yaml_path = 'data//settings.yaml'
with open(yaml_path, 'r') as f:
    st = f.read()
    data = yaml.load(st, Loader=yaml.FullLoader)
    f.close()
# 配置信息
default_reduce_rate = data['default_reduce_rate']
pin = data['pin']
test_info = data['test_info']
binance_order_types = data['binance_order_types']
TESTNET_BINANCE_CONFIG = data['TESTNET_BINANCE_CONFIG']
exchange = ccxt.binance(TESTNET_BINANCE_CONFIG)
# 变量
strategy_list = ['']
strategy_symbol_list = ['']
strategy_symbol_time_period_list = ['']
reduce_rate_list = ['']
# for S in strategy_list:
#     specific_strategy_symbol = ['']
#     # locals()[f'{S}_symbol_list'] = strategy_symbol
#     exec(f'{S}_symbol_list = ['']')
#     for s in eval(f'{S}_symbol_list'):
#         specific_strategy_symbol_time_period = ['']
#         # locals()[f'{S}_{s}_time_period_list'] = specific_strategy_symbol_time_period
#         exec(f'{S}_{s}_time_period_list = ['']')
#         for t in eval(f'{S}_{s}_time_period_list'):
#             specific_reduce_rate = ['']
#             # locals()[f'{S}_{s}_{t}_reduce_rate'] = specific_reduce_rate
#             exec(f'{S}_{s}_{t}_reduce_rate = ['']')


def load_config(strategy, symbol, time_period):
    # 从配置文件中加载各种配置
    with open(yaml_path, 'r') as f:
        global data
        data = f.read()
        data = yaml.load(data, Loader=yaml.FullLoader)
        f.close()
    if {'strategy_list', f'{strategy}_symbol_list', f'{strategy}_{symbol}_time_period_list', f'{strategy}_{symbol}_{time_period}_reduce_rate'}.issubset(data.keys()):
        global strategy_list
        strategy_list = data['strategy_list']
        global strategy_symbol_list
        strategy_symbol_list = [x for x in data.keys() if 'symbol_list' in x]
        global strategy_symbol_time_period_list
        strategy_symbol_time_period_list = [x for x in data.keys() if 'time_period_list' in x]
        global reduce_rate_list
        reduce_rate_list = [x for x in data.keys() if 'reduce_rate' in x].remove('default_reduce_rate')
        # for S in strategy_list:
        #     # global specific_strategy_symbol
        #     specific_strategy_symbol = data[''.join([x for x in strategy_symbol_list if S in x])]
        #     exec(f'{S}_symbol_list = {specific_strategy_symbol}')
        #     for s in eval(f'{S}_symbol_list'):
        #         # global specific_strategy_symbol_time_period
        #         specific_strategy_symbol_time_period = data[''.join([x for x in strategy_symbol_time_period_list if f'{S}_{s}'in x])]
        #         exec(f'{S}_{s}_time_period_list = {specific_strategy_symbol_time_period}')
        #         for t in eval(f'{S}_{s}_time_period_list'):
        #             # global specific_reduce_rate
        #             specific_reduce_rate = data[''.join([x for x in reduce_rate_list if f'{S}_{s}_{t}' in x])]
        #             exec(f'{S}_{s}_{t}_reduce_rate = {specific_reduce_rate}')
    else:
        _list = ['strategy_list', f'{strategy}_symbol_list', f'{strategy}_{symbol}_time_period_list', f'{strategy}_{symbol}_{time_period}_reduce_rate']
        with open(yaml_path, 'w') as f:
            for x in _list:
                if x not in data.keys():
                    data[x] = ['']
            yaml.dump(data, f)
            f.close()


def check_signal(strategy, symbol, time_period):
    """
    功能时用于检查每次收到的信号是否在预设文件中，如果没有，则在预设文件中新增，并且在数据库文件中新增对应位置来初始化
    """
    load_config(strategy, symbol, time_period)
    global data
    info = test_info.copy()
    info['time_period'] = time_period
    info['symbol'] = symbol
    info = pd.DataFrame(info)
    info.set_index(['time_period'], inplace=True)
    with open(yaml_path, 'w') as f:
        if strategy not in data['strategy_list']:
            data['strategy_list'].append(strategy)
            data['strategy_list'] = list(set(data['strategy_list']))
            if '' in data['strategy_list']:
                data['strategy_list'].remove('')
        if symbol not in data[f'{strategy}_symbol_list']:
            data[f'{strategy}_symbol_list'].append(symbol)
            data[f'{strategy}_symbol_list'] = list(set(data[f'{strategy}_symbol_list']))
            if '' in data[f'{strategy}_symbol_list']:
                data[f'{strategy}_symbol_list'].remove('')
        if time_period not in data[f'{strategy}_{symbol}_time_period_list']:
            data[f'{strategy}_{symbol}_time_period_list'].append(time_period)
            data[f'{strategy}_{symbol}_time_period_list'] = list(set(data[f'{strategy}_{symbol}_time_period_list']))
            if '' in data[f'{strategy}_{symbol}_time_period_list']:
                data[f'{strategy}_{symbol}_time_period_list'].remove('')
            data[f'{strategy}_{symbol}_{time_period}_reduce_rate'] = default_reduce_rate
            if '' in data[f'{strategy}_{symbol}_{time_period}_reduce_rate']:
                data[f'{strategy}_{symbol}_{time_period}_reduce_rate'].remove('')
            df = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
            df = pd.DataFrame(df)
            df = df.append(info)
            df = df[~df.index.duplicated(keep='first')]
            df.to_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
        yaml.dump(data, f)
        f.close()


def schedule_sync():
    """
    定时同步离线资金
    """
    latest_balance = get_latest_balance()
    sync(latest_balance)
    cal_allocated_ratio()


def usdt_future_exchange_info(symbol):
    """
    获取交易币种的最小下单价格、数量精度
    """
    exchange_info = exchange.fapiPublicGetExchangeinfo()
    # 转化为dataframe
    df = pd.DataFrame(exchange_info['symbols'])
    df = df[['symbol', 'pricePrecision', 'quantityPrecision']]
    df.set_index('symbol', inplace=True)
    price_precision = int(df.at[symbol, 'pricePrecision'])
    quantity_precision = df.at[symbol, 'quantityPrecision']
    # symbol_temp[symbol]['最小下单量精度'] = None if p == 0 else int(p)
    return price_precision, quantity_precision


def modify_order_quantity(symbol, quantity):
    """
    根据交易所的精度限制（最小下单单位、量等），修改下单的数量和价格
    """
    # 根据每个币种的精度，修改下单数量的精度
    # 获取每个币对的精度
    price_precision, quantity_precision = usdt_future_exchange_info(symbol)
    quantity_precision = '%.0{}f'.format(quantity_precision) % 0
    quantity = Decimal(quantity).quantize(Decimal(f'{quantity_precision}'))
    return quantity


def modify_decimal(n):
    """
    快速调用的将小数做Decimal处理的小功能
    """
    n = float(n)
    n = Decimal(n).quantize(Decimal("0.000"))
    return n


def get_latest_balance():
    with open("data//response.json", mode='r') as response:
        response = json.load(response)
        account_info = response
    # 获取账户当前总资金
    assets_df = pd.DataFrame(account_info['assets'], dtype=float)
    assets_df = assets_df.set_index('asset')
    latest_balance = modify_decimal(assets_df.loc['USDT', 'marginBalance'])  # 保证金余额
    return latest_balance


def join(strategy, symbol, time_period):
    """
    当有新交易策略/交易对/交易时间区间出现时使用, 利用原有allocate_ratio来对新加入的部分进行分配
    """
    # 初始化当中, 是以allocate ratio 决定allocate funds
    # 初始化
    L = 0
    df = []
    load_config(strategy, symbol, time_period)
    for S in data['strategy_list']:
        for s in data[f'{S}_symbol_list']:
            df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='r')
            df = pd.DataFrame(df)
            L += len(df.index)
    for S in data['strategy_list']:
        for s in data[f'{S}_symbol_list']:
            df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='a')
            df = pd.DataFrame(df)
            for t in data[f'{S}_{s}_time_period_list']:
                if {S, s, t}.issubset([strategy, symbol, time_period]):
                    pass
                else:
                    df.loc[t, 'period_allocated_ratio'] *= modify_decimal((L - 1) / L)
            df.to_hdf(f'data//{S}.h5', key=f'{s}', mode='a')
    df = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
    df = pd.DataFrame(df)
    df.loc[time_period, 'initialize'] = 'none'
    df.loc[time_period, 'period_allocated_ratio'] = modify_decimal(1 / L)
    df.to_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
    # 编辑好各symbol各period_allocated


def sync(latest_balance):
    """
    属于定时任务, 定期更新最新资金, 使用allocated_ratio来进行分配
    """
    for S in data['strategy_list']:
        for s in data[f'{S}_symbol_list']:
            df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='a')
            df = pd.DataFrame(df)
            for t in data[f'{S}_{s}_time_period_list']:
                period_allocated_ratio = modify_decimal(df.loc[t, 'period_allocated_ratio'])
                df.loc[t, 'period_allocated_funds'] = modify_decimal(latest_balance * period_allocated_ratio)
            df.to_hdf(f'data//{S}.h5', key=f'{s}', mode='a')


def cal_allocated_ratio():
    """
    用于通常情况下的资金分配, 用当前策略的allocated_funds来计算出allocated_ratio
    """
    account_balance = Decimal('0.000')
    symbol_allocated_funds = Decimal('0.000')
    strategy_allocated_funds = Decimal('0.000')
    # 累加出symbol_allocated_funds和strategy_allocated_funds
    for S in data['strategy_list']:
        for s in data[f'{S}_symbol_list']:
            df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='a')
            df = pd.DataFrame(df)
            for t in data[f'{S}_{s}_time_period_list']:
                funds = df.loc[t, 'period_allocated_funds']
                funds = modify_decimal(funds)
                symbol_allocated_funds += funds
            strategy_allocated_funds += symbol_allocated_funds
            df.to_hdf(f'data//{S}.h5', key=f'{s}', mode='a')
        account_balance += strategy_allocated_funds
    for S in data['strategy_list']:
        for s in data[f'{S}_symbol_list']:
            df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='a')
            df = pd.DataFrame(df)
            # 通过allocated_funds来逐个决定_allocated_ratio
            for t in data[f'{S}_{s}_time_period_list']:
                df.loc[t, 'account_balance'] = account_balance
                period_allocated_funds = df.loc[t, 'period_allocated_funds']
                period_allocated_funds = modify_decimal(period_allocated_funds)
                df.loc[t, 'period_allocated_ratio'] = modify_decimal(period_allocated_funds / account_balance)
            df.to_hdf(f'data//{S}.h5', key=f'{s}', mode='a')


def remove(strategy, symbol, time_period):
    """
    用于当需要移除交易对的情况, 在配置文件以及数据库文件中都删除其信息
    """
    with open(yaml_path, "w") as f:
        yf = yaml.load(f)
        if 'remove' in strategy:
            strategy = strategy.replace('remove_', '')
            del yf['strategy_list'][f'{strategy}']
            yaml.dump(yf, f)
            yf.close()
            with h5py.File(f'data//{strategy}.h5', "w") as f:
                f.close()
        if 'remove' in symbol:
            symbol = symbol.replace('remove_', '')
            del yf[f'{strategy}_symbol_list'][f'{symbol}']
            yaml.dump(yf, f)
            yf.close()
            with h5py.File(f'data//{strategy}.h5', "a") as f:
                del f[f'{symbol}']
                f.close()
        if 'remove' in time_period:
            symbol = time_period.replace('remove_', '')
            del yf[f'{strategy}_{symbol}_time_period_list'][f'{symbol}']
            yaml.dump(yf, f)
            yf.close()
            df = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
            df = pd.DataFrame(df)
            del df[f'{time_period}']
            df.to_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
    with open(yaml_path, 'r') as f:
        global data
        data = f.read()
        data = yaml.load(data, Loader=yaml.FullLoader)
        f.close()
    L = 0
    par = Decimal('0.000')
    for S in data['strategy_list']:
        for s in data[f'{S}_symbol_list']:
            df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='r')
            df = pd.DataFrame(df)
            for t in data[f'{S}_{s}_time_period_list']:
                p = Decimal(df.loc[t, 'period_allocated_ratio'])
                par += p
    for S in data['strategy_list']:
        for s in data[f'{S}_symbol_list']:
            df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='a')
            df = pd.DataFrame(df)
            for t in data[f'{S}_{s}_time_period_list']:
                df.loc[t, 'period_allocated_ratio'] *= modify_decimal(1 / par)
            df.to_hdf(f'data//{S}.h5', key=f'{s}', mode='a')
    latest_balance = get_latest_balance()
    sync(latest_balance)
    cal_allocated_ratio()


def update_allocation_statistics(strategy, symbol, time_period):
    """
    通过初始化类别，更新资金分配状况，和计算分配比例
    """
    # ====调用接口====
    # exchange.fapiPrivateGetAccount()
    with open("data//response.json", mode='r') as response:
        response = json.load(response)
        account_info = response
    # 获取账户当前总资金
    assets_df = pd.DataFrame(account_info['assets'], dtype=float)
    assets_df = assets_df.set_index('asset')
    latest_balance = modify_decimal(assets_df.loc['USDT', 'marginBalance'])  # 保证金余额
    # ====更新离线数据====
    df = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='r')
    df = pd.DataFrame(df)
    if df.loc[time_period, 'schedule_action'] == 'join':
        join(strategy, symbol, time_period)
        sync(latest_balance)
        cal_allocated_ratio()
    elif df.loc[time_period, 'schedule_action'] == 'sync':
        sync(latest_balance)
        cal_allocated_ratio()
    elif df.loc[time_period, 'schedule_action'] == 'none':
        cal_allocated_ratio()


def position_management(signal_type, strategy, symbol, time_period, quantity, trading_info):
    """
    根据订单类型来来得出开仓量, 和更新数据库文件中的对应记录持仓量
    """
    if signal_type == 'reduce_SHORT':
        # 计算出减仓量
        reduce_rate = data[f'{strategy}_{symbol}_{time_period}_reduce_rate_list']
        reduce_quantity = Decimal(reduce_rate * quantity)
        quantity = Decimal(quantity - reduce_quantity)
        # 在数据库文件里编辑
        trading_info.loc[time_period, 'period_SHORT_position'] = quantity
    if signal_type == 'reduce_LONG':
        # 计算出减仓量
        reduce_rate = data[f'{strategy}_{symbol}_{time_period}_reduce_rate_list']
        reduce_quantity = Decimal(reduce_rate * quantity)
        quantity = Decimal(quantity - reduce_quantity)
        # 在数据库文件里编辑
        trading_info.loc[time_period, 'period_LONG_position'] = quantity
    if signal_type == 'open_LONG':
        trading_info.loc[time_period, 'period_LONG_position'] = quantity
    if signal_type == 'open_SHORT':
        trading_info.loc[time_period, 'period_SHORT_position'] = quantity
    if signal_type == 'close_position':
        reduce_quantity = trading_info.loc[time_period, 'period_SHORT_position'] + trading_info.loc[time_period, 'period_LONG_position']
        quantity = Decimal(reduce_quantity)
    return symbol, signal_type, quantity, trading_info


def processing_trading_action(strategy, symbol, time_period, signal_type):
    """
    处理交易信号，计算开仓量，发送订单
    """
    df = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
    trading_info = pd.DataFrame(df)
    if signal_type == 'reduce_LONG':
        quantity = df.loc[time_period, 'period_LONG_position']
        symbol, signal_type, quantity, trading_info = position_management(signal_type, strategy, symbol, time_period, quantity, trading_info)
        quantity = modify_order_quantity(symbol, quantity)
        order = post_order(symbol, signal_type, quantity)
        trading_record(order, strategy, symbol, time_period, signal_type)
        processing_record(strategy, symbol, time_period)
    if signal_type == 'reduce_SHORT':
        quantity = df.loc[time_period, 'period_SHORT_position']
        symbol, signal_type, quantity, trading_info = position_management(signal_type, strategy, symbol, time_period, quantity, trading_info)
        quantity = modify_order_quantity(symbol, quantity)
        order = post_order(symbol, signal_type, quantity)
        trading_record(order, strategy, symbol, time_period, signal_type)
        processing_record(strategy, symbol, time_period)
    if signal_type == 'open_LONG':
        reduce_quantity = df.loc[time_period, 'period_SHORT_position']
        symbol, signal_type, quantity, trading_info = position_management(signal_type == 'close_position', strategy, symbol, time_period, reduce_quantity, trading_info)
        quantity = modify_order_quantity(symbol, reduce_quantity)
        order = post_order(symbol, signal_type, quantity)
        trading_record(order, strategy, symbol, time_period, signal_type)
        processing_record(strategy, symbol, time_period)
        latest_price = Decimal(exchange.fapiPublicGetTickerPrice({"symbol": "ETHUSDT"})['price'])
        allocated_funds = Decimal(df.loc[time_period, 'period_allocated_funds'])
        quantity = allocated_funds / latest_price
        order = post_order(symbol, signal_type, quantity)
        trading_record(order, strategy, symbol, time_period, signal_type)
        processing_record(strategy, symbol, time_period)
    elif signal_type == 'open_SHORT':
        reduce_quantity = df.loc[time_period, 'period_LONG_position']
        symbol, signal_type, quantity, trading_info = position_management(signal_type == 'close_position', strategy, symbol, time_period, reduce_quantity, trading_info)
        quantity = modify_order_quantity(symbol, reduce_quantity)
        order = post_order(symbol, signal_type, quantity)
        trading_record(order, strategy, symbol, time_period, signal_type)
        processing_record(strategy, symbol, time_period)
        latest_price = Decimal(exchange.fapiPublicGetTickerPrice({"symbol": "ETHUSDT"})['price'])
        allocated_funds = Decimal(df.loc[time_period, 'period_allocated_funds'])
        quantity = allocated_funds / latest_price
        order = post_order(symbol, signal_type, quantity)
        trading_record(order, strategy, symbol, time_period, signal_type)
        processing_record(strategy, symbol, time_period)


def post_order(symbol, signal_type, quantity):
    """
    发送订单, 处理交易所响应
    """
    order = \
        {
            'symbol': symbol,
            'side': binance_order_types[signal_type]['side'],
            'positionSide': binance_order_types[signal_type]['positionSide'],
            'quantity': modify_order_quantity(symbol, quantity),
            'type': 'MARKET',
            'timeInForce': 'GTC',
            'timestamp': int(time.time() * 1000)
        }
    order = json.dumps(order, separators=(',', ':'))
    order = order
    order = ccxt.binance.fapiPrivatePostOrder(order)
    print('\nOrder_Info\n', order)
    return order


def trading_record(order, strategy, symbol, time_period, signal_type):
    """
    目前功能暂时用于记录allocated_funds的变化, 通过获取的交易所响应, 计算当前订单的realized_PNL信息
    """
    quantity = order['executedQty']
    price = order['avgPrice']
    order_time = order['updateTime']
    side = order['side']
    order_time = time.localtime(order_time)
    order_time = time.strftime('%Y-%m-%d %H:%M:%S.%f', order_time)
    record = pd.read_csv('data//trading_record.csv')
    record = pd.DataFrame(record)
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
    record.append(df)
    record.set_index(df['order_time'])
    record.to_csv('data//trading_record.csv')


def processing_record(strategy, symbol, time_period):
    """
    通过record来计算PNL和allocated_funds
    """
    record = pd.read_csv('data//trading_record.csv')
    record = pd.DataFrame(record)
    df = record.query(f"'strategy'=='{strategy}' and 'symbol'=={symbol} and 'time_period'=={time_period}")
    df.set_index(df['order_time'])
    if len(df.index) >= 2:
        n_record = df.loc[df.index[-1]]
        o_record = df.loc[df.index[-2]]
        n_funds = Decimal(n_record['quantity']) * Decimal(n_record['Price']) * Decimal(0.9996)
        o_funds = Decimal(o_record['quantity']) * Decimal(n_record['Price']) * Decimal(0.9996)
        pnl = n_funds - o_funds
        trade_info = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
        trade_info = pd.DataFrame(trade_info)
        trade_info.loc[f'{time_period}', 'allocated_funds'] += pnl
        trade_info.to_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
    else:
        n_record = df.loc[df.index[-1]]
        n_funds = Decimal(n_record['quantity']) * Decimal(n_record['Price']) * Decimal(0.9996)
        trade_info = pd.read_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
        trade_info = pd.DataFrame(trade_info)
        o_funds = trade_info.loc[f'{time_period}', 'allocated_funds']
        funds = (o_funds - n_funds) + n_funds * Decimal('0.9996')
        trade_info.loc[f'{time_period}', 'allocated_funds'] *= modify_decimal(funds)
        trade_info.to_hdf(f'data//{strategy}.h5', key=f'{symbol}', mode='a')
