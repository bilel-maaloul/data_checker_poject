import pandas as pd
import streamlit as st
from itertools import product
import plotly.graph_objects as go
import numpy as np
import plotly.figure_factory as ff
import base64
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb 



date_cols = []
numerical_cols = []
######################
# Main page
######################
st.title("report")
if "report" not in st.session_state:
    st.warning("add reports before moving to this page")
else:
        st.dataframe(st.session_state['report'],use_container_width=True ,hide_index=True)

       
                # Convert DataFrame to CSV and create a download link
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')  # Explicitly set the engine to 'xlsxwriter'
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()  # Close the writer, which writes the data to the output buffer
    processed_data = output.getvalue()
    return processed_data

df_xlsx = to_excel(st.session_state['report'])
st.download_button(label='📥 Download Report',
                   data=df_xlsx,
                   file_name='report.xlsx',
                   mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')