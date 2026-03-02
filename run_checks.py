import duckdb
import pandas as pd
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

con = duckdb.connect(database=":memory:")

# Run SQL tests
sql_text = Path("sql/tests.sql").read_text()
con.execute(sql_text)

# Export exceptions
exceptions_df = con.execute("SELECT * FROM all_exceptions").df()
exceptions_df.to_csv("outputs/exceptions_report.csv", index=False)

# Export summaries
summary_df = con.execute("SELECT * FROM summary").df()
by_type_df = con.execute("SELECT * FROM exceptions_by_type").df()
by_service_df = con.execute("SELECT * FROM exceptions_by_service").df()

summary_df.to_csv("outputs/summary.csv", index=False)
by_type_df.to_csv("outputs/exceptions_by_type.csv", index=False)
by_service_df.to_csv("outputs/exceptions_by_service.csv", index=False)

# Print quick readout for you
prod_deployments = int(summary_df["prod_deployments"].iloc[0])
exc_count = len(exceptions_df)
compliance_rate = 0.0 if prod_deployments == 0 else (1 - exc_count / prod_deployments)

print("✅ Exports created in /outputs")
print(f"Prod deployments: {prod_deployments}")
print(f"Exceptions found: {exc_count}")
print(f"Compliance rate (rough): {compliance_rate:.2%}")
print("\nTop exception types:")
print(by_type_df.head(5).to_string(index=False))