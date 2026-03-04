import json
import os
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

TICKERS = [
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
    'MAXHEALTH.NS','FORTIS.NS','LALPATHLAB.NS','METROPOLIS.NS',
    'KEC.NS','THERMAX.NS','CUMMINSIND.NS','SCHAEFFLER.NS','TIMKEN.NS',
    'ENDURANCE.NS','SUNDRMFAST.NS','MOTHERSON.NS','ZEEL.NS','SUNTV.NS',
    'ROUTE.NS','INDIAMART.NS','TANLA.NS','HAPPSTMNDS.NS','NEWGEN.NS',
    'ZENSAR.NS','PAGEIND.NS','PIIND.NS','NAVINFLUOR.NS','DEEPAKNTR.NS',
    'ASTRAL.NS','JKCEMENT.NS','RAMCOCEM.NS','DALBHARAT.NS','SHREECEMT.NS'
]

TICKERS = list(dict.fromkeys(TICKERS))
TOP_N = 30


def get_data(tickers):
    data = yf.download(tickers, period='2mo', interval='1d',
                       group_by='ticker', auto_adjust=True, progress=False)
    return data


def compute_returns(data, tickers):
    records = []
    for ticker in tickers:
        try:
            if ticker not in data:
                continue
            df = data[ticker][['Close']].dropna()
            if len(df) < 5:
                continue
            close = df['Close']
            last = float(close.iloc[-1])
            daily = None
            weekly = None
            monthly = None
            if len(close) >= 2:
                daily = round((last / float(close.iloc[-2]) - 1) * 100, 2)
            if len(close) >= 6:
                weekly = round((last / float(close.iloc[-6]) - 1) * 100, 2)
            if len(close) >= 23:
                monthly = round((last / float(close.iloc[-23]) - 1) * 100, 2)
            sym = ticker.replace('.NS', '')
            records.append({
                'ticker': sym,
                'close': round(last, 2),
                'daily': daily,
                'weekly': weekly,
                'monthly': monthly
            })
        except Exception as exc:
            print('Error {}: {}'.format(ticker, exc))
    return records


def top30(records, key):
    valid = [r for r in records if r.get(key) is not None and r[key] > 0]
    return sorted(valid, key=lambda x: x[key], reverse=True)[:TOP_N]


def make_list(top_records, key):
    result = []
    for r in top_records:
        result.append({
            'ticker': r['ticker'],
            'name': r['ticker'],
            'gain_pct': r[key],
            'close': r['close']
        })
    return result


def save_chart(ticker_ns, data, charts_dir, period, sym):
    try:
        if ticker_ns not in data:
            return
        df = data[ticker_ns][['Close']].dropna()
        if len(df) < 5:
            return
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df.index[-60:], df['Close'].iloc[-60:], color='#2196f3', linewidth=2)
        ax.fill_between(df.index[-60:], df['Close'].iloc[-60:], alpha=0.1, color='#2196f3')
        ax.set_title('{} - {}'.format(sym, period), fontsize=13, color='#f1f5f9', pad=10)
        ax.set_facecolor('#0f172a')
        fig.patch.set_facecolor('#0f172a')
        ax.tick_params(colors='#64748b')
        ax.spines['bottom'].set_color('#334155')
        ax.spines['left'].set_color('#334155')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, linestyle='--', alpha=0.3, color='#334155')
        plt.tight_layout()
        fname = '{}_{}.png'.format(sym, period)
        plt.savefig(os.path.join(charts_dir, fname), dpi=100, bbox_inches='tight')
        plt.close()
    except Exception as exc:
        print('Chart error {} {}: {}'.format(ticker_ns, period, exc))


def main():
    out_dir = 'data'
    charts_dir = os.path.join(out_dir, 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    print('Fetching data for {} tickers...'.format(len(TICKERS)))
    data = get_data(TICKERS)
    print('Computing returns...')
    records = compute_returns(data, TICKERS)
    print('Valid records: {}'.format(len(records)))
    daily_top = top30(records, 'daily')
    weekly_top = top30(records, 'weekly')
    monthly_top = top30(records, 'monthly')
    gainers = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M IST'),
        'total_stocks': len(records),
        'daily': make_list(daily_top, 'daily'),
        'weekly': make_list(weekly_top, 'weekly'),
        'monthly': make_list(monthly_top, 'monthly')
    }
    with open(os.path.join(out_dir, 'gainers.json'), 'w') as f:
        json.dump(gainers, f, indent=2)
    print('Saved gainers.json')
    chart_tasks = []
    for period, top_list in [('daily', daily_top), ('weekly', weekly_top), ('monthly', monthly_top)]:
        for r in top_list:
            chart_tasks.append((r['ticker'] + '.NS', period, r['ticker']))
    print('Generating {} charts...'.format(len(chart_tasks)))
    for ticker_ns, period, sym in chart_tasks:
        save_chart(ticker_ns, data, charts_dir, period, sym)
    print('Done.')


if __name__ == '__main__':
    main()
