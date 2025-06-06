import unittest
import logging
import sqlite3
import sys
import types

# Provide a minimal ccxt stub so the module can be imported without the real
# dependency being installed during testing.
ccxt_stub = types.SimpleNamespace(
    mexc=lambda *args, **kwargs: None,
    InsufficientFunds=Exception,
    NetworkError=Exception,
)
sys.modules.setdefault("ccxt", ccxt_stub)

# Stub other optional dependencies that are not required for these tests
for mod in ["pandas", "numpy", "websocket"]:
    if mod == "pandas":
        stub = types.SimpleNamespace(Series=object, DataFrame=object)
    else:
        stub = types.SimpleNamespace()
    sys.modules.setdefault(mod, stub)

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "deepseek_python_20250606_a6dfb2",
    Path(__file__).resolve().parents[1] / "deepseek_python_20250606_a6dfb2.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
MEXCAdvancedTrader = module.MEXCAdvancedTrader


def create_trader():
    trader = MEXCAdvancedTrader.__new__(MEXCAdvancedTrader)
    trader.logger = logging.getLogger("test")
    trader.logger.addHandler(logging.NullHandler())
    trader.conn = sqlite3.connect(":memory:")
    trader.cursor = trader.conn.cursor()
    trader.cursor.execute(
        "CREATE TABLE signals (id INTEGER PRIMARY KEY, signal_type TEXT)"
    )
    trader.cursor.execute(
        """
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY,
            signal_id INTEGER,
            entry_price REAL NOT NULL,
            exit_time DATETIME,
            exit_price REAL,
            profit_loss REAL,
            status TEXT,
            position_size REAL
        )
        """
    )
    trader.conn.commit()
    return trader


class TestCloseTrade(unittest.TestCase):
    def test_pnl_buy(self):
        t = create_trader()
        t.cursor.execute("INSERT INTO signals (id, signal_type) VALUES (1, 'BUY')")
        t.cursor.execute(
            "INSERT INTO trades (id, signal_id, entry_price, position_size, status) VALUES (1, 1, 100, 0.5, 'open')"
        )
        t.conn.commit()
        t._close_trade(1, 110, 'manual')
        pnl = t.cursor.execute("SELECT profit_loss FROM trades WHERE id=1").fetchone()[0]
        self.assertAlmostEqual(pnl, (110 - 100) * 0.5)

    def test_pnl_sell(self):
        t = create_trader()
        t.cursor.execute("INSERT INTO signals (id, signal_type) VALUES (1, 'SELL')")
        t.cursor.execute(
            "INSERT INTO trades (id, signal_id, entry_price, position_size, status) VALUES (1, 1, 100, 0.5, 'open')"
        )
        t.conn.commit()
        t._close_trade(1, 90, 'manual')
        pnl = t.cursor.execute("SELECT profit_loss FROM trades WHERE id=1").fetchone()[0]
        self.assertAlmostEqual(pnl, (100 - 90) * 0.5)


if __name__ == '__main__':
    unittest.main()
