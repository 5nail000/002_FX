'''
import matplotlib.dates as mdates
import matplotlib.patches as patches
from dateutil.relativedelta import relativedelta
import numpy as np
'''
import time
import pprint
import math
from datetime import datetime, timedelta
import pandas as pd

from read_reports import parse_html
from draw_plots import plot_weekly_series, plot_weekly_balance


pp = pprint.PrettyPrinter(indent=2)


def process_deals(deals):
    processed_deals = []
    drawdown = 0
    series_length = 0
    drawdown_levels = {}
    series_start_balance = None  # добавляем переменную для хранения начала баланса на начало серии
    deals.pop(0)

    for deal in deals:
        profit = float(deal['Прибыль'].replace(" ", ""))
        balance = float(deal['Баланс'].replace(" ", ""))

        if series_start_balance is None or drawdown == 0:
            series_start_balance = balance - profit

        balance_change = balance - series_start_balance  # изменение баланса по серии

        if profit > 0:
            # If the previous deal(s) were losses, record them as a drawdown
            if drawdown < 0:
                processed_deals.append({
                    'Время': deal['Время'],
                    'Объем': deal['Объем'],
                    'Баланс': deal['Баланс'],
                    'Прибыль': balance_change,
                    'Просадка': drawdown,
                    'Размер серии': series_length + 1,
                    'Уровни просадки': drawdown_levels
                })
                # Reset the drawdown, series length, drawdown levels and series_start_balance
                drawdown = 0
                series_length = 0
                drawdown_levels = {}
            else:
                processed_deals.append({
                    'Время': deal['Время'],
                    'Объем': deal['Объем'],
                    'Баланс': deal['Баланс'],
                    'Прибыль': balance_change,
                    'Просадка': 0,
                    'Размер серии': 1,
                    'Уровни просадки': {}
                })
        else:
            drawdown += profit
            series_length += 1
            # Update the drawdown levels
            drawdown_levels[series_length] = drawdown

    return processed_deals


def recalculate_balance(processed_deals, initial_balance, drawdown_level, start_date=None, end_date=None, multiplier=3000):
    first_deposit = initial_balance
    balance = initial_balance
    balance_history = []
    withdrawals = 0  # Initialize the withdrawals counter
    deposits = 1  # Initialize the deposits counter

    # Convert start_date and end_date to datetime objects if they are not None and are strings
    if start_date is not None and isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%d.%m.%Y')
    if end_date is not None and isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%d.%m.%Y')

    for deal in processed_deals:
        # Parse the deal date
        deal_date = datetime.strptime(deal['Время'], '%Y.%m.%d %H:%M:%S')  # adjust the format as necessary

        # If start_date and end_date are provided, skip the deal if it's not within the date range
        if start_date is not None and deal_date < start_date:
            continue
        if end_date is not None and deal_date > end_date:
            continue

        # If the drawdown level of the deal is greater than the specified drawdown level,
        # use the loss corresponding to the specified drawdown level
        if deal['Размер серии'] > drawdown_level:
            loss = deal['Уровни просадки'].get(drawdown_level, 0)
        else:
            loss = deal['Прибыль']

        # Apply multiplier based on balance
        balance_ratio = balance / multiplier
        balance_ratio = max(math.floor(balance_ratio), 1)
        loss *= balance_ratio

        # Calculate the new balance after the deal
        last_positive_balance = balance  # Save the last positive balance before changing it
        balance += loss
        balance_change = loss

        # If balance is negative, set it to zero and adjust balance_change to be the negative of the last positive balance
        if balance < 0:
            balance_change = -last_positive_balance
            balance = 0  # Reset balance to zero

        balance_history.append({
            'Время': deal['Время'],
            'Прибыль': balance_change,
            'Баланс': balance,
            'Размер серии': deal['Размер серии'],
            'Множитель': balance_ratio,
            'Тип': 'сделка'
        })

        # If balance is less than first_deposit, add a deposit
        if balance < first_deposit:
            deposit_date = deal_date + timedelta(seconds=5)
            deposit_amount = first_deposit - balance
            balance += deposit_amount
            deposits += 1  # Increase the deposits counter
            balance_history.append({
                'Время': deposit_date.strftime('%Y.%m.%d %H:%M:%S'),
                'Прибыль': deposit_amount,
                'Баланс': balance,
                'Размер серии': 0,
                'Множитель': 0,
                'Тип': 'пополнение'
            })

        # If balance_ratio exceeds 2 and balance exceeds first_deposit, add a withdrawal
        # But only if the number of withdrawals is less than the number of deposits
        if balance >= ((multiplier * 2) + first_deposit) and withdrawals < deposits:
            withdrawal_date = deal_date + timedelta(seconds=5)
            balance -= first_deposit
            withdrawals += 1  # Increase the withdrawals counter
            balance_history.append({
                'Время': withdrawal_date.strftime('%Y.%m.%d %H:%M:%S'),
                'Прибыль': -first_deposit,
                'Баланс': balance,
                'Размер серии': 0,
                'Множитель': 0,
                'Тип': 'снятие средств'
            })

    return balance_history


def count_series_size(processed_deals):
    series_size_count = {}
    for deal in processed_deals:
        series_size = deal['Размер серии']
        if series_size in series_size_count:
            series_size_count[series_size] += 1
        else:
            series_size_count[series_size] = 1
    return series_size_count


def calculate_risk_and_split_balance(balance, risk_manage):
    sorted_risk_levels = sorted(risk_manage.keys(), reverse=True)
    for level in sorted_risk_levels:
        if balance >= level:
            risk_percent = risk_manage[level] / 100
            risky_balance = balance * risk_percent
            buffer_balance = balance - risky_balance
            return risk_percent, risky_balance, buffer_balance
    return 1, balance, 0  # If no risk level is satisfied, return 100% risk and all balance is risky


def save_to_excel(data, filename):
    df = pd.DataFrame(data)  # Создаем DataFrame из списка словарей
    df.to_excel(filename, index=False, startrow=2)  # Записываем DataFrame в xlsx файл


history_file = 'files/test_h1.html'
render_plot_file = 'files/weekly_series_sizes_h1.png'

deals = parse_html(history_file)
processed_deals = process_deals(deals)
count_series = count_series_size(processed_deals)
plot_weekly_series(processed_deals, render_plot_file)

initial_balance = 500
drawdown_level = 8
start_date = '01.01.2014'
end_date = '01.01.2024'
multiplier = 500

calculated_deals = recalculate_balance(processed_deals, initial_balance, drawdown_level, start_date, end_date, multiplier)
render_plot_file = 'files/weekly_recalculated_balance_h1.png'
plot_weekly_balance(calculated_deals, render_plot_file)
save_to_excel(calculated_deals, 'files/calculated_deals.xlsx')

# pp.pprint(processed_deals[-1])
# pp.pprint(calculated_deals)
pp.pprint(calculated_deals[-1]['Баланс'])
pp.pprint(len(calculated_deals))
# pp.pprint(count_series)
