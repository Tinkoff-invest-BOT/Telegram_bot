import requests
import apimoex
import pandas as pd


TIMEFRAMES = ['M1', 'M10', 'H1', 'D1', 'W1', 'MN1']
INDICATORS = ['ABERRATION', 'ABOVE', 'ABOVE_VALUE', 'ACCBANDS', 'AD', 'ADOSC', 'ADX', 'ALMA', 'AMAT', 'AO', 'AOBV', 'APO', 'AROON', 'ATR', 'BBANDS', 'BELOW', 'BELOW_VALUE', 'BIAS', 'BOP', 'BRAR', 'CCI', 'CDL_PATTERN', 'CDL_Z', 'CFO', 'CG', 'CHOP', 'CKSP', 'CMF', 'CMO', 'COPPOCK', 'CROSS', 'CROSS_VALUE', 'CTI', 'DECAY', 'DECREASING', 'DEMA', 'DM', 'DONCHIAN', 'DPO', 'EBSW', 'EFI', 'EMA', 'ENTROPY', 'EOM', 'ER', 'ERI', 'FISHER', 'FWMA', 'HA', 'HILO', 'HL2', 'HLC3', 'HMA', 'HWC', 'HWMA', 'ICHIMOKU', 'INCREASING', 'INERTIA', 'JMA', 'KAMA', 'KC', 'KDJ', 'KST', 'KURTOSIS', 'KVO', 'LINREG', 'LOG_RETURN', 'LONG_RUN', 'MACD', 'MAD', 'MASSI', 'MCGD', 'MEDIAN', 'MFI', 'MIDPOINT', 'MIDPRICE', 'MOM', 'NATR', 'NVI', 'OBV', 'OHLC4', 'PDIST', 'PERCENT_RETURN', 'PGO', 'PPO', 'PSAR', 'PSL', 'PVI', 'PVO', 'PVOL', 'PVR', 'PVT', 'PWMA', 'QQE', 'QSTICK', 'QUANTILE', 'RMA', 'ROC', 'RSI', 'RSX', 'RVGI', 'RVI', 'SHORT_RUN', 'SINWMA', 'SKEW', 'SLOPE', 'SMA', 'SMI', 'SQUEEZE', 'SQUEEZE_PRO', 'SSF', 'STC', 'STDEV', 'STOCH', 'STOCHRSI', 'SUPERTREND', 'SWMA', 'T3', 'TD_SEQ', 'TEMA', 'THERMO', 'TOS_STDEVALL', 'TRIMA', 'TRIX', 'TRUE_RANGE', 'TSI', 'TSIGNALS', 'TTM_TREND', 'UI', 'UO', 'VARIANCE', 'VHF', 'VIDYA', 'VORTEX', 'VP', 'VWAP', 'VWMA', 'WCP', 'WILLR', 'WMA', 'XSIGNALS', 'ZLMA', 'ZSCORE']


dict_timeframes = {
    'M1': 1,
    'M5': 10,
    'M10': 10,
    'H1': 60,
    'D1': 24,
    'W1': 7,
    'MN1': 31,
}


def get_symbol_names():
    res = ['ABIO', 'ABRD', 'ACKO', 'AFKS', 'AFLT', 'AGRO', 'AKRN', 'ALRS', 'AMEZ', 'APTK', 'AQUA', 'ARSA', 'ASSB', 'ASTR', 'AVAN', 'BANE', 'BANEP', 'BELU', 'BISVP', 'BLNG', 'BRZL', 'BSPB', 'BSPBP', 'CARM', 'CBOM', 'CHGZ', 'CHKZ', 'CHMF', 'CHMK', 'CIAN', 'CNTL', 'CNTLP', 'DIOD', 'DSKY', 'DVEC', 'DZRD', 'DZRDP', 'EELT', 'ELFV', 'ENPG', 'ETLN', 'EUTR', 'FEES', 'FESH', 'FIVE', 'FIXP', 'FLOT', 'GAZA', 'GAZAP', 'GAZC', 'GAZP', 'GAZS', 'GAZT', 'GCHE', 'GECO', 'GEMA', 'GEMC', 'GLTR', 'GMKN', 'GTRK', 'HHRU', 'HIMCP', 'HMSG', 'HNFG', 'HYDR', 'IGST', 'IGSTP', 'INGR', 'IRAO', 'IRKT', 'JNOS', 'JNOSP', 'KAZT', 'KAZTP', 'KBSB', 'KCHE', 'KCHEP', 'KGKC', 'KGKCP', 'KLSB', 'KMAZ', 'KMEZ', 'KOGK', 'KRKN', 'KRKNP', 'KRKOP', 'KROT', 'KROTP', 'KRSB', 'KRSBP', 'KTSB', 'KTSBP', 'KUBE', 'KUZB', 'KZOS', 'KZOSP', 'LENT', 'LIFE', 'LKOH', 'LNZL', 'LNZLP', 'LSNG', 'LSNGP', 'LSRG', 'LVHK', 'MAGE', 'MAGEP', 'MAGN', 'MDMG', 'MFGS', 'MFGSP', 'MGNT', 'MGNZ', 'MGTS', 'MGTSP', 'MISB', 'MISBP', 'MOEX', 'MRKC', 'MRKK', 'MRKP', 'MRKS', 'MRKU', 'MRKV', 'MRKY', 'MRKZ', 'MRSB', 'MSNG', 'MSRS', 'MSTT', 'MTLR', 'MTLRP', 'MTSS', 'MVID', 'NAUK', 'NFAZ', 'NKHP', 'NKNC', 'NKNCP', 'NKSH', 'NLMK', 'NMTP', 'NNSB', 'NNSBP', 'NSVZ', 'NVTK', 'OGKB', 'OKEY', 'OMZZP', 'OZON', 'PAZA', 'PHOR', 'PIKK', 'PLZL', 'PMSB', 'PMSBP', 'POLY', 'POSI', 'PRFN', 'PRMB', 'QIWI', 'RASP', 'RBCM', 'RDRB', 'RENI', 'RGSS', 'RKKE', 'RNFT', 'ROLO', 'ROSB', 'ROSN', 'ROST', 'RTGZ', 'RTKM', 'RTKMP', 'RTSB', 'RTSBP', 'RUAL', 'RUSI', 'RZSB', 'SAGO', 'SAGOP', 'SARE', 'SAREP', 'SBER', 'SBERP', 'SELG', 'SFIN', 'SGZH', 'SIBN', 'SLEN', 'SMLT', 'SNGS', 'SNGSP', 'SOFL', 'SPBE', 'STSB', 'STSBP', 'SVAV', 'SVCB', 'SVET', 'TASB', 'TASBP', 'TATN', 'TATNP', 'TCSG', 'TGKA', 'TGKB', 'TGKBP', 'TGKN', 'TNSE', 'TORS', 'TORSP', 'TRMK', 'TRNFP', 'TTLK', 'TUZA', 'UGLD', 'UKUZ', 'UNAC', 'UNKL', 'UPRO', 'URKZ', 'USBN', 'UTAR', 'VEON-RX', 'VGSB', 'VGSBP', 'VJGZ', 'VJGZP', 'VKCO', 'VLHZ', 'VRSB', 'VRSBP', 'VSMO', 'VSYD', 'VSYDP', 'VTBR', 'WTCM', 'WTCMP', 'WUSH', 'YAKG', 'YKEN', 'YKENP', 'YNDX', 'YRSB', 'YRSBP', 'ZILL', 'ZVEZ']
    return res


