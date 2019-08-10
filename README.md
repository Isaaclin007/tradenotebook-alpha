# tradenotebook-alpha

Secrets in environment variable - `source .env` or add to config vars in production.

The purpose of this app is to simulate actors in financial markets, deriving from the concept of a zero intelligence agent-based model on ETFs. The finished model should present an educational visualization of the effects of primary actors in financial markets.

## TODO:

Lightweight code refactor:
- [x] Remove H5 output and associated code
- [ ] Implement dataframe logic for delta over time and document output
- [ ] Consider implementing a wrapper for broader time periods - higher computational work, less json output
- [ ] Update schema design and add constraints
- [ ] Implement fuzzy logic prediction, perhaps with `fbprohet`

### Complete Refactor of Pyziabm

The main priority is to expose some of the internal endpoints to be able to `POST` data such as number of market makers, erratic actors, etc...

The current marketmaker class is a bit too arbitrary in pulling/pushing quotes. There should be some sort of fuzzy logic there that's not just a random guassian distribution.

Implement drift with Geometric brownian motion - needs to be quantifiable.

What economic model do you want to "enforce"? Merton?

What do you actually need to return? List those out; what "steps" do you actually need to return to make a nicer time series?
I don't think it will end up being "live". At least not in this implementation. But can still graph the marketmaker's profitability on the same scale.

Need a way to set the starting and stop prices. Also no need for pennyjumpers?

Need "Trader" instances to be very one-directional at times. Execute at a certain time...

In order to simulate a trading day, from 9:30 AM (timestamp 1) to 4pm there are 6 and a half hours. That makes 390 minutes. That makes 23400 seconds. So you should parse out the "randomness" to group into certain periods according to a bell curve.