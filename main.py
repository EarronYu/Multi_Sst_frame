"""
通过这个模块能够开放主机上的5000端口, 并且接收tradingview传来的post信息
"""
# Yes?

from functions import *
from flask import Flask, request, abort
import ast
import hashlib
import time
import datetime
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler

time_delta = 0
L = 0
a = 0
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


def report():
    with open(yaml_path, 'r') as f:
        global data
        data = f.read()
        data = yaml.load(data, Loader=yaml.FullLoader)
        f.close()
        msg_S = ''
        S = ''
        for S in data['strategy_list']:
            msg_s = ''
            msg_Ss = ''
            s = ''
            for s in data[f'{S}_symbol_list']:
                df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='r')
                df_record = pd.read_hdf(f'data//{S}_trading_record.h5', key=f'{s}', mode='r')
                df = pd.DataFrame(df).astype(str)
                df_record = pd.DataFrame(df_record).astype(str)
                msg_st = ''
                t = ''
                for t in data[f'{S}_{s}_time_period_list']:
                    ratio = df.loc[t, 'period_allocated_ratio']
                    funds = df.loc[t, 'period_allocated_funds']
                    position_SHORT = Decimal(df.loc[t, 'period_SHORT_position'])
                    position_LONG = Decimal(df.loc[t, 'period_LONG_position'])
                    if position_LONG - position_SHORT > 0:
                        side = 'LONG'
                    else:
                        side = 'SHORT'
                    position = position_LONG + position_SHORT
                    msg_t = f'Timeperiod: {t}\nRatio: {ratio}\nFunds: {funds}\n{side}_position: {position}\n'
                    msg_st += msg_t
                    msg_s = f'{s}\n{msg_st}\n'
                msg_Ss += msg_s
            msg_S = f'{S}\n{msg_Ss}'
            send_message(msg_S)

def processing_signal(strategy, symbol, time_period, signal_type):
    global a
    start = time.time()
    result = check_signal(strategy, symbol, time_period, signal_type)
    if result == 'passed':
        if a < 1:
            global a
            scheduler.add_job(schedule_sync, 'cron', month='*', day='*', hour='7, 19', minute='59', args=[], misfire_grace_time=10)
            scheduler.add_job(report, 'cron', month='*', day='*', hour='7, 9, 11, 13, 15, 17, 19, 21, 23', minute='59', args=[], misfire_grace_time=10)
            a += 2
        update_allocation_statistics(strategy, symbol, time_period)
        processing_trading_action(strategy, symbol, time_period, signal_type)
    else:
        print(f'Rejected Signal You did\'t Open Position Named {symbol} on {time_period}'.center(120))
    end = time.time()
    t = end - start
    print(f'Time Cost: {t}'.center(120))
    print('Completed!'.center(L))
    print('>' * 5 + '=' * (L - 10) + '<' * 5)


def tradingview_alart():
    msg = 'Time to modify expire dates on tradingview!'
    send_message(msg)
    time_now = datetime.datetime.now()
    target_time = time_now + datetime.timedelta(hours=2)
    target_time = target_time.replace(second=0, microsecond=0)
    scheduler.add_job(tradingview_alart, 'date', run_date=target_time, args=[], misfire_grace_time=10)



