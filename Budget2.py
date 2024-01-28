# Import Libraries
import pandas as pd                       #to perform data manipulation and analysis
import numpy as np                        #to cleanse data
import os                                 #to get update time of file
import time
from datetime import datetime                           #to manipulate dates
import plotly.express as px               #to create interactive charts
import plotly.graph_objects as go         #to create interactive charts
from jupyter_dash import JupyterDash      #to build Dash apps from Jupyter environments
from dash import dcc                      #to get components for interactive user interfaces
from dash import html                     #to compose the dash layout using Python structures

# Define the file paths for my accounts
chase_raw = 'R:/Dropbox/BillCSV/Chase9109_Activity.csv'
ncu_raw = 'R:/Dropbox/BillCSV/MYNCU.csv'
cashapp_raw = 'R:/Dropbox/BillCSV/cash_app_report.csv'

# check the latest time data was updated in AA/PM format
chase_upd_dt = datetime.fromtimestamp(os.path.getmtime(chase_raw)).strftime('%Y-%m-%d %I:%M:%S %p')
ncu_upd_dt = datetime.fromtimestamp(os.path.getmtime(ncu_raw)).strftime('%Y-%m-%d %I:%M:%S %p')
cashapp_upd_dt = datetime.fromtimestamp(os.path.getmtime(cashapp_raw)).strftime('%Y-%m-%d %I:%M:%S %p')

# Read the CSV files into separate data frames
chase_df = pd.read_csv(chase_raw,index_col=False)
ncu_df = pd.read_csv(ncu_raw,index_col=False,header = 3)
cashapp_df = pd.read_csv(cashapp_raw,index_col=False)

print(f"chase_df was updated: {chase_upd_dt}\nncu_df was updated {ncu_upd_dt} \ncashapp_df was updated {cashapp_upd_dt}")

# Clean up chase_df
chase_df.drop(['Details','Balance','Type','Check or Slip #'], axis=1, inplace=True)     
chase_df['Description'] = chase_df['Description'].astype(str).str.upper()
chase_df = chase_df.rename(columns={'Posting Date': 'Date'})

# Clean up ncu_df
ncu_df['Description'] = ncu_df['Description'].astype(str).str.upper() + ' ' + ncu_df['Memo'].astype(str).str.upper()
ncu_df['Amount'] = np.where(ncu_df['Amount Debit'].notnull(), ncu_df['Amount Debit'], ncu_df['Amount Credit'])
ncu_df.drop(['Transaction Number','Check Number','Memo','Amount Debit','Amount Credit','Balance','Fees  '], axis=1, inplace=True)     


# Clean up cashapp_df
# format the date
cashapp_df['Date'] = cashapp_df['Date'].str.replace('CST|CDT', '', regex=True) # remove tz for formatting
cashapp_df['Date'] = cashapp_df['Date'].apply(pd.to_datetime)                  #convert to date
cashapp_df['Date'] = cashapp_df['Date'].dt.strftime('%m/%d/%Y')                #re-format to match other dfs
#remove certain transactions 
cashapp_df = cashapp_df[~cashapp_df['Transaction Type'].isin(['Bitcoin Buy','Bitcoin Sale', 'Bitcoin Boost','Stock Sell','Stock Buy','Boost Payment'])]
# Create a new 'Description' column in cashapp_df combining Transaction Type, Notes, and Name
cashapp_df['Description'] = cashapp_df['Transaction Type'] + ' ' + cashapp_df['Notes'].fillna(cashapp_df['Name of sender/receiver']).fillna('')
# Convert the 'Description' column to uppercase
cashapp_df['Description'] = cashapp_df['Description'].str.upper()
# fix the amount field
cashapp_df['Amount'] = cashapp_df['Amount'].str.replace('$', '')                # remove the $
cashapp_df['Amount'] = pd.to_numeric(cashapp_df['Amount'], errors='coerce')     # convert the format to numeric
#drop columns
cashapp_df.drop(['Transaction ID','Currency','Asset Type','Asset Price','Asset Amount','Account','Fee',
          'Status','Name of sender/receiver','Notes','Transaction Type','Net Amount'], axis=1, inplace=True)     

