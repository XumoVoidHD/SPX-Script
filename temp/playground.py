from new_broker import IBTWSAPI
import credentials
import asyncio
from ib_insync import *
import nest_asyncio
from datetime import datetime
from pytz import timezone
from discord_bot import send_discord_message
import os
import logging
import time


def setup_logging():
    os.makedirs('logs', exist_ok=True)

    eastern = timezone('US/Eastern')
    current_date = datetime.now(eastern).strftime('%Y-%m-%d')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(f'logs/strategy_log_{current_date}.txt', mode='w'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


nest_asyncio.apply()

creds = {
    "host": credentials.host,
    "port": credentials.port,
    "client_id": 14
}


class Strategy:

    def __init__(self):
        self.call_rentry = None
        self.should_continue = None
        self.call_stp_id = None
        self.atm_call_sl = None
        self.atm_call_fill = None
        self.call_contract = None
        self.call_order_placed = None
        self.call_target_price = None
        self.call_percent = None
        self.broker = IBTWSAPI(creds=creds)
        self.enable_logging = credentials.enable_logging
        self.logger = setup_logging() if self.enable_logging else None

    async def dprint(self, phrase):
        print(phrase)
        if self.enable_logging:
            self.logger.info(phrase)
        await send_discord_message(phrase)

    async def lprint(self,phrase):
        if self.enable_logging:
            self.logger.info(phrase)


    async def main(self):
        await send_discord_message("." * 100)
        await self.dprint("\n1. Testing connection...")
        await self.broker.connect()
        await self.dprint(f"Connection status: {self.broker.is_connected()}")
        self.call_contract = Option(
            symbol="SPX",
            lastTradeDateOrContractMonth="20250414",
            strike=5400,
            right='C',
            exchange="SMART",
            currency="USD",
            multiplier='100'
        )
        # open_trades = await self.broker.get_positions()
        # call_exists = any(
        #     trade.contract.secType == 'OPT' and trade.contract.right == 'C' and trade.contract.symbol == "SPX"
        #     for trade in open_trades
        # )
        #
        # print(open_trades[0])

        premium_price = await self.broker.get_latest_premium_price(
            symbol="SPX",
            expiry="20250429",
            strike=5500,
            right="P"
        )

        print(premium_price)

    async def place_atm_call_order(self):
        premium_price = await self.broker.get_latest_premium_price(
            symbol=credentials.instrument,
            expiry=credentials.date,
            strike=self.call_target_price,
            right="C"
        )
        self.call_contract = Option(
            symbol=credentials.instrument,
            lastTradeDateOrContractMonth=credentials.date,
            strike=self.call_target_price,
            right='C',
            exchange="SMART",
            currency="USD",
            multiplier='100'
        )

        qualified_contracts = self.broker.client.qualifyContracts(self.call_contract)
        if not qualified_contracts:
            raise ValueError("Failed to qualify contract with IBKR.")
        print('last price is', premium_price['last'])

        try:
            k = await self.broker.place_market_order(contract=self.call_contract, qty=credentials.call_position,
                                                     side="SELL")
            self.call_order_placed = True
            self.atm_call_fill = k[1]
            self.call_contract = self.call_contract
            self.atm_call_sl = self.atm_call_fill * (1 + (self.call_percent / 100))
            await self.dprint(f"Call Order placed at {k[1]}")
            self.call_stp_id = await self.broker.place_stp_order(contract=self.call_contract, side="BUY",quantity=credentials.call_position, sl=self.atm_call_sl)
        except Exception as e:
            await self.dprint(f"Error in placing sell side call order: {str(e)}")

    async def call_check(self):
        temp_percentage = 1 - (credentials.call_entry_price_changes_by / 100)
        while self.should_continue:
            if self.call_order_placed:
                premium_price = await self.broker.get_latest_premium_price(
                    symbol=credentials.instrument,
                    expiry=credentials.date,
                    strike=self.call_target_price,
                    right="C"
                )

                if temp_percentage <= 0:
                    continue

                if premium_price['mid'] <= temp_percentage * self.atm_call_fill:
                    self.atm_call_sl = self.atm_call_sl - (self.atm_call_fill * (credentials.call_change_sl_by / 100))
                    await self.dprint(
                        f"[CALL] Price dip detected - Adjusting trailing parameters"
                        f"\nFill Price: {self.atm_call_fill}"
                        f"\nCurrent Premium: {premium_price['mid']}"
                        f"\nDip Threshold: {temp_percentage * self.atm_call_fill}"
                        f"\nOld Temp %: {temp_percentage:.2%}"
                        f"\nNew Temp %: {(temp_percentage - credentials.call_entry_price_changes_by / 100):.2%}"
                        f"\nNew SL: {self.atm_call_sl}"
                    )
                    await self.broker.modify_stp_order(contract=self.call_contract, side="BUY",
                                                       quantity=credentials.call_position, sl=self.atm_call_sl,
                                                       order_id=self.call_stp_id)

                    temp_percentage -= credentials.call_entry_price_changes_by / 100
                    if temp_percentage < 0:
                        temp_percentage = 0
                        await self.dprint(f"Put trailing sl is at {temp_percentage}")
                    continue

                await asyncio.sleep(1)
            else:
                premium_price = await self.broker.get_latest_premium_price(
                    symbol=credentials.instrument,
                    expiry=credentials.date,
                    strike=self.call_target_price,
                    right="C"
                )

                if premium_price['mid'] <= self.atm_call_fill and self.call_rentry < credentials.number_of_re_entry:
                    await self.dprint(
                        f"[CALL] Entry condition met - Initiating new position"
                        f"\nCurrent Premium: {premium_price['mid']}"
                        f"\nEntry Price: {self.atm_call_fill}"
                        f"\nStrike Price: {self.call_target_price}"
                        f"\nReentry Count: {self.call_rentry + 1}"
                    )
                    self.call_rentry += 1
                    await self.dprint(f"Number of re-entries happened: {self.call_rentry}")
                    # await self.place_hedge_orders(call=True, put=False)
                    await self.place_atm_call_order()
                    temp_percentage = 1 - (credentials.put_entry_price_changes_by / 100)
                    self.call_order_placed = True
                    continue

                if not self.call_rentry < credentials.number_of_re_entry:
                    await self.dprint("Call re-entry limit reached")
                    return

                await asyncio.sleep(5)




if __name__ == "__main__":
    s = Strategy()
    asyncio.run(s.main())
