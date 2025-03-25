from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
import warnings
import matplotlib
matplotlib.use('Agg') 

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
file_path = os.path.join("data", "expenses.xlsx")

def get_expense_data():
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    total_income = df[df['Debit/Credit'] > 0]['Debit/Credit'].sum()
    total_expenses = df[df['Debit/Credit'] < 0]['Debit/Credit'].sum()
    net_savings = total_income + total_expenses
    monthly_summary = df.groupby('Month')['Debit/Credit'].agg(['sum', lambda x: x[x > 0].sum(), lambda x: x[x < 0].sum()])
    monthly_summary.columns = ['Net', 'Income', 'Expenses']
    #MAKING ALL CATEGORIES IN LOWER CASE SINCE THERE IS AN CONFLICT IN THE DATA SET
    df['Category'] = df['Category'].str.lower()
    return total_income,total_expenses,net_savings,df, monthly_summary


def removing_Incomes_data_from_df(df):
    value_to_remove = 'Income'
    df_filtered_without_salary= df[df['Income/Expense'] != value_to_remove]    
    df_only_salary = df[df['Income/Expense'] == value_to_remove]
    return df_filtered_without_salary,df_only_salary


#analysis categories without salary incomes 
def analyze_spending_by_category(dfWithoutIncomes):
    category_spending = dfWithoutIncomes.groupby('Category')['Debit/Credit'].sum().reset_index()
    category_spending = category_spending.sort_values(by='Debit/Credit')
    return category_spending

def prediction_related(df):
    df["Date"]=pd.to_datetime(df["Date"])
    df["Year-Month"]=df["Date"].dt.to_period("M")
    monthly_finance=df.groupby(["Year-Month","Income/Expense"])["Debit/Credit"].sum().unstack().fillna(0)
    monthly_finance.columns=["Expenses","Income"]
    monthly_finance["Net Savings"] = monthly_finance["Income"]+monthly_finance["Expenses"]
    saving_series=monthly_finance["Net Savings"]
    model= ARIMA(saving_series, order=(2,1,2))
    model_fit=model.fit()
    forecast_steps = 6
    forecast = model_fit.forecast(steps=forecast_steps)
    future_months= pd.period_range(start=saving_series.index[-1] + 1,periods=forecast_steps,freq="M")
    return saving_series, future_months, forecast

def plot_monthly_income_vs_expenses(df):
    monthly_summary = df.groupby(['Month', 'Income/Expense'])['Debit/Credit'].sum().unstack()
    plt.figure(figsize=(12, 6))
    monthly_summary.plot(kind='bar', stacked=True)
    plt.title("Monthly Income vs. Expense")
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    filename = "monthly_income_vs_expenses.png"
    filepath = os.path.join("static", filename)
    plt.savefig(filepath)
    plt.close()
    return filename 
    
# def plot_monthly_income_vs_expenses(monthly_summary):
#     plt.figure(figsize=(10, 6))
#     monthly_summary[['Income', 'Expenses']].plot(kind='bar')
#     plt.title('Monthly Income vs. Expenses')
#     plt.xlabel('Month')
#     plt.ylabel('Amount')
#     plt.xticks(rotation=45)
#     filename = "monthly_income_vs_expenses.png"
#     plt.savefig(os.path.join("static", filename))
#     plt.close()
#     return filename