#print(cashapp_df.head(3))

# Add a new columns 'Source' indicating the source and last updated
chase_df['Source'] = 'Chase Bank'
chase_df['Source Updated'] = chase_upd_dt
ncu_df['Source'] = 'Neighborhood CU'
ncu_df['Source Updated'] = ncu_upd_dt
cashapp_df['Source'] = 'Cash App'
cashapp_df['Source Updated'] = cashapp_upd_dt

# Combine the dataframes into a single dataframe
df = pd.concat([chase_df, ncu_df, cashapp_df], ignore_index=True)
#filter out items prior to 2023
df = df[pd.to_datetime(df['Date']) >= '2022-10-01']
#df = df[pd.to_datetime(df['Date']).dt.year >= 2023]


# Define the categories
FastFood = 'TREATS|STARBUCKS|SWIG|KONA ICE|DONUTBOX|DELISH|SMASHBURGER|POPEYES|DOMINO|PANERA|BURGERS|BURGER|TACO|MCDONALD|\
JERSEY MIKES|PANDA EXPRESS|SONIC|CHICK|BOBA|JAM|THAI|CHIPOTLE|PIZZA|WING|WENDY|RUSSO|ROSAS|BRAUMS|COOKHOUSE|BAHAMA|PIZZERIA|\
BAGEL|CHICKEN|BISTRO|DAIRY|DOMINO|DRIP N ROLL|MOUNTAIN COO|WHATABURGER|WAFFLE|DEBIT TST|TST'

Grocery = 'KROGER|WAL-MART|SPROUTS|H-E-B|HOLLYWOOD FEED|SUPERMARKET|PET SUPPLIES|PETCO'
Travel = 'NEW ORLEANS|UBER|LYFT|MSY|SAN DIEGO|GUANACASTE'
Income = 'PAYROLL|DEPOSIT|TAX REF'
Entertainment = 'PARAMNTPLUS|HULU|NETFLIX|YOUTUBE|APPLE.COM|PEACOCKTVLL|DIRECTV|SPOTIFY|DIRECTV|CINEMARK|GOOGLE_P|PATREON|SHOWTIME'
Remove = 'CASH OUT VISA|TRANSFER|CASH OUT'  # these transactions can be removed
Alcohol = 'LIQUOR|TOTAL WINE|WINE AND SPIRIT'
Gas = 'Fuel'
Car = 'TO LOAN 0000'
Maintenance = 'BRAKES PLUS'
PersonalCare = 'MCGUINESS|TPD SMILES|LCSW|MASSAGE'
Bills = '9864031004|CVS CAREPASS|DROPBOX'
CreditCards = '5920|CAPITAL ONE|CITICTP|CARDMEMBER|TARGET CARD|NEFURNMART|DISCOVER|CHASE CREDIT'
ATM = 'ATM WITHDRAW|ATM FEE'

df['Category'] =np.where(df['Description'].str.contains(Income), 'Income',
                np.where(df['Description'].str.contains(Gas), 'Gas', 
                np.where(df['Description'].str.contains(Grocery), 'Grocery',
                np.where(df['Description'].str.contains(Alcohol), 'Alcohol',
                np.where(df['Description'].str.contains(Maintenance), 'Maintenance', 
                np.where(df['Description'].str.contains(FastFood),'Fast_Food',        
                np.where(df['Description'].str.contains(Entertainment), 'Entertainment',
                np.where(df['Description'].str.contains(PersonalCare), 'Personal_Care',
                np.where(df['Description'].str.contains(Bills), 'Bills',
                np.where(df['Description'].str.contains(CreditCards), 'Credit_Cards',
                np.where(df['Description'].str.contains(Travel), 'Travel',
                np.where(df['Description'].str.contains(Car), 'Car',
                np.where(df['Description'].str.contains(ATM), 'ATM',
                np.where(df['Description'].str.contains(Remove), 'Remove', 
                'Shopping' ))))))))))))))

