import encodings
import locale
import logging
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, executor, types
from reportlab.pdfbase import pdfmetrics

# import markups as nav
from temporary import df_str, df_html, df
from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from tabulate import tabulate
from io import BytesIO
from db import Database
from passwords import *
from connection_db import connection
from messages import *
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
from bot import *
import chardet
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, GetAccountsResponse
#
# TOKEN = "t.aR38YYpBrtrkJezowoByFlvhDiOUl8ixFl9QLbnYPr-6x9pfuAL0IOpwjmPdBFI-sNt25Ln1BT9SlhoH1V2WoA"
from fpdf import FPDF
import sys
import codecs
import pandas as pd

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
def token_check(TOKEN):
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

# def share_check(share):
#     result = db.share_exist(share)
#     if result:
#         return True
#     return False

def create_pdf_from_dataframe(dataframe):
    output = BytesIO()
    # pdfmetrics.registerFont(TTFont('Sochi2014Bold', r"C:\Users\Timur\PycharmProjects\pythonProject\Tinkoff_invest\Sochi2014Bold.ttf"))

    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    doc.encoding = "utf-8"
    table_data = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8))]))
    elements.append(table)
    doc.build(elements)
    return output

def token_access_level(token):
    pass





