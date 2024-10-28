import random

def get_electricity_data():
    current_usage = random.uniform(0.5, 5.0)
    total_usage = random.uniform(200, 1000)
    total_bill = total_usage * 0.20
    return current_usage, total_usage, total_bill