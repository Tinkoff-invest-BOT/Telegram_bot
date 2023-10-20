import Cython
import pandas as pd
from textblob import TextBlob
import chardet
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, GetAccountsResponse
#
# TOKEN = "t.aR38YYpBrtrkJezowoByFlvhDiOUl8ixFl9QLbnYPr-6x9pfuAL0IOpwjmPdBFI-sNt25Ln1BT9SlhoH1V2WoA"


def tocken_check(TOKEN):
    try:
        if chardet.detect(TOKEN.encode('cp1251'))['language'] == 'Russian':
            result = 2
            return result
    except UnicodeEncodeError as e:
        result = 3
        return result
    else:
        try:
            with Client(TOKEN) as client:
                try:
                    r = client.users.get_accounts()
                    result = 0
                except RequestError as e:
                    result = 1
        except ValueError as e:
            result = 1
        return result