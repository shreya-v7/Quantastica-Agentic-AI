def analyze_uploaded_data(fetch_bank_transactions, fetch_credit_report, fetch_mf_transactions):
    # Salary
    salary = 0
    sip_total = 0
    for bank in fetch_bank_transactions["bankTransactions"]:
        for txn in bank.get("txns", []):
            amount = float(txn[0])
            desc = txn[1].lower()
            if txn[3] == 1 and "salary" in desc:
                salary += amount
            elif "sip" in desc or "mutual" in desc:
                sip_total += amount

    # Loans
    credit = fetch_credit_report["creditReports"][0]["creditReportData"]["creditAccount"]["creditAccountSummary"]
    outstanding = float(credit["totalOutstandingBalance"]["outstandingBalanceAll"])

    # MF total investment
    mf_total = 0
    for scheme in fetch_mf_transactions["mfTransactions"]:
        for txn in scheme["txns"]:
            mf_total += txn[4]  # transactionAmount

    return {
        "UserType": "Salaried",
        "GrossIncome": salary,
        "EPF": 50000,  # Can be made dynamic if EPF file is added
        "Insurance": 30000,  # Assume user has insurance for now
        "SIP": sip_total,
        "LoanOutstanding": outstanding,
        "MFInvestment": mf_total
    }
