from pyziabm.runner import Runner
import time

def main(num_mms = 1, mm_maxq = 1, mm_quotes = 5, mm_quote_range = 20, q_provide = 0.5, run_steps = 50000):

    start = time.time()
    print(start) 

    
#    num_mms=1
#    mm_maxq=1
#    mm_quotes=5
#    mm_quote_range=20
#    mm_delta=0.05
#    num_takers=100
#    taker_maxq=1
#    num_providers=45
#    provider_maxq=1
#    q_provide=0.5
#    alpha=0.0375
#    mu=0.0005
#    delta=0.025
#    lambda0=100
#    wn=0.001
#    c_lambda=50.0
#    run_steps=100000
#    mpi=1
#    h5filename='test.h5'  

    market1 = Runner(run_steps = run_steps)
        
    market1.seed_orderbook()
    market1.make_setup(20)

    market1.run_mcs(20)
    
    tb = market1.exchange.trade_book_to_df()
    qtake = market1.qtake_to_df()
    mmp = market1.mm_profitability_to_df()
    orders = market1.exchange.order_history_to_df()
    trades = market1.exchange.trade_book_to_df()
    
    print('Run 2: %.2f minutes' % ((time.time() - start)/60))
    
    return [tb, qtake, mmp, orders, trades]


if __name__ == "__main__":
    df = main()

    # df.info()
    query = df.to_json()


"""
Testing Zone

from pyziabm_run_d import main 

import random
import numpy as np

random.seed(5); np.random.seed(5) 

df = main(run_steps=10000) 

len(df[-1]['price'])

df[-1]['price'].plot(title='Trade Execution Prices for n = 10000 steps')


import matplotlib.pyplot as plt

fig, ax = plt.subplots(nrows=2)

ax[0].plot(df[2]['cash_flow'])
ax[1].plot(df[2]['position'])

ax[0].title.set_text("Market Maker Net Cash Flow")
ax[1].title.set_text("Market Maker Net Position")

"""