"""
generate_dataset.py
-------------------
Generates a realistic synthetic loan collection dataset for Vastu Housing Finance
interview preparation, containing 115 records with various DPD buckets,
branches, collection agencies, and specific edge cases for validation testing.
"""

import csv
import random
from datetime import datetime, timedelta

def generate_loan_data(filepath="data/loan_data.csv", total_records=115):
    random.seed(42)  # For reproducible dataset

    branches = [
        "Mumbai - Andheri",
        "Pune - Shivaji Nagar",
        "Ahmedabad - SG Highway",
        "Indore - Vijay Nagar",
        "Jaipur - MI Road",
        "Bengaluru - Whitefield",
        "Delhi - Connaught Place",
        "Chennai - Anna Nagar"
    ]

    agencies = [
        "In-House Recovery Team",
        "Apex Recovery Solutions",
        "Surya FinServe Collections",
        "Swift Resolution Agents",
        "Pioneer Field Solutions"
    ]

    first_names = [
        "Aarav", "Amit", "Ananya", "Deepak", "Kavita", "Manoj", "Neha", "Pooja", 
        "Rahul", "Rajesh", "Ramesh", "Rohit", "Sachin", "Sanjay", "Sneha", "Sunil",
        "Suresh", "Vikram", "Vikas", "Priya", "Anil", "Meera", "Kunal", "Harish",
        "Gaurav", "Naveen", "Swati", "Divya", "Alok", "Preeti", "Arun", "Bhavna"
    ]

    last_names = [
        "Sharma", "Verma", "Patel", "Kulkarni", "Deshmukh", "Gupta", "Joshi", "Mehta",
        "Nair", "Iyer", "Reddy", "Singh", "Yadav", "Chauhan", "Agarwal", "Bansal",
        "Pandey", "Mishra", "Saxena", "Trivedi", "Rathore", "Bhatia", "Malhotra", "Shukla"
    ]

    base_due_date = datetime(2026, 9, 5)

    records = []

    # Generate 105 clean and varied standard records
    for i in range(1, 106):
        loan_id = f"LN{1000 + i}"
        customer_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        branch = random.choice(branches)
        agency = random.choice(agencies)
        loan_amount = random.randint(15, 65) * 50000  # 7,50,000 to 32,50,000
        due_amount = random.randint(12, 45) * 1000     # 12,000 to 45,000

        # Distribution of delinquency
        # 40% Current (0 DPD), 25% Early (1-30), 15% Mid (31-60), 10% Late (61-90), 10% 90+ DPD
        rand_bucket = random.random()
        if rand_bucket < 0.40:
            dpd = 0
            # Current loans are either fully paid or on track
            paid_amount = due_amount if random.random() < 0.85 else int(due_amount * random.uniform(0.5, 0.95))
            pay_date = (base_due_date - timedelta(days=random.randint(0, 4))).strftime("%Y-%m-%d")
        elif rand_bucket < 0.65:
            dpd = random.randint(1, 30)
            paid_amount = int(due_amount * random.choice([0.0, 0.3, 0.5, 0.7, 1.0]))
            pay_date = (base_due_date + timedelta(days=dpd)).strftime("%Y-%m-%d") if paid_amount > 0 else ""
        elif rand_bucket < 0.80:
            dpd = random.randint(31, 60)
            paid_amount = int(due_amount * random.choice([0.0, 0.0, 0.25, 0.5]))
            pay_date = (base_due_date + timedelta(days=dpd - 10)).strftime("%Y-%m-%d") if paid_amount > 0 else ""
        elif rand_bucket < 0.90:
            dpd = random.randint(61, 90)
            paid_amount = int(due_amount * random.choice([0.0, 0.0, 0.2]))
            pay_date = (base_due_date + timedelta(days=dpd - 20)).strftime("%Y-%m-%d") if paid_amount > 0 else ""
        else:
            dpd = random.randint(91, 180)
            paid_amount = 0  # Severe delinquency usually unpaid
            pay_date = ""

        records.append({
            "loan_id": loan_id,
            "customer_name": customer_name,
            "branch": branch,
            "collection_agency": agency,
            "loan_amount": loan_amount,
            "due_amount": due_amount,
            "paid_amount": paid_amount,
            "due_date": base_due_date.strftime("%Y-%m-%d"),
            "payment_date": pay_date,
            "days_past_due": dpd
        })

    # Add deliberate edge cases (Records 106 to 115) to rigorously test validation!
    edge_cases = [
        # Edge Case 1: Missing loan_id
        {
            "loan_id": "",
            "customer_name": "Rohan Deshpande",
            "branch": "Mumbai - Andheri",
            "collection_agency": "In-House Recovery Team",
            "loan_amount": 1500000,
            "due_amount": 25000,
            "paid_amount": 25000,
            "due_date": "2026-09-05",
            "payment_date": "2026-09-04",
            "days_past_due": 0
        },
        # Edge Case 2: Duplicate loan_id (matches LN1015)
        {
            "loan_id": "LN1015",
            "customer_name": "Duplicate Entry Record",
            "branch": "Pune - Shivaji Nagar",
            "collection_agency": "Apex Recovery Solutions",
            "loan_amount": 1200000,
            "due_amount": 20000,
            "paid_amount": 10000,
            "due_date": "2026-09-05",
            "payment_date": "2026-09-20",
            "days_past_due": 15
        },
        # Edge Case 3: Negative loan_amount
        {
            "loan_id": "LN1108",
            "customer_name": "Kailash Chand",
            "branch": "Jaipur - MI Road",
            "collection_agency": "Swift Resolution Agents",
            "loan_amount": -500000,
            "due_amount": 15000,
            "paid_amount": 0,
            "due_date": "2026-09-05",
            "payment_date": "",
            "days_past_due": 45
        },
        # Edge Case 4: Negative due_amount
        {
            "loan_id": "LN1109",
            "customer_name": "Anita Sengupta",
            "branch": "Delhi - Connaught Place",
            "collection_agency": "Surya FinServe Collections",
            "loan_amount": 1800000,
            "due_amount": -18000,
            "paid_amount": 0,
            "due_date": "2026-09-05",
            "payment_date": "",
            "days_past_due": 60
        },
        # Edge Case 5: Negative paid_amount
        {
            "loan_id": "LN1110",
            "customer_name": "Venkatesh Rao",
            "branch": "Bengaluru - Whitefield",
            "collection_agency": "Pioneer Field Solutions",
            "loan_amount": 2200000,
            "due_amount": 32000,
            "paid_amount": -5000,
            "due_date": "2026-09-05",
            "payment_date": "",
            "days_past_due": 30
        },
        # Edge Case 6: Payment amount greater than due amount (paid > due)
        {
            "loan_id": "LN1111",
            "customer_name": "Simran Kaur",
            "branch": "Ahmedabad - SG Highway",
            "collection_agency": "In-House Recovery Team",
            "loan_amount": 2500000,
            "due_amount": 20000,
            "paid_amount": 35000,  # Overpayment: paid > due
            "due_date": "2026-09-05",
            "payment_date": "2026-09-05",
            "days_past_due": 0
        },
        # Edge Case 7: Corrupted / invalid date format
        {
            "loan_id": "LN1112",
            "customer_name": "Tariq Mansoor",
            "branch": "Indore - Vijay Nagar",
            "collection_agency": "Surya FinServe Collections",
            "loan_amount": 1400000,
            "due_amount": 22000,
            "paid_amount": 22000,
            "due_date": "05/09/2026-INVALID",  # Invalid date string
            "payment_date": "2026-09-05",
            "days_past_due": 0
        },
        # Edge Case 8: Missing due_date
        {
            "loan_id": "LN1113",
            "customer_name": "Pooja Hegde",
            "branch": "Chennai - Anna Nagar",
            "collection_agency": "Apex Recovery Solutions",
            "loan_amount": 1900000,
            "due_amount": 28000,
            "paid_amount": 0,
            "due_date": "",  # Missing due date
            "payment_date": "",
            "days_past_due": 35
        },
        # Edge Case 9: Negative Days Past Due (DPD < 0)
        {
            "loan_id": "LN1114",
            "customer_name": "Manish Tiwari",
            "branch": "Pune - Shivaji Nagar",
            "collection_agency": "In-House Recovery Team",
            "loan_amount": 1600000,
            "due_amount": 24000,
            "paid_amount": 24000,
            "due_date": "2026-09-05",
            "payment_date": "2026-08-31",
            "days_past_due": -5  # Negative DPD
        },
        # Edge Case 10: Missing customer_name and branch
        {
            "loan_id": "LN1115",
            "customer_name": "",
            "branch": "",
            "collection_agency": "Swift Resolution Agents",
            "loan_amount": 1750000,
            "due_amount": 26000,
            "paid_amount": 13000,
            "due_date": "2026-09-05",
            "payment_date": "2026-09-15",
            "days_past_due": 10
        }
    ]

    records.extend(edge_cases)

    # Write out CSV
    fieldnames = [
        "loan_id", "customer_name", "branch", "collection_agency",
        "loan_amount", "due_amount", "paid_amount", "due_date",
        "payment_date", "days_past_due"
    ]

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Successfully generated {len(records)} records in '{filepath}'.")

if __name__ == "__main__":
    generate_loan_data()
