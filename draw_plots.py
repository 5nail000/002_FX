import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np


def plot_weekly_series(processed_deals, output_file):
    # Convert times to datetime objects
    times = [datetime.strptime(deal['Время'], '%Y.%m.%d %H:%M:%S') for deal in processed_deals]

    # Use the date of the first deal as the base date
    base_date = times[0]
    end_date = times[-1]

    # Create a list of weeks (since the base date) and series sizes
    weeks = [(time - base_date).days // 7 for time in times]
    series_sizes = [deal['Размер серии'] for deal in processed_deals]

    # Group series sizes by week
    week_to_series_sizes = {}
    for week, series_size in zip(weeks, series_sizes):
        if week not in week_to_series_sizes:
            week_to_series_sizes[week] = []
        week_to_series_sizes[week].append(series_size)

    # Create a list of all weeks between the first and last deal
    all_weeks = list(range((end_date - base_date).days // 7 + 1))

    # Prepare the data for the plot
    x = []
    widths = []
    heights = []
    colors = []

    for week in all_weeks:
        series_sizes = week_to_series_sizes.get(week, [0])

        num_series = len(series_sizes)
        for i, series_size in enumerate(series_sizes):
            x.append(week + i / num_series)
            widths.append(1.0 / num_series)
            heights.append(series_size)
            colors.append('blue' if num_series > 1 else 'darkblue')

    # Create the plot
    fig, ax = plt.subplots(figsize=(len(x) / 2, 6))
    bars = ax.bar(x, heights, width=widths, color=colors, align='edge')

    # Add labels under each bar
    for bar, height in zip(bars, heights):
        ax.text(bar.get_x() + bar.get_width() / 2.0, -0.05, str(height), color='black', ha='center', va='top')

    # Add labels and title
    plt.title('Weekly Series Sizes')
    plt.xlabel('Week')
    plt.ylabel('Series Size')

    # Set up the space between bars
    ax.set_xticks([week + 1 for week in all_weeks], minor=True)

    # Add grey lines for weeks
    for week in all_weeks:
        ax.axvline(x=week + 1, color='grey', linewidth=0.5, linestyle='--')

    # Determine the weeks when a new month or year starts
    month_changes = []
    year_changes = []
    current_month = base_date.month
    current_year = base_date.year
    week_times = [base_date + timedelta(weeks=week) for week in all_weeks]

    for week, time in enumerate(week_times):
        if time.month != current_month:
            month_changes.append(week)
            current_month = time.month
        if time.year != current_year:
            year_changes.append(week)
            current_year = time.year

    # Add vertical lines for month and year changes
    for week in month_changes:
        ax.axvline(x=week, color='orange', linestyle='--', linewidth=1)
    for week in year_changes:
        ax.axvline(x=week, color='red', linestyle='--', linewidth=2)

    # Add year labels at year changes
    for week in year_changes:
        ax.text(week, max(heights) * 1.1, str(week_times[week].year), ha='center', va='top', color='red', fontsize=12)

    # Save the plot as a PNG file
    plt.savefig(output_file, dpi=100)


def plot_weekly_balance(processed_deals, output_file):
    # Convert times to datetime objects and get balances
    times = [datetime.strptime(deal['Время'], '%Y.%m.%d %H:%M:%S') for deal in processed_deals]
    balances = [deal['Баланс'] for deal in processed_deals]
    types = [deal['Тип'] for deal in processed_deals]
    profits = [deal['Прибыль'] if 'Прибыль' in deal else 0 for deal in processed_deals]

    # Use the date of the first deal as the base date
    base_date = times[0]
    end_date = times[-1]

    # Create a list of all weeks between the first and last deal
    all_weeks = list(range((end_date - base_date).days // 7 + 1))

    # Group balances by week
    week_to_balances = {week: [] for week in all_weeks}
    week_to_deposits = {week: [] for week in all_weeks}
    week_to_withdrawals = {week: [] for week in all_weeks}
    for time, balance, ttype, profit in zip(times, balances, types, profits):
        week = (time - base_date).days // 7
        week_to_balances[week].append(balance)
        if ttype == 'пополнение':
            week_to_deposits[week].append(balance)
        elif ttype == 'снятие средств':
            week_to_withdrawals[week].append(profit)

    # Get the last balance for each week
    last_known_balance = None
    week_finals = {}
    for week, balances in week_to_balances.items():
        if balances:
            last_known_balance = balances[-1]
        week_finals[week] = last_known_balance

    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(len(all_weeks) / 2, 6), gridspec_kw={'height_ratios': [3, 1]})
    # Adjust the subplots size
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)

    ax1.plot(all_weeks, [week_finals[week] for week in all_weeks], linewidth=4)

    # Add labels and title
    ax1.set_title('Weekly Final Balance')
    ax1.set_xlabel('Week')
    ax1.set_ylabel('Final Balance')

    # Determine the weeks when a new month or year starts
    month_changes = []
    year_changes = []
    current_month = base_date.month
    current_year = base_date.year
    week_times = [base_date + timedelta(weeks=week) for week in all_weeks]

    for week, time in enumerate(week_times):
        if time.month != current_month:
            month_changes.append(week)
            current_month = time.month
        if time.year != current_year:
            year_changes.append(week)
            current_year = time.year

    # Add vertical lines for month and year changes
    for week in month_changes:
        ax1.axvline(x=week, color='orange', linestyle='--', linewidth=1)
    for week in year_changes:
        ax1.axvline(x=week, color='red', linestyle='--', linewidth=2)

    # Add year labels at year changes
    for week in year_changes:
        ax1.text(week, max(value for value in week_finals.values() if value is not None) * 1.1, str(week_times[week].year), ha='center', va='top', color='red', fontsize=12)

    # Add month labels at month changes
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for i in range(len(month_changes)):
        week = month_changes[i]
        next_week = month_changes[i + 1] if i + 1 < len(month_changes) else len(all_weeks)
        label_x = (week + next_week) / 2
        label_y = 10
        ax1.text(label_x, label_y, month_names[week_times[week].month - 1], ha='center', va='top', color='orange', fontsize=10)

    # Create the histogram for deposit and withdrawal
    deposits = {week: sum(balances) for week, balances in week_to_deposits.items() if balances}
    withdrawals = {week: sum(balances) for week, balances in week_to_withdrawals.items() if balances}
    ax2.bar(deposits.keys(), deposits.values(), color='green')
    ax2.bar(withdrawals.keys(), withdrawals.values(), color='red')
    for week, value in deposits.items():
        ax2.text(week, value, f'{value:.2f}', ha='center', va='bottom', fontsize=8)
    for week, value in withdrawals.items():
        ax2.text(week, value, f'{-value:.2f}', ha='center', va='top', fontsize=8)

    # Add total deposit and withdrawal amounts to the plot
    total_deposit = sum(deposits.values())
    total_withdrawal = sum(withdrawals.values())
    ax1.text(0, max(value for value in week_finals.values() if value is not None) * 1.1, f'Total deposit: {total_deposit:.2f}', ha='left', va='top', color='green', fontsize=48)
    ax1.text(0, max(value for value in week_finals.values() if value is not None) * 0.85, f'Total withdrawal: {-total_withdrawal:.2f}', ha='left', va='top', color='red', fontsize=48)

    # Save the plot
    plt.savefig(output_file)
