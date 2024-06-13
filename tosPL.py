import csv
from datetime import datetime
def adjust_balance_collect_data(file_path, initial_balance):
    balance = initial_balance
    tickers = {}
    # List to collect data for plotting
    plot_data = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)  # Convert the reader to a list to enable reversing
        rows.reverse()  # Process trades from bottom to top


        for row in rows:
            symbol = row['Symbol']
            qty = int(row['Qty'])  # Qty includes the correct sign as per the CSV
            price = float(row['Price'])
            exec_time = datetime.strptime(row['Exec Time'], '%m/%d/%y %H:%M:%S')

            if symbol not in tickers:
                tickers[symbol] = {'qty': 0, 'total_price': 0}

            tickers[symbol]['qty'] += qty
            tickers[symbol]['total_price'] -= qty * price  # Adjust the total price

            if tickers[symbol]['qty'] == 0:
                # When a position closes, record the P/L and the execution time
                pl = tickers[symbol]['total_price']
                balance += pl
                plot_data.append({"time": exec_time, "pl": round(pl,2)})

                # Reset the ticker's tracking after closing the position
                tickers[symbol] = {'qty': 0, 'total_price': 0}
                print(f"Trade for {symbol} at {exec_time.strftime('%Y-%m-%d %H:%M')}, Adjusted total P/L: ${pl:.2f}, New balance: ${balance:.2f}")

    return balance, plot_data

# Example usage:
file_path = 'new2.csv'
initial_balance = 30000
new_balance, plot_data = adjust_balance_collect_data(file_path, initial_balance)
print(f'Final account balance: ${new_balance:.2f}')




import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Assuming 'plot_data' is your list of dictionaries with 'time' and 'pl' from previous steps
df = pd.DataFrame(plot_data)
df['time'] = pd.to_datetime(df['time'])

# Extract just the time (hour and minute) part of the 'time' column for aggregation
df['time_of_day'] = df['time'].dt.strftime('%H:%M')

# Aggregate P/L by 'time_of_day'
aggregated_df = df.groupby('time_of_day')['pl'].sum().reset_index()

# Convert 'time_of_day' to a datetime object to facilitate extracting hours and minutes
# This is necessary for sorting the times correctly and possibly for plotting
# Ensure this conversion is done before trying to use 'time_of_day_dt'
aggregated_df['time_of_day_dt'] = pd.to_datetime(aggregated_df['time_of_day'], format='%H:%M')

# Directly calculate 'minutes_since_midnight' without dropping 'time_of_day_dt'
aggregated_df['minutes_since_midnight'] = aggregated_df['time_of_day_dt'].dt.hour * 60 + aggregated_df['time_of_day_dt'].dt.minute

# Calculate a moving average of the aggregated P/L values (e.g., over a 5-minute window)
window_size = 3
aggregated_df['moving_average'] = aggregated_df['pl'].rolling(window=window_size, min_periods=1).mean()

# Prepare for plotting by ensuring time labels are generated from 'time_of_day'
time_labels = aggregated_df['time_of_day'].unique()

# Plot setup
# Calculate the Exponential Moving Average (EMA) for a smoother line
# Adjust `span` for your desired responsiveness. A smaller span makes the EMA more responsive.
span = 9  # This is akin to the "window_size" for rolling averages but controls the decay in EMA
aggregated_df['ema_pl'] = aggregated_df['pl'].ewm(span=span, adjust=False).mean()

# Calculate the range of 'minutes_since_midnight'
min_minutes = aggregated_df['minutes_since_midnight'].min()
max_minutes = aggregated_df['minutes_since_midnight'].max()

# Generate a list of tick positions every 10 minutes within the range
tick_positions = np.arange(min_minutes, max_minutes + 1, 10)

# Generate corresponding tick labels for these positions
# Convert each position back to HH:MM format for labeling
tick_labels = [(pd.Timestamp('2024-01-01') + pd.Timedelta(minutes=int(minute))).strftime('%H:%M') for minute in tick_positions]

# Plot setup
plt.figure(figsize=(14, 7))


# Plotting the aggregated P/L values
plt.scatter(aggregated_df['minutes_since_midnight'], aggregated_df['pl'], color='red', marker='x', label='Aggregated P/L')

# Plotting the Exponential Moving Average (EMA) for a smoother line
plt.plot(aggregated_df['minutes_since_midnight'], aggregated_df['ema_pl'], color='blue', label='EMA of P/L')

# Add a horizontal line across the 0 point and vertical lines for each minute (as before)
plt.axhline(y=0, color='gray', linestyle='-', linewidth=1)

# Formatting the plot
plt.xlabel('Minutes Since Midnight')
plt.ylabel('Aggregated Profit/Loss ($)')
# Plotting the aggregated P/L values and EMA
# (Include your plotting code here)

# Adjusting x-axis ticks to show every 10 minutes
plt.xticks(ticks=tick_positions, labels=tick_labels, rotation=45)

# Formatting the plot (Include your formatting code here)
plt.xlabel('Time of Day')
plt.ylabel('Aggregated Profit/Loss ($)')
plt.title('Aggregated Profit/Loss by Time of Day Across All Days with EMA')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()