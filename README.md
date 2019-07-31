# tradenotebook-alpha

Secret key changed to environment variable - `source .env` or add to config vars in production.


TODO:
Currently each run of pyziabm_run main() outputs a test.h5 file. Remove that.
Get the respective dataframes for the other 4 currently outputting to .

Convert to json format.


Bring into view


TODO:

What do you actually need to return? List those out; what "steps" do you actually need to return to make a nicer time series?
I don't think it will end up being "live". At least not in this implementation.
But you can graph the marketmaker's profitability on the same scale.

Need a way to set the starting and stop prices. Also no need for pennyjumpers right? They do exist and write a case for them... but not usually.
Need "Trader" instances to be very one-directional at times. Execute at a certain time...
From 9:30 AM (timestamp 1) to 4pm there are 6 and a half hours. That makes 390 minutes. That makes 23400 seconds. So you should parse out the "randomness" to group into certain periods... ACCORDING TO A BELL CURVE!!!