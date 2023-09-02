import pandas as pd

# Open the spreadsheet

# Read the local file
df = pd.read_excel('files/history2.xlsx')

# Initialize an empty dictionary to store the trading data
trades = {}

# Iterate over each row in the data
for index, row in df.iterrows():
    # Get the date, symbol, price, and amount from the current row
    date = row['Date']
    symbol = row['Symbol']
    price = row['Price']
    amount = row['Amount']

    # Add the trade to the dictionary
    trade = {
        'date': date,
        'symbol': symbol,
        'price': price,
        'amount': amount
    }
    trades[f"{len(trades) + 1}"] = trade

# Print the trades dictionary
print(trades)