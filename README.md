User Bank Expenses Python Flask Project

This is a Flask-based web application for analyzing personal bank expenses using an Excel file. The app provides various financial insights, such as income vs. expenses, category-wise spending, suspicious transaction detection, and savings forecasting.

Features

Income vs. Expenses Analysis: Monthly comparison of income and expenses.

Spending by Category: Visualizes spending habits across different categories.

Needs vs. Wants Analysis: Breaks down essential vs. discretionary spending.

Savings Forecast: Uses ARIMA modeling to predict future savings.

Outlier Detection: Highlights suspicious transactions using Isolation Forest.

Installation

Clone the Repository

Using GitHub CLI:

gh repo clone hadizgheib/user-bank-expenses-python-flask-project

Or using Git:

git clone https://github.com/hadizgheib/user-bank-expenses-python-flask-project.git
cd user-bank-expenses-python-flask-project

Set Up a Virtual Environment (Optional but Recommended)

python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Ensure Data File Exists

Make sure the data/expenses.xlsx file is present in the data directory.

Running the Application

Run the Flask app:

python app.py

The application will be accessible at http://127.0.0.1:5000/.

File Structure

📂 user-bank-expenses-python-flask-project
│── 📂 data
│   ├── expenses.xlsx
│── 📂 static
│   ├── (Generated images will be stored here)
│── 📂 templates
│   ├── index.html
│── app.py
│── requirements.txt
│── README.md

Dependencies

This project requires:

Flask

Pandas

Matplotlib

Seaborn

OpenPyXL (for Excel file support)

Statsmodels (for ARIMA forecasting)

Scikit-learn (for anomaly detection)

Install them using:

pip install -r requirements.txt

Future Improvements

Add user authentication.

Allow users to upload their own Excel files.

Improve UI with interactive visualizations.

License

This project is open-source and available under the MIT License.

