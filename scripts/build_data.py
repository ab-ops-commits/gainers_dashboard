import json
import os
import yfinance as yf
import numpy as np
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

BENCHMARK = '^NSEI'
TICKERS = list(dict.fromkeys(TICKERS))
TOP_N = 30
ATR_PERIOD = 14
RS_BARS = 20


def get_data(tickers):
    all_syms = tickers + [BENCHMARK]
    data = yf.download(all_syms, period='3mo', interval='1d',
                       group_by='ticker', auto_adjust=True, progress=False)
    return data


def calc_atr(df, period=14):
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    tr = np.maximum(high - low,
         np.maximum(abs(high - prev_close), abs(low - prev_close)))
    atr = tr.rolling(period).mean()
    return atr


def assign_grade(rs_score):
    if rs_score >= 80:
        return 'A+'
    elif rs_score >= 65:
        return 'A'
    elif rs_score >= 50:
        return 'B'
    elif rs_score >= 35:
        return 'C'
    else:
        return 'D'


def compute_records(data, tickers):
    # Get benchmark close series
    bench_close = None
    try:
        if BENCHMARK in data and not data[BENCHMARK].empty:
            bench_df = data[BENCHMARK][['Close']].dropna()
            bench_close = bench_df['Close']
    except Exception:
        pass

    records = []
    for ticker in tickers:
        try:
            if ticker not in data:
                continue
            df = data[ticker][['High', 'Low', 'Close']].dropna()
            if len(df) < 25:
                continue
            close = df['Close']
            last = float(close.iloc[-1])

            # Returns
            day_pct = round((last / float(close.iloc[-2]) - 1) * 100, 2) if len(close) >= 2 else None
            d5_pct = round((last / float(close.iloc[-6]) - 1) * 100, 2) if len(close) >= 6 else None
            d20_pct = round((last / float(close.iloc[-21]) - 1) * 100, 2) if len(close) >= 21 else None
            monthly_pct = round((last / float(close.iloc[-23]) - 1) * 100, 2) if len(close) >= 23 else None

            # ATR%
            atr_series = calc_atr(df, ATR_PERIOD)
            atr_val = float(atr_series.iloc[-1]) if not np.isnan(atr_series.iloc[-1]) else None
            atr_pct = round(atr_val / last * 100, 2) if atr_val and last > 0 else None

            # RS vs benchmark (ratio of stock to benchmark, normalised over RS_BARS)
            rs_vals = None
            rs_score = 50
            if bench_close is not None and len(bench_close) >= RS_BARS:
                aligned = close.reindex(bench_close.index).dropna()
                b_aligned = bench_close.reindex(aligned.index).dropna()
                common_idx = aligned.index.intersection(b_aligned.index)
                if len(common_idx) >= RS_BARS:
                    s = aligned[common_idx]
                    b = b_aligned[common_idx]
                    ratio = (s / b).iloc[-RS_BARS:]
                    ratio_norm = ((ratio - ratio.min()) / (ratio.max() - ratio.min() + 1e-10) * 100)
                    rs_vals = [round(float(v), 1) for v in ratio_norm.values]
                    rs_score = round(float(ratio_norm.iloc[-1]), 1)

            grade = assign_grade(rs_score)

            sym = ticker.replace('.NS', '')
            records.append({
                'ticker': sym,
                'close': round(last, 2),
                'day_pct': day_pct,
                'daily': day_pct,
                'd5_pct': d5_pct,
                'weekly': d5_pct,
                'd20_pct': d20_pct,
                'monthly': monthly_pct,
                'atr_pct': atr_pct,
                'rs_score': rs_score,
                'rs_vals': rs_vals if rs_vals else [],
                'grade': grade
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
            'close': r['close'],
            'day_pct': r.get('day_pct'),
            'd5_pct': r.get('d5_pct'),
            'd20_pct': r.get('d20_pct'),
            'atr_pct': r.get('atr_pct'),
            'grade': r.get('grade', 'C'),
            'rs_score': r.get('rs_score', 50),
            'rs_vals': r.get('rs_vals', [])
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
    print('Computing records...')
    records = compute_records(data, TICKERS)
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
