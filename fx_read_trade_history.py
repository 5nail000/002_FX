from bs4 import BeautifulSoup

# URL of the trading history file
url = "https://drive.google.com/file/d/1NPDy0SI6-s9_Hv9Q3Ft6qGU5XtqcY-TR/view"

filename = 'files/history.html'
with open(filename, 'r', encoding='utf_8') as f:
    soup = BeautifulSoup(f, 'html.parser')
    print(soup)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(soup, 'html.parser')

# Find the table containing the trading history
table = soup.find('table')

# Initialize an empty dictionary to store the trades
trades = {}

# Iterate over each trade row in the table
for row in table.find_all('tr'):
    # Extract the trade details from the row
    order_num = row.find('td', class_='order-number').text.strip()
    symbol = row.find('td', class_='symbol').text.strip()
    quantity = row.find('td', class_='quantity').text.strip()
    price = row.find('td', class_='price').text.strip()
    timestamp = row.find('td', class_='timestamp').text.strip()

    # Add the trade to the dictionary with an incrementing order number
    order_num = int(order_num)
    trades[order_num] = {
        'symbol': symbol,
        'quantity': quantity,
        'price': price,
        'timestamp': timestamp
    }

# Print the contents of the trades dictionary
print(trades)
