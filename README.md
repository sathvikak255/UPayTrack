# 💸 UpayTrack – UPI Expense Tracker

## About the Project

UpayTrack is a personal finance tool designed to automatically track and categorize UPI transactions. It extracts essential details such as transaction amounts, merchants, and timestamps from UPI messages, providing users with a clear overview of their spending habits.

## Project Overview

The system processes UPI transaction messages to extract relevant information and categorize expenses accordingly.

<!-- You can include a diagram or flowchart here -->
<!-- ![Flowchart](path_to_image.png) -->

---

### Key Features

- **Automated Parsing**: Extracts transaction details from UPI messages without manual input.
- **Expense Categorization**: Classifies expenses into categories like Food, Travel, and Bills.
- **Budget Monitoring**: Tracks monthly budgets and alerts users when spending thresholds are crossed.
- **User-Friendly Interface**: Provides an intuitive dashboard to view transaction history and spending patterns.

---

## Tech Stack

- **Backend**: Python, Flask  
- **Database**: PostgreSQL (with SQLite support for development)  
- **Frontend**: HTML, CSS, JavaScript  
- **Others**: SQLAlchemy, Jinja2 Templates  

---

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sathvikak255/UpayTrack.git
   cd UpayTrack
   ```
2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirement.txt
   ```
4. **Configure the Database**:
   - Ensure PostgreSQL is installed and running.
   - Create a new database and update the config.py file with your database credentials.
5. **Initialize the Database**:
   ```bash
   python create_db.py
   ```
6. **Run the Application**:
   ```bash
   python run.py    # or $flask run
   ```

### Future Enhancements

- Bank Statement Integration: Import and parse bank statements for comprehensive expense tracking.
- Advanced Analytics: Implement predictive analytics to forecast future expenses.
- Mobile Application: Develop a mobile version for on-the-go expense tracking.
- Multi-Currency Support: Enable tracking expenses in different currencies for international users.

