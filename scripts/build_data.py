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
# Using a broad list of liquid NSE stocks
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
    'ABB.NS','ADANIGREEN.NS','ADANIPOWER.NS','AMBUJACEM.NS','AUROPHARMA.NS',
    'BAJAJ-AUTO.NS','BANKBARODA.NS','BEL.NS','BERGEPAINT.NS','BOSCHLTD.NS',
    'CANBK.NS','CHOLAFIN.NS','COLPAL.NS','DMART.NS','DLF.NS',
    'ESCORTS.NS','FEDERALBNK.NS','GAIL.NS','GODREJCP.NS','GODREJPROP.NS',
    'HAVELLS.NS','HDFCAMC.NS','HINDPETRO.NS','ICICIPRULI.NS','IDFCFIRSTB.NS',
    'IGL.NS','INDHOTEL.NS','INDUSTOWER.NS','INFY.NS','IOC.NS',
    'IRCTC.NS','JINDALSTEL.NS','JUBLFOOD.NS','LICHSGFIN.NS','LODHA.NS',
    'LTI.NS','LTIM.NS','LUPIN.NS','MCDOWELL-N.NS','MFSL.NS',
    'MOTHERSON.NS','MPHASIS.NS','MRF.NS','MUTHOOTFIN.NS','NAUKRI.NS',
    'NBCC.NS','NHPC.NS','NMDC.NS','OBEROIRLTY.NS','OFSS.NS',
    'PAGEIND.NS','PEL.NS','PERSISTENT.NS','PETRONET.NS','PFC.NS',
    'PHOENIXLTD.NS','PIIND.NS','PNB.NS','POLYCAB.NS','PVR.NS',
    'RECLTD.NS','SAIL.NS','SHRIRAMFIN.NS','SRF.NS','STAR.NS',
    'SUPREMEIND.NS','TATACOMM.NS','TATAELXSI.NS','TATAPOWER.NS','TATACHEM.NS',
    'TORNTPHARM.NS','TORNTPOWER.NS','TRENT.NS','TRIDENT.NS','UBL.NS',
    'UNIONBANK.NS','UPL.NS','VEDL.NS','VOLTAS.NS','WHIRLPOOL.NS',
    'YESBANK.NS','ZOMATO.NS','PAYTM.NS','NYKAA.NS','POLICYBZR.NS',
    'DELHIVERY.NS','RVNL.NS','IRFC.NS','RAILVIKAS.NS','HAL.NS',
    'BDL.NS','COCHINSHIP.NS','MAZAGON.NS','GRSE.NS','BEML.NS',
    'KALYANKJIL.NS','SENCO.NS','TITAN.NS','PCJEWELLER.NS','RAJESHEXPO.NS',
    'HSCL.NS','GMDCLTD.NS','NATIONALUM.NS','RATNAMANI.NS','JSWENERGY.NS',
    'CESC.NS','TATAPOWER.NS','RPOWER.NS','ADANIENSOL.NS','GREENPANEL.NS',
    'CENTURYPLY.NS','PLYCEM.NS','SHREECEMT.NS','RAMCOCEM.NS','DALBHARAT.NS',
    'JKCEMENT.NS','HEIDELBERG.NS','STARCEMENT.NS','KAJARIACER.NS','SOMANY.NS',
    'ASTRAL.NS','SUPREMEIND.NS','FINOLEX.NS','NILKAMAL.NS','ATUL.NS',
    'NAVINFLUOR.NS','DEEPAKNTR.NS','NOCIL.NS','NEOGEN.NS','CLEAN.NS',
    'LALPATHLAB.NS','METROPOLIS.NS','THYROCARE.NS','KIMS.NS','SYNGENE.NS',
    'MAXHEALTH.NS','RAINBOW.NS','NARAYANA.NS','FORTIS.NS','MEDANTA.NS',
    'INDIGRID.NS','POWERMECH.NS','KEC.NS','KALPATPOWR.NS','ENGINERSIN.NS',
    'THERMAX.NS','CUMMINSIND.NS','GRINDWELL.NS','TIMKEN.NS','SCHAEFFLER.NS',
    'SKFINDIA.NS','SUPRAJIT.NS','ENDURANCE.NS','MINDACORP.NS','FIEM.NS',
    'SUNDRMFAST.NS','BALKRISIND.NS','APOLLOTYRE.NS','CEATLTD.NS','MRF.NS',
    'MAHSEAMLES.NS','MANAPPURAM.NS','IIFL.NS','M&MFIN.NS','BAJAJHLDNG.NS',
    'CHOLAHLDNG.NS','EDELWEISS.NS','5PAISA.NS','ANGELONE.NS','CDSL.NS',
    'BSE.NS','MCX.NS','CAMS.NS','KFINTECH.NS','NSDL.NS',
    'ZEEL.NS','SUNTV.NS','PVRINOX.NS','SAREGAMA.NS','NAZARA.NS',
    'ROUTE.NS','INDIAMART.NS','JUSTDIAL.NS','CARTRADE.NS','EASEMYTRIP.NS',
    'IXIGO.NS','MAPMYINDIA.NS','LATENTVIEW.NS','INTELLECT.NS','KPITTECH.NS',
    'LTTS.NS','COFORGE.NS','MASTEK.NS','QUICKHEAL.NS','RATEGAIN.NS',
    'TANLA.NS','HAPPSTMNDS.NS','NEWGEN.NS','ZENSAR.NS','SONATSOFTW.NS'
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
            # Daily return: today vs yesterday
            daily = (last / float(close.iloc[-2]) - 1) * 100 if len(close) >= 2 else None
            # Weekly return: today vs ~5 trading days ago
            weekly = (last / float(close.iloc[-6]) - 1) * 100 if len(close) >= 6 else None
            # Monthly return: today vs ~22 trading days ago
            monthly = (last / float(close.iloc[-23]) - 1) * 100 if len(close) >= 23 else None
            sym = ticker.replace('.NS', '')
            records.append({
                'ticker': sym,
                'last_price': round(last, 2),
                'daily': round(daily, 2) if daily is not None else None,
                'weekly': round(weekly, 2) if weekly is not None else None,
                'monthly': round(monthly, 2) if monthly is not None else None
            })
        except Exception as e:
            print(f'Error {ticker}: {e}')
    return records

