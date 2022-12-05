import time
import datetime
import pandas as pd
import web3
from web3 import Web3
import json
from typing import Union
from eth_typing.evm import Address, ChecksumAddress
import itertools
import numpy as np

AddressLike = Union[Address, ChecksumAddress]

rpc_polygon = 'https://polygon-mainnet.nodereal.io/v1/b491dd1e97ed43e2bbab31aa1f9f7a27'

crv_polygon = '0x172370d5Cd63279eFa6d502DAB29171933a610AF'
usdc_polygon = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
b4bm = Web3.toChecksumAddress('0x56a15aaa0f88338fceb5aec28aba249acc75f185')
set_router = Web3.toChecksumAddress('0x1c0c05a2aA31692e5dc9511b04F651db9E4d8320')


def open_abi(w3: Web3, abi: str, address: AddressLike):
    """open .abi files for smart contract execution"""
    address = Web3.toChecksumAddress(address)
    with open(f'{abi}.abi', 'r') as f:
        json_abi = json.load(f)
    return w3.eth.contract(address=address, abi=json_abi)


def estimate_block_height_by_timestamp(timestamp):
    block_found = False
    last_block_number = connection_polygon.eth.blockNumber
    close_in_seconds = 600

    while not block_found:
        block = connection_polygon.eth.getBlock(last_block_number-1)
        block_time = datetime.datetime.fromtimestamp(block.timestamp).date()
        difference_in_seconds = int((timestamp - block_time).total_seconds())

        block_found = abs(difference_in_seconds) < close_in_seconds

        if block_found:
            return last_block_number

        if difference_in_seconds < 0:
            last_block_number //= 2
        else:
            last_block_number = int(last_block_number * 1.5) + 1


def pandas_dt():
    df = pd.DataFrame(columns=['date'])
    end_date = datetime.datetime.now()

    df['date'] = pd.date_range('17-11-2022', end_date, freq='D')

    df['date'] = df['date'].values.astype(np.int64)
    print(df)
    return df


range_df = pandas_dt()
connection_polygon = Web3(Web3.HTTPProvider(rpc_polygon))


for date in range_df['date']:
    block = estimate_block_height_by_timestamp(date)

    print(block)


print(connection_polygon.eth.blockNumber)

univ3_price = open_abi(connection_polygon, 'abi/b4bm', b4bm).functions.getPositions().call(block_identifier=connection_polygon.eth.blockNumber)
print(univ3_price)