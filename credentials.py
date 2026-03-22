# Default Values #close_hedges
port = 7497
host = "127.0.0.1"
data_type = 4
instrument = "XSP"
exchange = "CBOE"
currency = "USD"
close_positions = False
enable_logging = False
calc_values = True
active_close_hedges = True
close_hedges = True
# if active_close_hedges is false then don't open the hedges at all if true
# And close_hedges is true then close and open hedges accordingly
# And if close-hedges is False then just open the hedges but don't close them
WEBHOOK_URL = "https://discord.com/api/webhooks/1338550862922125382/ngLa-LmVaolmdMDeNV4f4jTEhzhCJwvZXsSrpHiYcZmWIhYEQ9ef4elRQB0Kf1PmYG5B"

# Changeable Values
date = "20251210"                   # Date of contract (YYYY-MM-DD)
number_of_re_entry = 1              # Specifies the number of re-entries allowed
OTM_CALL_HEDGE = 2                # How far away the call hedge is (10 means that its $50 away from current price)
OTM_PUT_HEDGE = 2                 # How far away the put hedge is (10 means that its $50 away from current price)
ATM_CALL = 5                        # How far away call position is (2 means that its $10 away from current price)
ATM_PUT = 5                         # How far away put position is (2 means that its $10 away from current price)
call_sl = 1                        # From where the call stop loss should start from (15 here means 15% of entry price)
call_entry_price_changes_by = 5     # What % should call entry premium price should change by to update the trailing %
call_change_sl_by = 5               # What % of entry price should call sl change when trailing stop loss updates
put_sl = 1                         # From where the put stop loss should start from (15 here means 15% of entry price)
put_entry_price_changes_by = 5      # What % should put entry premium price should change by to update the trailing %
put_change_sl_by = 5                # What % of entry price should put sl change when trailing stop loss updates
conversion_time = 10                # Deprecated (No use)
entry_hour = 9                      # Entry time in hours
entry_minute = 40                   # Entry time in minutes
entry_second = 00                    # Entry time in seconds
exit_hour = 10                     # Exit time in hours
exit_minute = 15                  # Exit time in minutes
exit_second = 00                     # Exit time in seconds
call_hedge_quantity = 1             # Quantity for call hedge
put_hedge_quantity = 1              # Quantity for put hedge
call_position = 1                   # Quantity for call position
put_position = 1                    # Quantity for put position
call_hedge = 5400
call_strike = 5415
put_hedge = 5350
put_strike = 5405
call_check_time = 1
call_reentry_time = 5
put_check_time = 1
put_reentry_time = 5
