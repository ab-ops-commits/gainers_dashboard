# Build gainers dashboard data - Top 30 Daily/Weekly/Monthly gainers from Nifty 500
import json
import os
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# Nifty 500 tickers (yfinance format: SYMBOL.NS)
NIFTY500_TICKERS = [
 'RELIANCE.NS','TCS.NS','HDFCBANK.NS','BHARTIARTL.NS','ICICIBANK.NS',
 'INFOSYS.NS','SBIN.NS','HINDUNILVR.NS','ITC.NS','LT.NS',
 'HCLTECH.NS','KOTAKBANK.NS','AXISBANK.NS','BAJFINANCE.NS','ASIANPAINT.NS',
 'MARUTI.NS','TITAN.NS','ULTRACEMCO.NS','NESTLEIND.NS','WIPRO.NS',
 'NTPC.NS','POWERGRID.NS','SUNPHARMA.NS','TATAMOTORS.NS','ONGC.NS',
 'TATASTEEL.NS','TECHM.NS','COALINDIA.NS','HINDALCO.NS','ADANIENT.NS',
 'ADANIPORTS.NS','DRREDDY.NS','BAJAJFINSV.NS','CIPLA.NS','DIVISLAB.NS',
 'EICHERMOT.NS','BRITANNIA.NS','APOLLOHOSP.NS','HEROMOTOCO.NS','TATACONSUM.NS',
 'BPCL.NS','GRASIM.NS','INDUSINDBK.NS','JSWSTEEL.NS','M&M.NS',
 'SBILIFE.NS','HDFCLIFE.NS','ICICIGI.NS','PIDILITIND.NS','SIEMENS.NS',
 'ABB.NS','AMBUJACEM.NS','AUROPHARMA.NS','BAJAJ-AUTO.NS','BANKBARODA.NS',
 'BEL.NS','BERGEPAINT.NS','BOSCHLTD.NS','CANBK.NS','CHOLAFIN.NS',
 'COLPAL.NS','DMART.NS','DLF.NS','FEDERALBNK.NS','GAIL.NS',
 'GODREJCP.NS','GODREJPROP.NS','HAVELLS.NS','HDFCAMC.NS','HINDPETRO.NS',
 'ICICIPRULI.NS','IDFCFIRSTB.NS','IGL.NS','INDHOTEL.NS','IOC.NS',
 'IRCTC.NS','JUBLFOOD.NS','LICHSGFIN.NS','LUPIN.NS','MUTHOOTFIN.NS',
 'NAUKRI.NS','NHPC.NS','NMDC.NS','OFSS.NS','PERSISTENT.NS',
 'PETRONET.NS','PFC.NS','PNB.NS','POLYCAB.NS','RECLTD.NS',
 'SAIL.NS','SHRIRAMFIN.NS','SRF.NS','TATAPOWER.NS','TATACHEM.NS',
 'TORNTPHARM.NS','TORNTPOWER.NS','TRENT.NS','UPL.NS','VEDL.NS',
 'VOLTAS.NS','YESBANK.NS','ZOMATO.NS','HAL.NS','RVNL.NS',
 'IRFC.NS','CDSL.NS','BSE.NS','MCX.NS','ANGELONE.NS',
 'KPITTECH.NS','LTTS.NS','COFORGE.NS','LTIM.NS','MPHASIS.NS',
 'TATAELXSI.NS','APOLLOTYRE.NS','BALKRISIND.NS','CEATLTD.NS','MANAPPURAM.NS',
 'IIFL.NS','MAXHEALTH.NS','FORTIS.NS','LALPATHLAB.NS','METROPOLIS.NS',
 'KEC.NS','THERMAX.NS','CUMMINSIND.NS','SCHAEFFLER.NS','TIMKEN.NS',
 'ENDURANCE.NS','SUNDRMFAST.NS','MOTHERSON.NS','ZEEL.NS','SUNTV.NS',
 'ROUTE.NS','INDIAMART.NS','TANLA.NS','HAPPSTMNDS.NS','NEWGEN.NS',
 'ZENSAR.NS','PAGEIND.NS','PIIND.NS','NAVINFLUOR.NS','DEEPAKNTR.NS',
 'ASTRAL.NS','JKCEMENT.NS','RAMCOCEM.NS','DALBHARAT.NS','SHREECEMT.NS'
]

# Deduplicate
NIFTY500_TICKERS = list(dict.fromkeys(NIFTY500_TICKERS))
TOP_N = 30

