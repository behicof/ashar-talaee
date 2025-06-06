# MEXC Golden Decimal Advanced Trading System
سیستم معاملاتی هوشمند، قدرتمند و دقیق، مبتنی بر تحلیل اعشارهای طلایی در بازار رمزارز  
*A smart, robust, and precise trading system based on golden decimal analysis for the cryptocurrency market*

---

## 📖 معرفی | Introduction

**فارسی:**  
این پروژه یک سیستم معاملاتی پیشرفته است که با بهره‌گیری از تحلیل اعشارهای طلایی (Golden Decimals) و الگوریتم‌های تکنیکال، سیگنال‌های خرید و فروش را در بازار رمزارز به‌صورت خودکار تولید، ثبت و مدیریت می‌کند.  
ویژگی اصلی این سیستم، شناسایی نقاط حساس قیمتی بر اساس الگوهای اعشاری و تایید با ابزارهایی نظیر RSI، EMA و مدیریت ریسک است.

**English:**  
This project is an advanced trading system that leverages golden decimal analysis and technical algorithms to automatically generate, record, and manage buy/sell signals in the crypto market.  
Its main feature is the detection of key price points based on fractional (decimal) patterns, validated by tools such as RSI, EMA, and risk management modules.

---

## 🚀 ویژگی‌ها | Features

- تحلیل و شناسایی خودکار الگوهای اعشار طلایی (Golden Decimals)
- یکپارچه با صرافی MEXC با استفاده از CCXT
- مدیریت سیگنال‌ها و معاملات در پایگاه داده SQLite
- پشتیبانی از چندین جفت‌ارز و تایم‌فریم (BTC, ETH, SOL, ...)
- محاسبه حجم معامله بر اساس مدیریت ریسک
- ثبت کامل عملکرد (Performance Tracking)
- اتصال بلادرنگ با WebSocket
- گزارش‌گیری و لاگ حرفه‌ای
- توسعه‌پذیر و قابل شخصی‌سازی
- مستندات کامل و کدنویسی تمیز (Clean Code & Docs)

---

## ⚡ نصب و راه‌اندازی سریع | Quick Start

```bash
git clone https://github.com/behicof/mexc-golden-decimal-trader.git
cd mexc-golden-decimal-trader
pip install -r requirements.txt
# فایل config را ویرایش کرده و کلید API خود را وارد کنید
python main.py
```

- نیازمند Python 3.8+
- قبل از اجرا، دسترسی به API صرافی MEXC را فعال کنید.

---

## 📁 ساختار فایل‌ها | File Structure

```
mexc-golden-decimal-trader/
├── main.py                 # هسته سیستم معاملاتی
├── requirements.txt        # وابستگی‌ها
├── data/                   # دیتابیس SQLite و داده‌های ذخیره‌شده
├── logs/                   # لاگ‌ها
├── README.md               # همین فایل
└── ...                     # سایر ماژول‌ها و ابزارها
```

---

## 🏆 لایسنس | License

این پروژه تحت لایسنس MIT منتشر شده است.  
This project is released under the MIT License.

---

## 👤 درباره نویسنده | About the Author

**بهروز بوذری (behrouzboozari)**  
بنیان‌گذار و طراح سیستم‌های معاملاتی پیشرفته  
_مهارت‌ها:_ Python, CCXT, SQLite, WebSocket, تحلیل تکنیکال، مدل‌سازی اعشاری  
_شعار:_ «هر روز یک قدم به سمت هوشمندی بیشتر!»

[GitHub](https://github.com/behicof)

---

## 💎 پروژه‌های شاخص | Featured Projects

1. **MEXC Golden Decimal Advanced Trading System** *(این پروژه)*
2. ... (در صورت تمایل می‌توانید پروژه‌های دیگر را اضافه کنید)

---

<div align="center">
  
  ⭐️ اگر این پروژه برای شما مفید بود، ستاره بدهید و سوالات یا پیشنهادات خود را در Issues مطرح کنید!  
  <br/><br/>
  <img src="https://img.shields.io/github/license/behicof/mexc-golden-decimal-trader?style=flat-square" alt="MIT License"/>
  <img src="https://img.shields.io/badge/made%20with-python-blue?style=flat-square" alt="Python"/>
</div>