# create a Subcategory to further break out certain items
df['Sub-Category'] = df['Description'].apply(lambda x: 'CHICK FIL A' if 'CHICK' in x 
else 'ROSAS' if 'ROSAS' in x 
else 'ATT' if 'ATT' in x 
else 'DROPBOX' if 'DROPBOX' in x 
else 'BEST BUY' if 'BEST BUY' in x 
else 'CAPITAL ONE' if 'CAPITAL ONE' in x 
else 'MYNCU' if 'CARDMEMBER' in x 
else 'DISCOVER' if '5119' in x 
else 'CHASE' if '5920' in x 
else 'TARGET' if 'TARGET' in x 
else 'CINEMARK' if 'CINEMARK' in x 
else 'HULU' if 'HULU' in x 
else 'APPLE' if 'APPLE' in x 
else 'DIRECTV' if 'DIRECTV' in x 
else 'YOUTUBE' if 'YOUTUBE' in x 
else 'NETFLIX' if 'NETFLIX' in x 
else 'PARAMOUNT' if 'PARAMNTPLUS' in x 
else 'PEACOCK' if 'PEACOCKTVLL' in x 
else 'SPOTIFY' if 'SPOTIFY' in x 
else 'AMAZON' if 'AMZN' in x 
else 'CVS' if 'CVS' in x 
else 'UBER' if 'UBER' in x 
else 'BOBA' if 'BOBA' in x 
else 'WHATABURGER' if 'WHATABURGER' in x 
else 'KROGER' if 'KROGER' in x 
else 'WAL-MART' if 'WAL-MART' in x 
else 'CHIPOTLE' if 'CHIPOTLE' in x 
else 'WENDYS' if 'WENDY' in x 
else 'BRAUMS' if 'BRAUMS' in x
else 'JOY THAI' if 'JOY THAI' in x
else 'JOY THAI' if 'JOYTHAI' in x
else 'PANDA EXPRESS' if 'PANDA EXPRESS' in x
else 'SWIG' if 'SWIG' in x
else 'TIFFS TREATS' if 'TIFFS TREATS' in x
else 'WINGSTOP' if 'WINGSTOP' in x
else 'Ray' if 'HOLLYWOOD FEED' in x
else 'Ray' if 'HOLLYWOODFEED' in x
else 'Ray' if 'PETCO' in x
else 'TPD SMILES' if 'TPD SMILES' in x
else 'COSTCO' if 'COSTCO' in x
else 'T.J. MAXX' if 'T.J. MAXX' in x
else 'ULTA' if 'ULTA' in x
else 'STARBUCKS' if 'STARBUCKS' in x
else 'BAHAMA BUCKS' if 'BAHAMA BUCKS' in x
else 'MISC') 

df['Date'] = pd.to_datetime(df['Date'])

df['week'] = df['Date'].dt.isocalendar().week


df['year_month'] = df['Date'].dt.strftime('%Y-%m')
df['month_day'] = df['Date'].dt.strftime('%m-%d')
df['year_month_day'] = df['Date'].dt.strftime('%Y-%m-%d')



# This is a test to confirm the fast food category does not contain certain CC sub-categories

df_filtered2test = df[(df['Category'] == 'Fast_Food') & (df['Sub-Category'].isin(['CAPITAL ONE', 'CHASE', 'DISCOVER']))]
df_filtered2test

output = "R:/Dropbox/BillCSV/TEST3.xlsx"
df.to_excel(output)

df.info()

# This will create a df for monthly income

Income_Table = df.query("Amount > 0").groupby('year_month')['Amount'].sum().reset_index(name ='sum')
Income_Table

# Income over time

