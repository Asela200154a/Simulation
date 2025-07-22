import pandas as pd
from datetime import datetime

# Load the trades data (assuming the CSV content is copied into a file named 'Trades-Summary - Sheet1.csv')
df = pd.read_csv('Trades-Summary - Sheet1.csv', skiprows=2)  # Skip header rows
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')

# Sort trades by date and time
df = df.sort_values('DateTime').reset_index(drop=True)

# FTMO rules
INITIAL_BALANCE = 10000
MAX_LOSS = 1000  # 10% of initial balance
MAX_DAILY_LOSS = 500  # 5% of initial balance
RISK_PERCENTAGE = 0.01  # 1% risk per trade

# RRRs to simulate
RRRs = [1.2, 1.5, 2, 2.5, 3]

# Function to simulate account growth for a given RRR
def simulate_ftmo_account(df, rrr):
    balance = INITIAL_BALANCE
    monthly_balances = {}
    current_day = None
    day_start_balance = INITIAL_BALANCE
    
    for index, row in df.iterrows():
        date = row['DateTime']
        day = date.date()
        month_key = date.strftime('%Y-%m')
        
        # New day: reset daily loss tracking
        if current_day != day:
            current_day = day
            day_start_balance = balance
        
        # Calculate risk amount (R)
        R = balance * RISK_PERCENTAGE
        
        # Determine trade outcome for this RRR
        rrr_col = str(rrr)
        if row[rrr_col] == 'hit':
            profit = R * rrr
        else:
            profit = -R
        
        # Update balance
        balance += profit
        
        # Check FTMO rules
        if balance < (INITIAL_BALANCE - MAX_LOSS):
            print(f"RRR {rrr}: Account breached at trade {row['Trades']} on {date}. Balance: ${balance:.2f}")
            monthly_balances[month_key] = (balance, (balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100)
            break
        
        if balance < (day_start_balance - MAX_DAILY_LOSS):
            print(f"RRR {rrr}: Daily loss limit breached at trade {row['Trades']} on {date}. Balance: ${balance:.2f}")
            monthly_balances[month_key] = (balance, (balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100)
            break
        
        # Record balance at end of month
        monthly_balances[month_key] = (balance, (balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100)
    
    return monthly_balances

# Run simulations for each RRR
results = {}
for rrr in RRRs:
    print(f"\nSimulation for RRR = {rrr}")
    results[rrr] = simulate_ftmo_account(df, rrr)
    
    # Display monthly growth
    print(f"{'Month':<10} {'Balance':<12} {'Growth %':<10}")
    print("-" * 32)
    for month, (bal, growth) in results[rrr].items():
        print(f"{month:<10} ${bal:<11.2f} {growth:.2f}%")