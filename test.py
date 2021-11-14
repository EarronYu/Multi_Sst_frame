# # # # import time
# # # # import datetime
# # # # from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
# # # #
# # # # time_delta = 0
# # # #
# # # #
# # # # def job_func():
# # # #     print('okay')
# # # #
# # # #
# # # # def reset_time():
# # # #     time.sleep(60)
# # # #     global time_delta
# # # #     time_delta = 0
# # # #     time_now = datetime.datetime.now()
# # # #     target_time = time_now + datetime.timedelta(minutes=4)
# # # #     scheduler.add_job(reset_time(), 'date', run_date=target_time, args=[])
# # # #     scheduler.start()
# # # #     print('Time Delta Reset')
# # # #
# # # #
# # # # def offset_time():
# # # #     time_now = datetime.datetime.now()
# # # #     global time_delta
# # # #     target_time = time_now + datetime.timedelta(seconds=time_delta)
# # # #     time_delta += 3
# # # #     return target_time
# # # #
# # # #
# # # # # 第一次启动的时候调用reset_
# # # # scheduler = BackgroundScheduler()
# # # # # scheduler = BlockingScheduler()
# # # # scheduler.add_job(reset_time(), 'date', run_date=datetime.datetime(2021, 8, 29, 11, 34, 0), args=[])
# # # # scheduler.add_job(job_func(), 'date', run_date=offset_time(), args=[])
# # # # scheduler.start()
# import pandas as pd
# import yaml
# from decimal import Decimal
# # # import h5py
# # # import sys
# # # # pd.set_option('display.max_columns', None)
# symbol = 'ETHUSDT'
# strategy_01 = 'Vision_Beginner'
# # # strategy_02 = 'Vision_algorithmic_indicator'
# # # # # with h5py.File(f'data//{strategy_02}.h5', "a") as f:
# # # # #     del f[f'{symbol}']
# # # # #     f.close()
# pd.set_option('display.max_rows', 1000)
# pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
# pd.set_option('display.unicode.ambiguous_as_wide', True)  # 设置命令行输出时的列对齐功能
# pd.set_option('display.unicode.east_asian_width', True)
# pd.set_option('display.max_columns', 1000)
# pd.set_option('display.width', 1000)
# pd.set_option('display.max_colwidth', 1000)
# pd.set_option('mode.chained_assignment', None)
# df_01 = pd.read_hdf(f'data//{strategy_01}.h5', key=f'{symbol}', mode='r')
# # df_02 = pd.read_hdf(f'data//{strategy_01}_trading_record.h5', key=f'{symbol}', mode='r')
# print(df_01)
# # print(df_02)
#
#
# yaml_path = 'data//settings.yaml'
# from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
#
#
# def report():
#     with open(yaml_path, 'r') as f:
#         global data
#         data = f.read()
#         data = yaml.load(data, Loader=yaml.FullLoader)
#         f.close()
#         msg_S = ''
#         S = ''
#         for S in data['strategy_list']:
#             msg_s = ''
#             msg_Ss = ''
#             s = ''
#             for s in data[f'{S}_symbol_list']:
#                 df = pd.read_hdf(f'data//{S}.h5', key=f'{s}', mode='r')
#                 df_record = pd.read_hdf(f'data//{S}_trading_record.h5', key=f'{s}', mode='r')
#                 df = pd.DataFrame(df).astype(str)
#                 df_record = pd.DataFrame(df_record).astype(str)
#                 msg_st = ''
#                 t = ''
#                 for t in data[f'{S}_{s}_time_period_list']:
#                     ratio = df.loc[t, 'period_allocated_ratio']
#                     funds = df.loc[t, 'period_allocated_funds']
#                     position_SHORT = Decimal(df.loc[t, 'period_SHORT_position'])
#                     position_LONG = Decimal(df.loc[t, 'period_LONG_position'])
#                     if position_LONG - position_SHORT > 0:
#                         side = 'LONG'
#                     else:
#                         side = 'SHORT'
#                     position = position_LONG + position_SHORT
#                     msg_t = f'Timeperiod: {t}\nRatio: {ratio}\nFunds: {funds}\n{side}_position: {position}'
#                     msg_st += msg_t
#                     msg_s = f'{s}\n{msg_st}\n'
#                 msg_Ss += msg_s
#             msg_S = f'{S}\n{msg_Ss}'
#             send_message(msg_S)
#     scheduler.add_job(report, 'interval', hours=2, args=[], misfire_grace_time=10)
#
# report()
#
a = 0
result = 'passed'


def c(result):
    global a
    if result == 'passed':
        if a < 1:
            print('yes')
            a += 2
        else:
            print('no')

c(result)
c(result)
c(result)