def get_data(tickers):
 data = yf.download(tickers, period='2mo', interval='1d', group_by='ticker', auto_adjust=True)
 return data

def compute_returns(data, tickers):
 records = []
 for ticker in tickers:
 try:
 if ticker not in data or data[ticker].empty:
 continue
 df = data[ticker][['Close']].dropna()
 if len(df) < 5:
 continue
 close = df['Close']
 last = float(close.iloc[-1])
 daily = (last / float(close.iloc[-2]) - 1) * 100 if len(close) >= 2 else None
 weekly = (last / float(close.iloc[-6]) - 1) * 100 if len(close) >= 6 else None
 monthly = (last / float(close.iloc[-23]) - 1) * 100 if len(close) >= 23 else None
 sym = ticker.replace('.NS', '')
 records.append({
 'ticker': sym,
 'close': round(last, 2),
 'daily': round(daily, 2) if daily is not None else None,
 'weekly': round(weekly, 2) if weekly is not None else None,
 'monthly': round(monthly, 2) if monthly is not None else None
 })
 except Exception as e:
 print(f'Error {ticker}: {e}')
 return records

def top30(records, key):
 valid = [r for r in records if r.get(key) is not None and r[key] > 0]
 return sorted(valid, key=lambda x: x[key], reverse=True)[:TOP_N]

def make_gainers_list(top_records, key):
 result = []
 for r in top_records:
 result.append({
 'ticker': r['ticker'],
 'name': r['ticker'],
 'gain_pct': r[key],
 'close': r['close']
 })
 return result

def save_chart(ticker_ns, data, out_dir, period_label, sym):
 try:
 if ticker_ns not in data or data[ticker_ns].empty:
 return
 df = data[ticker_ns][['Close']].dropna()
 if len(df) < 5:
 return
 fig, ax = plt.subplots(figsize=(10, 4))
 ax.plot(df.index[-60:], df['Close'].iloc[-60:], color='#2196f3', linewidth=2)
 ax.fill_between(df.index[-60:], df['Close'].iloc[-60:], alpha=0.1, color='#2196f3')
 ax.set_title(f'{sym} - {period_label}', fontsize=13, color='#f1f5f9', pad=10)
 ax.set_facecolor('#0f172a')
 fig.patch.set_facecolor('#0f172a')
 ax.tick_params(colors='#64748b')
 ax.spines['bottom'].set_color('#334155')
 ax.spines['left'].set_color('#334155')
 ax.spines['top'].set_visible(False)
 ax.spines['right'].set_visible(False)
 ax.grid(True, linestyle='--', alpha=0.3, color='#334155')
 plt.tight_layout()
 fname = f'{sym}_{period_label.lower()}.png'
 plt.savefig(os.path.join(out_dir, fname), dpi=100, bbox_inches='tight')
 plt.close()
 except Exception as e:
 print(f'Chart error {ticker_ns} {period_label}: {e}')

def main():
 out_dir = 'data'
 charts_dir = os.path.join(out_dir, 'charts')
 os.makedirs(charts_dir, exist_ok=True)
 print(f'Fetching data for {len(NIFTY500_TICKERS)} tickers...')
 data = get_data(NIFTY500_TICKERS)
 print('Computing returns...')
 records = compute_returns(data, NIFTY500_TICKERS)
 print(f'Valid records: {len(records)}')
 daily_top = top30(records, 'daily')
 weekly_top = top30(records, 'weekly')
 monthly_top = top30(records, 'monthly')
 gainers = {
 'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M IST'),
 'total_stocks': len(records),
 'daily': make_gainers_list(daily_top, 'daily'),
 'weekly': make_gainers_list(weekly_top, 'weekly'),
 'monthly': make_gainers_list(monthly_top, 'monthly')
 }
 with open(os.path.join(out_dir, 'gainers.json'), 'w') as f:
 json.dump(gainers, f, indent=2)
 print('Saved gainers.json')
 # Generate period-specific charts
 periods = [('daily', daily_top), ('weekly', weekly_top), ('monthly', monthly_top)]
 all_chart_tasks = set()
 for period_label, top_list in periods:
 for r in top_list:
 all_chart_tasks.add((r['ticker'] + '.NS', period_label, r['ticker']))
 print(f'Generating {len(all_chart_tasks)} charts...')
 for ticker_ns, period_label, sym in all_chart_tasks:
 save_chart(ticker_ns, data, charts_dir, period_label, sym)
 print('Done.')

if __name__ == '__main__':
 main()
