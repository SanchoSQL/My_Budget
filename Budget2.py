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
#filter out items prior to 2023
cashapp_df = cashapp_df[pd.to_datetime(cashapp_df['Date']).dt.year >= 2023]

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
df['year_month'] = df['Date'].dt.strftime('%Y-%m')
df['month_day'] = df['Date'].dt.strftime('%m-%d')

# This is a test to confirm the fast food category does not contain certain CC sub-categories

df_filtered2test = df[(df['Category'] == 'Fast_Food') & (df['Sub-Category'].isin(['CAPITAL ONE', 'CHASE', 'DISCOVER']))]
df_filtered2test

output = "R:/Dropbox/BillCSV/TEST3.xlsx"
df.to_excel(output)

# This will create a df for monthly income

Income_Table = df.query("Amount > 0").groupby('year_month')['Amount'].sum().reset_index(name ='sum')
Income_Table

# filter income from df and convert negative amounts 

df = df[df.Category != "Remove"] 
df['Amount'] = df.Amount*(-1)  

#categories = df.loc[:, 'Category'].unique()

# create a table for each category

categories = df['Category'].unique()
dfs = {}
for category in categories:
    dfs[f"{category}_Table"] = df[df['Category'] == category].groupby('year_month')['Amount'].sum().reset_index(name=f"{category}_sum")
for key in dfs:
    exec(f"{key} = dfs['{key}']")
    print(key)


%whos DataFrame
Credit_Cards_Table


