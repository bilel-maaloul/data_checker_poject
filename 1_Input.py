######################
# Import libraries
######################

import pandas as pd
import numpy as np
import streamlit as st
import sys
import streamlit as st1


sys.path.insert(0, "../scripts")

types_list = ['datetime64[ns]', 'float64', 'int64', 'bool', 'object']
df = pd.DataFrame()
min_value=1000
max_value=10000 


if  "filters" not in st.session_state:
     st.session_state['filters']= ['white space', 'negative values','zero values']
     
if  "report" in st.session_state:
    df_report= st.session_state['report']
else :
     st.session_state['report']= pd.DataFrame({
                        'file names': [],
                        'Type of issue': [],
                         'Description' :[]})
     df_report= st.session_state['report']
if  "names" in st.session_state:
     list_names= st.session_state['names']
else:
      st.session_state['names']=''




######################
# config page
######################

st.set_page_config(page_title="Data checker", page_icon="📶", layout="wide", initial_sidebar_state="expanded", menu_items=None)


def extract_names(files):
    return [file.name for file in files if file.name.endswith((".csv", ".xlsx"))]


def set_dataframe(data, columns, map_type):
    df = data.copy()
    error_indices = []
    
    for col, dtype in map_type.items():
        try:
            df[col] = df[col].astype(dtype)
        except (ValueError, TypeError) as e:
            print(f"Error converting column '{col}': {e}")
            error_indices.extend(df[df[col].isnull()].index.tolist())
            
    return df, error_indices


@st.cache_data(show_spinner=False)
def read_file(files,header):
    dfs = []
    columns = None
    
    for file in files:
        if ".csv" in file.name:
            data = pd.read_csv(file,header=header)
        elif ".xlsx" in file.name:
            data = pd.read_excel(file,header=header)
        else:
            st.warning(f"Unsupported file format: {file.name}")
            continue  # Skip unsupported file formats
        
        if columns is None:
            columns = set(data.columns)
            dfs.append(data)
        elif set(data.columns) == columns:
            dfs.append(data)
        else:
            st.error("The tables do not have the same columns!", icon="🚨")
            return None
    
    return pd.concat(dfs)


def display_files_list(names):
    files_list = ''
    if names:
        for name in names:
            files_list += name + ', '
        st.session_state['names']=files_list
    else:
      
        files_list = st.session_state['names']
    st.write('The files that are currently in Data Checker are: ' + str(files_list))
       


def convert_column_types(data, column_map, columns):
    updated_df = data.copy()  # Create a copy of the DataFrame to avoid modifying the original

    conversion_errors = {}  # Use a dictionary to store column and error pairs

    for column, new_type in column_map.items():
        try:
            updated_df[column] = updated_df[column].astype(new_type)  # Convert column type
        except Exception as e:
            conversion_errors[column] = str(e)  # Store column and error in the dictionary

    if conversion_errors:
        return conversion_errors  # Return the dictionary of conversion errors
    else:
        return updated_df[columns]  # Return the DataFrame with updated columns

def get_values(df,min,max,rows_per_page):
    
    try:
           
        if min > len(df):
                    rows_per_page=len(df)
        if max>len(df):
                    rows_per_page=len(df)
        return rows_per_page
    except:
           pass
    
def display_dataframe_with_pagination(df, rows_per_page):
            try:
                start_idx = 0
                n=0
                while start_idx < len(df):
                    st.dataframe(df.iloc[start_idx:start_idx + rows_per_page])
                    start_idx += rows_per_page
                    n=n+1
                    if number_of_page==n:
                        break
            except:
                pass

        # Call the function to display the large DataFrame with pagination


######################
# Side bar
######################
# sb = st.sidebar
# selected2 = option_menu(None, ["Input", "Date handle", "Missing values", "Outliers"],
#                         icons=["🟠", "date_range","warning","trending_up"],
#                         menu_icon="cast",
#                         default_index=0)


######################
# Main page
######################
st.title("Input")

header = st.number_input("input header row", min_value=0, max_value=None, value=0, step=1)

rows_per_page = st.number_input("Number of Rows per Page", min_value=1000, max_value=10000, value=1000)

number_of_page= st.number_input("Number of page", min_value=1, max_value=50, value=1)

uploaded_files = st.file_uploader("Input csv or excel file", type=["xlsx","csv"],accept_multiple_files=True)

list_names=extract_names(uploaded_files)

if list_names:
     st.session_state['names']=list_names
     
display_files_list(list_names) 
     
if len(uploaded_files)>0:
    df = read_file(uploaded_files,header)

elif "df" in st.session_state:
    df = st.session_state["df"]

else :
    df = pd.DataFrame()

if len(df)>0:
    st.markdown(
    """
    <style>
    .stButton button {
        padding: 0.75rem 1.5rem;
        font-size: 16px;
        display: block;
        margin: 0 auto;
        margin-left:-300px
    }
    </style>
    """,
    unsafe_allow_html=True
)

    st.markdown("# columns configuration")
    selected_cols = st.multiselect("select columns: ", list(df.columns), default=list(df.columns))
    
    default_types_map = dict(df.dtypes)
    types_map_1 = {}
    types_map_2 = {}
   
    n=0
    col1, col2 = st.columns(2)
    col1_row1, col1_row2 = col1.columns(2)

# In the second horizontal column (col2), create two vertical columns
    col2_row1, col2_row2 = col2.columns(2)

    for col in selected_cols:
        type = str(df.dtypes[col])

        if n%2==0:
            types_map_1[n] = col1_row1.selectbox(label=col,key=col+"_type", options=types_list, index=types_list.index(type))
        else: 
            types_map_2[n]= col2_row1.selectbox(label=col,
                          key=col+"_type_", options=types_list, index=types_list.index(type))          
        
        
        
        n=n+1
    types_map_ = {}
    for col in selected_cols:
        type = str(df.dtypes[col])
        types_map_[col] = type
    merged_dict = {**types_map_1, **types_map_2}
    types_map_final = {}
    sorted_merged_dict = dict(sorted(merged_dict.items(), key=lambda item: int(item[0])))

# Iterate through the original_dict
    l=0
    for col in selected_cols:
         types_map_[col]=sorted_merged_dict[l]
         l=l+1
         if l==len(sorted_merged_dict):
            break
         
    if default_types_map != types_map_1:
        col3,col4=st.columns(2)
        button_container = col4.empty()
        if button_container.button('confirm'):
            result = convert_column_types(df, types_map_,selected_cols)
            if isinstance(result, dict):
                for column, error_message in enumerate(result):
                    st.error(f"Error converting column '{column}': {error_message}", icon="🚨")
                
            else:
                df = result
                st.success('type conversion is successfully done', icon="✅")                                           
                default_types_map = dict(df.dtypes)
                button_container.empty()

    display_dataframe_with_pagination(df,get_values(df,min_value,max_value,rows_per_page))
    
    
           
         
    st.session_state["df"] = df
    st.session_state["report"]=df_report
    
  
   


