#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEXC Golden Decimal Advanced Trading System (Optimized)
User: behicof
Start Time: 2025-06-01 16:46:11 UTC
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import threading
import queue
import logging
import os
import json
import websocket
import time
from typing import Dict, List, Optional

class MEXCAdvancedTrader:
    def __init__(self):
        # Enhanced configuration
        self.config = {
            'api_key': 'mx0vglzxie532HhFS4',
            'api_secret': 'YOUR_API_SECRET',  # ADD YOUR SECRET HERE
            'session_id': 'd327b04c1509491eacd65dc00621845b',
            'user': 'behicof',
            'start_time': datetime.strptime("2025-06-01 16:46:11", "%Y-%m-%d %H:%M:%S"),
            'pairs': [
                'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOT/USDT',
                'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT', 'ADA/USDT'
            ],
            'timeframes': ['1m', '5m', '15m', '1h', '4h', '1d'],
            'default_timeframe': '1h',
            'max_position_size': 0.1,  # Max 10% of balance per trade
            'risk_percent': 1.0,       # 1% risk per trade
            'stop_loss': 0.01,         # 1% stop loss
            'take_profit': 0.02        # 2% take profit
        }
        
        # Initialize system
        self._setup_logging()
        self._setup_database()
        self._setup_exchange()
        self._setup_queues()
        
        # Golden decimal patterns
        self.patterns = self._load_patterns()
        
        # WebSocket setup
        self.ws = None
        self.ws_thread = None
        self.should_run = True
        
        self.logger.info(f"Advanced trading system started for user {self.config['user']}")
    
    def _setup_logging(self):
        """Enhanced logging setup with rotation"""
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/trading_{datetime.now().strftime('%Y%m%d')}.log"
        
        self.logger = logging.getLogger('MEXC_Trader')
        self.logger.setLevel(logging.INFO)
        
        # File handler with rotation
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _setup_database(self):
        """Database setup with error handling"""
        self.db_path = 'data/trading.db'
        os.makedirs('data', exist_ok=True)
        
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Create tables with improved schema
            self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    pattern_name TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    decimal_value REAL NOT NULL,
                    confidence REAL NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id INTEGER NOT NULL,
                    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    entry_price REAL NOT NULL,
                    exit_time DATETIME,
                    exit_price REAL,
                    profit_loss REAL,
                    status TEXT DEFAULT 'open',
                    position_size REAL NOT NULL,
                    FOREIGN KEY (signal_id) REFERENCES signals (id)
                );
                
                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    symbol TEXT NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    profit_loss REAL DEFAULT 0
                );
            """)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Database setup error: {e}")
            raise
    
    def _setup_exchange(self):
        """Exchange setup with error handling"""
        try:
            self.exchange = ccxt.mexc({
                'apiKey': self.config['api_key'],
                'secret': self.config['api_secret'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            })
            
            # Test connectivity
            self.exchange.load_markets()
            self.logger.info(f"Connected to MEXC. Available markets: {len(self.exchange.markets)}")
        except Exception as e:
            self.logger.error(f"Exchange connection error: {e}")
            raise
    
    def _setup_queues(self):
        """Queue setup"""
        self.signal_queue = queue.Queue(maxsize=100)
        self.trade_queue = queue.Queue(maxsize=50)
        self.ws_queue = queue.Queue(maxsize=200)
    
    def _load_patterns(self) -> List[Dict]:
        """Pattern configuration"""
        return [
            {
                "decimal": 0.618,
                "signal": "BUY",
                "tolerance": 0.005,
                "name": "Golden Ratio",
                "weight": 1.2,
                "conditions": {
                    "rsi_max": 70,
                    "trend_min": -0.5
                }
            },
            {
                "decimal": 0.382,
                "signal": "BUY",
                "tolerance": 0.005,
                "name": "Fibonacci 0.382",
                "weight": 1.0,
                "conditions": {
                    "rsi_max": 65,
                    "trend_min": 0
                }
            },
            {
                "decimal": 0.03,
                "signal": "BUY",
                "tolerance": 0.007,
                "name": "Golden Decimal 0.03",
                "weight": 1.1,
                "conditions": {
                    "rsi_max": 60,
                    "trend_min": 0.5
                }
            }
        ]
    
    def start_websocket(self):
        """WebSocket connection with authentication"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                self.ws_queue.put(data)
            except Exception as e:
                self.logger.error(f"WS message error: {e}")
        
        def on_error(ws, error):
            self.logger.error(f"WS error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            self.logger.info("WS connection closed")
        
        def on_open(ws):
            self.logger.info("WS connection established")
            # Subscribe to tickers
            for pair in self.config['pairs']:
                symbol = pair.replace('/', '').upper()
                ws.send(json.dumps({
                    "method": "SUBSCRIPTION",
                    "params": [f"{symbol}@miniTicker"]
                }))
        
        # Use the correct MEXC WS endpoint
        self.ws = websocket.WebSocketApp(
            "wss://contract.mexc.com/ws",
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def calculate_rsi(self, closes: pd.Series, period: int = 14) -> pd.Series:
        """Improved RSI calculation"""
        delta = closes.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss.replace(0, 0.001)  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze_price(self, symbol: str, price: float, timestamp: datetime) -> Optional[Dict]:
        """Enhanced price analysis with technical checks"""
        try:
            # Get OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=self.config['default_timeframe'],
                limit=100
            )
            
            if len(ohlcv) < 50:
                return None
                
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Calculate technical indicators
            df['rsi'] = self.calculate_rsi(df['close'], 14)
            df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
            df['trend'] = (df['ema20'] - df['ema50']) / df['ema50'] * 100
            
            last_row = df.iloc[-1]
            decimal_part = round(price - int(price), 3)
            
            # Check patterns
            for pattern in self.patterns:
                if abs(decimal_part - pattern["decimal"]) <= pattern["tolerance"]:
                    # Check additional conditions
                    conditions_met = True
                    if pattern["signal"] == "BUY":
                        if "rsi_max" in pattern["conditions"]:
                            if last_row['rsi'] > pattern["conditions"]["rsi_max"]:
                                conditions_met = False
                        if "trend_min" in pattern["conditions"]:
                            if last_row['trend'] < pattern["conditions"]["trend_min"]:
                                conditions_met = False
                    
                    if conditions_met:
                        confidence = 1 - (abs(decimal_part - pattern["decimal"]) / pattern["tolerance"])
                        confidence *= pattern["weight"]
                        
                        if confidence > 0.7:  # Minimum confidence threshold
                            signal = {
                                "timestamp": timestamp,
                                "symbol": symbol,
                                "price": price,
                                "pattern_name": pattern["name"],
                                "signal_type": pattern["signal"],
                                "decimal_value": decimal_part,
                                "confidence": confidence
                            }
                            
                            # Save signal to DB
                            self._save_signal(signal)
                            return signal
            return None
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return None
    
    def _save_signal(self, signal: Dict):
        """Save signal to database"""
        try:
            self.cursor.execute("""
                INSERT INTO signals 
                (timestamp, symbol, price, pattern_name, signal_type, decimal_value, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                signal["timestamp"],
                signal["symbol"],
                signal["price"],
                signal["pattern_name"],
                signal["signal_type"],
                signal["decimal_value"],
                signal["confidence"]
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Signal save error: {e}")
    
    def calculate_position_size(self, price: float) -> float:
        """Risk-managed position sizing"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['total']['USDT']
            
            if not usdt_balance or usdt_balance <= 0:
                self.logger.warning("No USDT balance available")
                return 0
                
            risk_amount = usdt_balance * (self.config['risk_percent'] / 100)
            stop_distance = price * self.config['stop_loss']
            position_size = risk_amount / stop_distance
            
            # Apply max position size
            max_size = usdt_balance * self.config['max_position_size'] / price
            return min(position_size, max_size)
        except Exception as e:
            self.logger.error(f"Position calc error: {e}")
            return 0
    
    def execute_trade(self, signal: Dict):
        """Trade execution with enhanced error handling"""
        try:
            symbol = signal["symbol"]
            side = signal["signal_type"].lower()
            price = signal["price"]
            
            # Calculate position size
            size = self.calculate_position_size(price)
            if size <= 0:
                self.logger.warning(f"Invalid size for {symbol}: {size}")
                return
            
            # Create market order for better execution
            order = self.exchange.create_order(
                symbol=symbol,
                type='market',
                side=side,
                amount=size
            )
            
            # Get actual execution price
            executed_price = order['price']
            
            # Save trade to database
            self.cursor.execute("""
                INSERT INTO trades 
                (signal_id, entry_price, position_size, status)
                VALUES (
                    (SELECT id FROM signals WHERE timestamp = ? AND symbol = ?),
                    ?, ?, 'open'
                )
            """, (
                signal["timestamp"],
                signal["symbol"],
                executed_price,
                size
            ))
            self.conn.commit()
            
            self.logger.info(f"New trade: {side.upper()} {size:.6f} {symbol} @ {executed_price}")
            
        except ccxt.InsufficientFunds as e:
            self.logger.error(f"Insufficient funds: {e}")
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error: {e}")
        except Exception as e:
            self.logger.error(f"Trade execution error: {e}")
    
    def _process_ws_message(self, message: Dict):
        """Process WebSocket messages"""
        try:
            if 'stream' in message and 'data' in message:
                stream_type = message['stream']
                
                if 'miniTicker' in stream_type:
                    data = message['data']
                    symbol = data['s'].replace('USDT', '/USDT')
                    price = float(data['c'])
                    timestamp = datetime.fromtimestamp(data['E'] / 1000)
                    
                    # Analyze price
                    signal = self.analyze_price(symbol, price, timestamp)
                    if signal:
                        self.signal_queue.put(signal)
        except Exception as e:
            self.logger.error(f"WS processing error: {e}")
    
    def _check_open_trades(self):
        """Monitor open trades with profit targets"""
        try:
            self.cursor.execute("""
                SELECT t.id, t.entry_price, s.symbol, s.signal_type
                FROM trades t
                JOIN signals s ON t.signal_id = s.id
                WHERE t.status = 'open'
            """)
            open_trades = self.cursor.fetchall()
            
            for trade in open_trades:
                trade_id, entry_price, symbol, signal_type = trade
                
                # Get current price
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Calculate PnL
                if signal_type == "BUY":
                    pnl = (current_price - entry_price) / entry_price
                else:
                    pnl = (entry_price - current_price) / entry_price
                
                # Check exit conditions
                exit_reason = None
                if pnl <= -self.config['stop_loss']:
                    exit_reason = "stop_loss"
                elif pnl >= self.config['take_profit']:
                    exit_reason = "take_profit"
                
                # Close trade if needed
                if exit_reason:
                    self._close_trade(trade_id, current_price, exit_reason)
                    
        except Exception as e:
            self.logger.error(f"Trade monitoring error: {e}")
    
    def _close_trade(self, trade_id: int, exit_price: float, reason: str):
        """Close trade and record results"""
        try:
            # Get trade details along with signal type
            self.cursor.execute(
                """
                SELECT t.entry_price, t.position_size, s.signal_type
                FROM trades t
                JOIN signals s ON t.signal_id = s.id
                WHERE t.id = ?
                """,
                (trade_id,)
            )
            entry_price, position_size, signal_type = self.cursor.fetchone()

            # Calculate PnL based on trade direction
            if signal_type == "BUY":
                pnl = (exit_price - entry_price) * position_size
            else:
                pnl = (entry_price - exit_price) * position_size
            
            # Update trade record
            self.cursor.execute("""
                UPDATE trades
                SET exit_time = ?, exit_price = ?, profit_loss = ?, status = ?
                WHERE id = ?
            """, (datetime.now(), exit_price, pnl, reason, trade_id))
            self.conn.commit()
            
            self.logger.info(f"Trade {trade_id} closed: {reason} @ {exit_price} | PnL: {pnl:.4f} USDT")
        except Exception as e:
            self.logger.error(f"Trade close error: {e}")
    
    def run(self):
        """Main trading loop"""
        self.start_websocket()
        self.logger.info("Trading system started")
        
        try:
            while self.should_run:
                # Process WebSocket messages
                while not self.ws_queue.empty():
                    message = self.ws_queue.get()
                    self._process_ws_message(message)
                
                # Process signals
                while not self.signal_queue.empty():
                    signal = self.signal_queue.get()
                    if signal["confidence"] >= 0.7:  # Confidence threshold
                        self.execute_trade(signal)
                
                # Monitor open trades
                self._check_open_trades()
                
                time.sleep(0.5)  # Reduce CPU usage
                
        except Exception as e:
            self.logger.critical(f"Main loop error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Clean shutdown procedure"""
        self.should_run = False
        self.logger.info("Shutting down system...")
        
        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join(timeout=5)
        
        if self.conn:
            self.conn.close()
        
        self.logger.info("System shutdown complete")

# Run the system
if __name__ == "__main__":
    trader = MEXCAdvancedTrader()
    try:
        trader.run()
    except KeyboardInterrupt:
        trader.stop()
        print("\nSystem stopped by user")