Income_Table['cumulative sum'] = Income_Table['sum'].cumsum()
Income_Table = go.Figure(
    data = go.Scatter(x = Income_Table["year_month"], y = Income_Table["cumulative sum"]),
    layout = go.Layout(
        title = go.layout.Title(text = "Income Over Time")
    )
)
Income_Table.update_layout(
    xaxis_title = "Date",
    yaxis_title = "Net Worth (£)",
    hovermode = 'x unified'
    )
Income_Table.update_xaxes(
    tickangle = 45)
Income_Table.show()

# filter income from df and convert negative amounts, renamed to df_spending

df_spending = df[df.Category != "Remove"] 
df_spending = df_spending[df_spending["Category"].isin(["Remove","Income"]) == False]
df_spending['Amount'] = df_spending.Amount*(-1)  

df_spending.info()
df_spending


Expenses_Breakdown_Table = pd.pivot_table(df_spending, values = ['Amount'], index = ['Category', 'year_month'], aggfunc=sum).reset_index()
Expenses_Breakdown_Table

Expenses_Breakdown_Table.columns = [x.upper() for x in Expenses_Breakdown_Table.columns]

Expenses_Breakdown_Chart = px.line(Expenses_Breakdown_Table, x='YEAR_MONTH', y="AMOUNT", title="Expenses Breakdown", color = 'CATEGORY')

Expenses_Breakdown_Chart.update_yaxes(title='Expenses (£)', visible=True, showticklabels=True)

Expenses_Breakdown_Chart.update_xaxes(title='Date', visible=True, showticklabels=True)

Expenses_Breakdown_Chart.show()


#categories = df.loc[:, 'Category'].unique()

# create a table for each category for graphs

categories = df_spending['Category'].unique()
dfs = {}
for category in categories:
    dfs[f"{category}_Table"] = df_spending[(df_spending['Category'] == category) & (df_spending['Amount'] > 0)].groupby('year_month')['Amount'].sum().reset_index(name=f"{category}_sum")
for key in dfs:
    exec(f"{key} = dfs['{key}']")
    print(key)

# by day

categories = df_spending['Category'].unique()
dfs = {}
for category in categories:
    dfs[f"{category}_Table_Day"] = df_spending[(df_spending['Category'] == category) & (df_spending['Amount'] > 0)].groupby('year_month_day')['Amount'].sum().reset_index(name=f"{category}_sum")
for key in dfs:
    exec(f"{key} = dfs['{key}']")
    print(key)




#%whos DataFrame #to view all datarames in memory
# put tables into list

expense_tbls = list(dfs.keys())
expense_tbls 

# merge all dfs; this needs to be done on the date which is an object
#from functools import partial, reduce
#Expenses_Monthly = reduce(lambda left,right: pd.merge(left,right,on=["year_month"],
#                                            how="outer"), expense_tbls).fillna('void')
#Expenses_Monthly

Fast_Food_Table_Week

# Test Graph

fig = go.Figure([go.Scatter(x=Fast_Food_Table_Day['year_month_day'], y=Fast_Food_Table_Day['Fast_Food_sum'])])
fig.show()

fig = go.Figure([go.Scatter(x=Grocery_Table_Day['year_month_day'], y=Grocery_Table_Day['Grocery_sum'])])
fig.show()



# Fast Food over time

Fast_Food_Table['cumulative sum'] = Fast_Food_Table['Fast_Food_sum'].cumsum()
Fast_Food_Table = go.Figure(
    data = go.Scatter(x = Fast_Food_Table["year_month"], y = Fast_Food_Table["cumulative sum"]),
    layout = go.Layout(
        title = go.layout.Title(text = "Fast Food Spending over time")
    )
)
Fast_Food_Table.update_layout(
    xaxis_title = "Date",
    yaxis_title = "Net Worth (£)",
    hovermode = 'x unified'
    )
Fast_Food_Table.update_xaxes(
    tickangle = 45)
Fast_Food_Table.show()

fig = px.sunburst(df_spending, path=['Category'], values='Amount', color='Category')
fig.show()




