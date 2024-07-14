1. Set up an API to a daily end of day data set for ASX (eg Bodhi6 - JustData's Stock Market Data Downloader). 
2. Then apply simple rules:
- Find the all-time high
- Find the lowest point since the all-time high
- If the all-time high is more than double the low, and the low occurred within the last 30 days, then we have a match
3. Then export list of all stocks that satisfy the screen, into .csv for import into Tradingview 
(format eg.. 
ASX:14D
)