def next_run_time(time_interval, ahead_seconds=5):
    """
    根据time_interval，计算下次运行的时间，下一个整点时刻。
    目前只支持分钟和小时。
    :param time_interval: 运行的周期，15m，1h
    :param ahead_seconds: 预留的目标时间和当前时间的间隙
    :return: 下次运行的时间
    案例：
    15m  当前时间为：12:50:51  返回时间为：13:00:00
    15m  当前时间为：12:39:51  返回时间为：12:45:00
    10m  当前时间为：12:38:51  返回时间为：12:40:00
    5m  当前时间为：12:33:51  返回时间为：12:35:00
    5m  当前时间为：12:34:51  返回时间为：12:35:00

    1h  当前时间为：14:37:51  返回时间为：15:00:00
    2h  当前时间为：00:37:51  返回时间为：02:00:00

    30m  当前时间为：21日的23:33:51  返回时间为：22日的00:00:00
    5m  当前时间为：21日的23:57:51  返回时间为：22日的00:00:00

    ahead_seconds = 5
    15m  当前时间为：12:59:57  返回时间为：13:15:00，而不是 13:00:00
    """
    if time_interval.endswith('m') or time_interval.endswith('h'):
        pass
    elif time_interval.endswith('T'):
        time_interval = time_interval.replace('T', 'm')
    elif time_interval.endswith('H'):
        time_interval = time_interval.replace('H', 'h')
    else:
        print('illegal time_interval format, Exit')
        exit()
    ti = pd.to_timedelta(time_interval)
    now_time = datetime.datetime.now()
    # now_time = datetime(2019, 5, 9, 23, 50, 30)  # 指定now_time，可用于测试
    this_midnight = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    min_step = datetime.timedelta(minutes=1)
    target_time = now_time.replace(second=0, microsecond=0)

    while True:
        target_time = target_time + min_step
        delta = target_time - this_midnight
        if delta.seconds % ti.seconds == 0 and (target_time - now_time).seconds >= ahead_seconds:
            # 当符合运行周期，并且目标时间有足够大的余地，默认为60s
            break
    target_time = target_time - datetime.timedelta(minutes=1)
    print(f'Next Reset Time_Delta Time：{target_time}')
    return target_time


def reset_time():
    time.sleep(60)
    global time_delta
    time_delta = 0
    time_now = datetime.datetime.now()
    target_time = time_now + datetime.timedelta(minutes=4)
    target_time = target_time.replace(second=0, microsecond=0)
    scheduler.add_job(reset_time, 'date', run_date=target_time, args=[], misfire_grace_time=10)


def offset_time():
    time_now = datetime.datetime.now()
    global time_delta
    target_time = time_now + datetime.timedelta(seconds=time_delta)
    time_delta += 3
    return target_time


scheduler = BackgroundScheduler()
# scheduler = BlockingScheduler()
scheduler.add_job(reset_time, 'date', run_date=next_run_time('5m'), args=[], misfire_grace_time=10)
scheduler.add_job(tradingview_alart, 'cron', month='1-12', day='1st mon', hour='10', args=[], misfire_grace_time=10)
scheduler.start()


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    建立出来一个叫做webhook的位置, 专门接收post信息并分拣到不同symbol以及不同time_period
    """
    global L
    if request.method == 'POST':
        # Parse the string data from tradingview into a python dict
        data = parse_webhook(request.get_data(as_text=True))  # 将接收到的信息交给action中的parse_webhook函数处理, return给data
        # Check that the key is correct
        if get_token() == data['key']:  # 如果get_token返回来的值等于data数据容器中的'key', 向下执行
            strategy = data["strategy"]
            symbol = data["symbol"]
            symbol = symbol[:-4]
            time_period = data["time_period"]
            signal_type = data["signal_type"]
            if 'remove' in (strategy + symbol + time_period):
                msg = f'Removing {strategy} {symbol} {time_period}'
                L = 120
                print('>' * 5 + '=' * (L-10) + '<' * 5)
                print(msg.center(L))
                print('Processing...'.center(L))
                remove(strategy, symbol, time_period)
                print('Completed!'.center(L))
                print('>' * 5 + '=' * (L-10) + '<' * 5)
                print('Completed!'.center(L))
            else:
                msg = f'Received Trading Information: {strategy} {symbol} {time_period} {signal_type} Signal'
                L = 120
                print('>' * 5 + '=' * (L-10) + '<' * 5)
                print(msg.center(L))
                print('Processing...'.center(L))
                scheduler.add_job(processing_signal, 'date', run_date=offset_time(), args=[strategy, symbol, time_period, signal_type], misfire_grace_time=10)
        else:
            abort(403)
    else:
        abort(400)
    return 'complete', 200


if __name__ == '__main__':
    app.run()