def top30(records, key):
    valid = [r for r in records if r.get(key) is not None]
    return sorted(valid, key=lambda x: x[key], reverse=True)[:TOP_N]

def save_chart(ticker_ns, data, out_dir):
    try:
        if ticker_ns not in data or data[ticker_ns].empty:
            return
        df = data[ticker_ns][['Close']].dropna()
        if len(df) < 5:
            return
        sym = ticker_ns.replace('.NS', '')
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df.index[-60:], df['Close'].iloc[-60:], color='#2196f3', linewidth=2)
        ax.set_title(f'{sym} - Last 60 Days', fontsize=13, color='#f1f5f9', pad=10)
        ax.set_facecolor('#0f172a')
        fig.patch.set_facecolor('#0f172a')
        ax.tick_params(colors='#64748b')
        ax.spines['bottom'].set_color('#334155')
        ax.spines['left'].set_color('#334155')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, linestyle='--', alpha=0.3, color='#334155')
        ax.xaxis.label.set_color('#64748b')
        ax.yaxis.label.set_color('#64748b')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f'{sym}.png'), dpi=100, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f'Chart error {ticker_ns}: {e}')

def main():
    out_dir = 'data'
    charts_dir = os.path.join(out_dir, 'charts')
    os.makedirs(charts_dir, exist_ok=True)

    print(f'Fetching data for {len(NIFTY500_TICKERS)} tickers...')
    data = get_data(NIFTY500_TICKERS)

    print('Computing returns...')
    records = compute_returns(data, NIFTY500_TICKERS)
    print(f'Valid records: {len(records)}')

    snapshot = {
        'daily': top30(records, 'daily'),
        'weekly': top30(records, 'weekly'),
        'monthly': top30(records, 'monthly')
    }

    with open(os.path.join(out_dir, 'snapshot.json'), 'w') as f:
        json.dump(snapshot, f, indent=2)

    with open(os.path.join(out_dir, 'meta.json'), 'w') as f:
        json.dump({'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'total_stocks': len(records)}, f, indent=2)

    # Generate charts only for stocks that appear in any top30 list
    chart_tickers = set()
    for lst in snapshot.values():
        for r in lst:
            chart_tickers.add(r['ticker'] + '.NS')

    print(f'Generating {len(chart_tickers)} charts...')
    for t in chart_tickers:
        save_chart(t, data, charts_dir)

    print('Done.')

if __name__ == '__main__':
    main()
