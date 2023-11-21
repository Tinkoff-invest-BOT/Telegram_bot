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


# from weasyprint import HTML
#
# def create_pdf_from_dataframe(dataframe):
#     # Преобразовываем датафрейм в HTML
#     html = dataframe.to_html(classes='table table-condensed table-bordered')
#
#     output = BytesIO()
#
#     # Генерируем PDF из HTML
#     HTML(string=html).write_pdf(output)
#
#     return output

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

# class PDF(FPDF):
#     def header(self):
#         self.set_font("Arial", "B", 12)
#         self.cell(0, 10, "Заголовок", 0, 1, "C")
#
#     def chapter_title(self, title):
#         self.set_font("Arial", "B", 12)
#         self.cell(0, 10, title, 0, 1, "L")
#         self.ln(10)
#
#     def chapter_body(self, body):
#         self.set_font("Arial", "", 12)
#         self.multi_cell(0, 10, body)
#         self.ln()
#
# def create_pdf_from_dataframe(dataframe):
#     output = BytesIO()
#     pdf = PDF()
#     pdf.add_page()
#
#     text = dataframe.to_string(index=False)
#
#     pdf.chapter_title("Ваш заголовок")
#     pdf.chapter_body(text)
#
#     pdf.output(output)
#     return output


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


def create_pdf_from_dataframe(dataframe):
    output = BytesIO()
    pdfmetrics.registerFont(TTFont('Sochi2014Bold', r"C:\Users\Timur\PycharmProjects\pythonProject\Tinkoff_invest\Sochi2014Bold.ttf"))

    doc = SimpleDocTemplate(output, pagesize=letter, fontName='Sochi2014Bold')
    elements = []
    doc.encoding = "utf-8"
    table_data = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8))]))
    elements.append(table)
    doc.build(elements)
    return output