def plot_category_spendings(df):
    category_monthly = df.groupby(['Month', 'Category'])['Debit/Credit'].sum().unstack().fillna(0)
    plt.figure(figsize=(14, 7))
    category_monthly.plot(kind='bar', colormap='coolwarm', edgecolor='black', alpha=0.85, figsize=(14, 7), width=0.8)
    plt.xlabel("Month", fontsize=12, fontweight='bold')
    plt.ylabel("Amount Spent ($)", fontsize=12, fontweight='bold')
    plt.title("Spending by Category Over Time", fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend(title="Category", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Adds light horizontal gridlines
    plt.tight_layout()
    filename = "category_trends.png"
    plt.savefig(os.path.join("static", filename), bbox_inches="tight", dpi=300)
    plt.close()

    return filename

def plot_monthly_balance(monthly_summary):
    plt.figure(figsize=(10, 6))
    monthly_summary['Net'].plot(kind='line', marker='o')
    plt.title('Monthly Balance Over Time')
    plt.xlabel('Month')
    plt.ylabel('Net Balance')
    plt.grid(True)
    filename = "monthly_balance.png"
    plt.savefig(os.path.join("static", filename))
    plt.close()
    return filename

def plot_income_sources(df):
    income_sources = df[df['Debit/Credit'] > 0].groupby('Category')['Debit/Credit'].sum()
    plt.figure()
    income_sources.plot(kind='pie', autopct='%1.1f%%', title='Income Sources Breakdown')
    filename = "income_sources.png"
    plt.savefig(os.path.join("static", filename))
    plt.close()
    return filename


#need to be in html 
def plot_needs_wants(df):
    essential_categories = ['household', 'transportation']
    total_expenses = abs(df[df['Debit/Credit'] < 0]['Debit/Credit'].sum())
    essential_spending = abs(df[df['Category'].isin(essential_categories)]['Debit/Credit'].sum())
    discretionary_spending = total_expenses - essential_spending
    labels = ['Needs', 'Wants']
    plt.figure()
    plt.pie([essential_spending, discretionary_spending], labels=labels, autopct='%1.1f%%')
    plt.title('Needs vs. Wants Spending')
    filename = "needs_wants.png"
    plt.savefig(os.path.join("static", filename))  # Save the plot in the "static" folder
    plt.close()
    return filename
#prdiction part 
#need to be in html
def plot_actual_vs_forecasted_savings(saving_series, future_months, forecast):
    plt.figure(figsize=(12, 6))
    plt.plot(saving_series.index.astype(str), saving_series, label="Actual Net Savings", marker="o")
    plt.plot(future_months.astype(str), forecast, label="Forecasted Net Savings", marker="x", linestyle="--", color="red")
    plt.xticks(rotation=45)
    plt.xlabel("Month")
    plt.ylabel("Net Savings ($)")
    plt.title("Net Savings Forecast for Next 6 Months")
    plt.legend()
    plt.grid(True)
    filename = "actual_vs_forecasted_savings.png"
    plt.savefig(os.path.join("static", filename))  
    plt.close()
    return filename

#need to be in html 
def Visualize_suspicious_transactions_highlight_outliers(df):
    df['Rolling_Avg'] = df.groupby('Year-Month')['Debit/Credit'].transform(lambda x: x.rolling(window=3).mean())
    df['Rolling_Std'] = df.groupby('Year-Month')['Debit/Credit'].transform(lambda x: x.rolling(window=3).std())
    outlier_detector = IsolationForest(contamination=0.02)  # 2% of data as outliers
    df['Outlier'] = outlier_detector.fit_predict(df[['Debit/Credit']])
    outliers = df[df['Outlier'] == -1]
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Debit/Credit'], label='Transaction Amount')
    plt.scatter(outliers['Date'], outliers['Debit/Credit'], color='red', label='Outliers (Fraud)')
    plt.title('Suspicious Transactions (Outliers)')
    plt.xlabel('Date')
    plt.ylabel('Transaction Amount')
    plt.legend()
    plt.grid(True)
    filename = "suspicious_transactions.png"
    plt.savefig(os.path.join("static", filename)) 
    plt.close()
    return filename
def Plot_actual_vs_forecasted_savings(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year-Month"] = df["Date"].dt.to_period("M")
    monthly_finance = df.groupby(["Year-Month", "Income/Expense"])["Debit/Credit"].sum().unstack().fillna(0)
    monthly_finance.columns = ["Expenses", "Income"]
    monthly_finance["Net Savings"] = monthly_finance["Income"] + monthly_finance["Expenses"]
    saving_series = monthly_finance["Net Savings"]
    model = ARIMA(saving_series, order=(2,1,2))
    model_fit = model.fit()
    forecast_steps = 6
    forecast = model_fit.forecast(steps=forecast_steps)
    future_months = pd.period_range(start=saving_series.index[-1] + 1, periods=forecast_steps, freq="M")
    plt.figure(figsize=(12, 6))
    plt.plot(saving_series.index.astype(str), saving_series, label="Actual Net Savings", marker="o")
    plt.plot(future_months.astype(str), forecast, label="Forecasted Net Savings", marker="x", linestyle="--", color="red")
    plt.xticks(rotation=45)
    plt.xlabel("Month")
    plt.ylabel("Net Savings ($)")
    plt.title("Net Savings Forecast for Next 6 Months")
    plt.legend()
    plt.grid(True)
    filename = "net_savings_forecast.png"
    plt.savefig(os.path.join("static", filename))   # Ensure the static directory exists
    plt.close()
    return filename

@app.route("/")
def index():
    total_income,total_expenses,net_savings,df, monthly_summary = get_expense_data()
    #app.logger.debug(f"Total Income: {total_income}, Total Expenses: {total_expenses}, Net Savings: {net_savings}")
    df_filtered_without_salary,df_only_salary=removing_Incomes_data_from_df(df)
    analyzed_spending_by_category=analyze_spending_by_category(df_filtered_without_salary)
    saving_series, future_months, forecast=prediction_related(df)
    plot_needs_wants(df)
    plot_actual_vs_forecasted_savings(saving_series, future_months, forecast)
    Visualize_suspicious_transactions_highlight_outliers(df)
    # Plot_monthly_income_vs_expenses = plot_monthly_income_vs_expenses(monthly_summary)
    Plot_monthly_income_vs_expenses=plot_monthly_income_vs_expenses(df)
    Plot_monthly_balance = plot_monthly_balance(monthly_summary)
    Plot_income_sources = plot_income_sources(df)
    Plot_needs_wants = plot_needs_wants(df)
    h2_h=Plot_actual_vs_forecasted_savings(df)
    #bar
    h3_h=plot_category_spendings(df_filtered_without_salary)
    h4_4=  plot_category_spendings(df_filtered_without_salary)
   
    return render_template("index.html", 
                           income_vs_expenses_chart=Plot_monthly_income_vs_expenses, 
                           balance_chart=Plot_monthly_balance,
                           income_sources_chart=Plot_income_sources,
                           correlation_chart=Plot_needs_wants,
                           h2_h=h2_h,
                           h3_h=h3_h,
                           h4_4=h4_4,
                           total_income=total_income, 
                           total_expenses=total_expenses, 
                           net_savings=net_savings)
    
# debt_chart=debt_chart,

if __name__ == "__main__":
    app.run(debug=True)
