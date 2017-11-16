import pandas as pd
import numpy as np
from openpyxl import load_workbook


file1 = 'ArithmeticS14ExplnANON.xlsx'
file2 = 'ArithmeticS13ExplnANONResults.xlsx'
file3 = 'ArithmeticS13ControlExplanationANONResults.xlsx'
file4 = 'ArithmeticF13VizExplanationANONResults.xlsx'
file5 = 'ArithmeticF13ExplanationANONResults.xlsx'
file6 = 'ArithmeticF12VizExplnANONResults.xlsx'
file7 = 'ArithmeticF12ExplnANONResults.xlsx'


def correlation():
    df1 = pd.read_excel(file1, sheetname='Stats')
    df2 = pd.read_excel(file2, sheetname='Stats')
    df3 = pd.read_excel(file3, sheetname='Stats')
    df4 = pd.read_excel(file4, sheetname='Stats')
    df5 = pd.read_excel(file5, sheetname='Stats')
    df6 = pd.read_excel(file6, sheetname='Stats')
    df7 = pd.read_excel(file7, sheetname='Stats')

    #for s in ['1', '2', '3', '4', '5', '6', '7']
    
    df_concat = pd.concat([df1, df2, df3, df4, df5, df6, df7])
    
    #print df_concat
    #print df_concat.iloc[4,0]
    
    df_concat[df_concat.columns[0]].mean()

    
correlation()