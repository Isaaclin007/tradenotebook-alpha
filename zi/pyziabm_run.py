from .pyziabm.runner import Runner
import time

def main(num_mms = 1, mm_maxq = 1, mm_quotes = 5, mm_quote_range = 20, q_provide = 0.5, run_steps = 1000):

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

    market1 = Runner()
        
    market1.seed_orderbook()
    market1.make_setup(20)

    market1.run_mcs(20)
    
    tb = market1.exchange.trade_book_to_df()
    qtake = market1.qtake_to_df()
    mmp = market1.mm_profitability_to_df()
    orders = market1.exchange.order_history_to_df()
    trades = market1.exchange.trade_book_to_df()

    

    
    return [tb, qtake, mmp, orders, trades]

    print('Run 2: %.2f minutes' % ((time.time() - start)/60))
    
if __name__ == "__main__":
    df = main()

    # df.info()
    query = df.to_json()