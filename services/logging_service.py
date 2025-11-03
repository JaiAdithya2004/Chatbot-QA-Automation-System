from datetime import datetime
import os
import pandas as pd


def log_result(prompt: str, expected: str, actual: str, status: str) -> None:
    df = pd.DataFrame([
        {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Prompt": prompt,
            "Expected": expected,
            "Actual": actual,
            "Status": status,
        }
    ])
    file_path = "test_results.csv"
    file_exists = os.path.exists(file_path)
    file_empty = False
    if file_exists:
        try:
            file_empty = os.path.getsize(file_path) == 0
        except OSError:
            file_empty = True
    # Write header if file does not exist or is empty
    df.to_csv(file_path, mode="a", header=(not file_exists or file_empty), index=False)


