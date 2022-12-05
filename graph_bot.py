import numpy as np
import requests
import datetime
import time
import json
import pandas as pd

seven_d = datetime.date.today() - datetime.timedelta(6)
seven_d = time.mktime(seven_d.timetuple())
whitelist_tokens = ['0x514910771af9ca656af840dff83e8264ecf986ca',
                    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
                    '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
                    '0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0',

                    ]

def graph_query(graph_q):
    req = requests.post('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
                        json={'query': graph_q})

    return req.text


def div_zero(x, y):
    try:
        return x / y
    except ZeroDivisionError:
        return 0


def volatility(list_data):
    list_data = [div_zero(list_data[i + 1], list_data[i]) - 1 for i in range(len(list_data) - 1)]
    vol = np.std(list_data)
    return vol


def construct_data(json_abi):
    json_abi = json.loads(json_abi)
    pos = {}
    for i, data in enumerate(json_abi['data']['pools']):
        res = {'id_pool': data['id'], 'token1_id': data['token0']['id'], 'token2_id': data['token1']['id'],
               'token1_symbol': data['token0']['symbol'], 'token2_symbol': data['token1']['symbol'],
               'pool_reserveUSD': data['totalValueLockedUSD'], 'pool_volumeUSD': data['volumeUSD'],
               'feeTier': data['feeTier'],
               'pool_volumeUSD_7D': sum([float(x['volumeUSD']) for x in data['poolDayData']]),
               'std_7d': volatility([float(x['close']) for x in data['poolDayData']])}
        pos = pos | {i: res}
    return pos


graph_q = """
{
    pools(
        first: 1000
        where: {totalValueLockedUSD_gt: "1000000", volumeUSD_gt: "50000"}
        orderBy: totalValueLockedUSD
        orderDirection: desc
        ) {
            id
            token0 {
              id
              symbol
            }
            token1 {
              id
              symbol
            }
            totalValueLockedUSD
            volumeUSD
            feeTier
            poolDayData(where: {date_gt: """ + str(int(seven_d)) + """ }
            ) {volumeUSD
               close}
            }
}
"""

query_data = graph_query(graph_q)
full_data = pd.DataFrame(construct_data(query_data)).T
full_data.loc[:, 'yearly_return'] = full_data['pool_volumeUSD_7D'].astype(float) * full_data['feeTier'].astype(float) /\
                                    1000000 / full_data['pool_reserveUSD'].astype(float) * 52
full_data = full_data.sort_values(by=['yearly_return'], ascending=False)
print(full_data.head(30).to_string())