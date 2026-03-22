from ib_insync import *

# Connect to IBKR
ib = IB()
ib.connect('127.0.0.1', 7497)

# Define SPX Option contract (ensure all fields are correct)
spx_option = Option(
                symbol="SPX",
                lastTradeDateOrContractMonth="20250414",
                strike=5415,
                right='C',
                exchange="SMART",
                currency="USD",
                multiplier='100'
            )

# Request contract details to validate
details = ib.reqContractDetails(spx_option)
if details:
    print(details)
    contract = details[0].contract
    print(contract)
    # Create a simple stop order without any extra parameters
    stop_order = StopOrder('BUY', 1, 25.50)

    # Place the order
    trade = ib.placeOrder(contract, stop_order)
    print(stop_order)
    print(trade)
    ib.sleep(2)
    print(f"Order status: {trade.orderStatus.status}")
else:
    print("Contract not found")