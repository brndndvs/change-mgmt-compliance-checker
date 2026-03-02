import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

fake = Faker()
random.seed(42)

N_DEPLOYMENTS = 1500
N_TICKETS = 1200

start = datetime(2025, 10, 1)
end = datetime(2025, 12, 31)

services = ["billing-api", "ads-service", "playback", "auth", "search", "recommendations"]
deployers = ["svc-cicd", "alice", "bob", "carol", "dave"]
approver_roles = ["manager", "cab", "sre"]
pipelines = ["github-actions", "jenkins", "gitlab-ci"]

def rand_dt():
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

# --- Tickets ---
tickets = []
for i in range(N_TICKETS):
    ticket_id = f"CHG-{10000+i}"
    change_type = random.choices(["standard", "emergency"], weights=[0.9, 0.1])[0]
    requested_at = rand_dt()

    # Approval usually after request, sometimes missing or late (to create exceptions)
    approved_at = requested_at + timedelta(minutes=random.randint(10, 72*60))
    status = "approved"
    testing_evidence = random.choices(["yes", "no"], weights=[0.92, 0.08])[0]
    risk_level = random.choices(["low", "med", "high"], weights=[0.6, 0.3, 0.1])[0]
    approver_role = random.choice(approver_roles)

    # inject some bad tickets
    if random.random() < 0.03:
        status = "rejected"
    if random.random() < 0.03:
        approved_at = None  # missing approval evidence

    tickets.append({
        "ticket_id": ticket_id,
        "change_type": change_type,
        "requested_at": requested_at,
        "approved_at": approved_at,
        "approver_role": approver_role,
        "testing_evidence": testing_evidence,
        "status": status,
        "risk_level": risk_level
    })

tickets_df = pd.DataFrame(tickets)

# --- Deployments ---
deployments = []
for i in range(N_DEPLOYMENTS):
    deployment_id = f"DPL-{50000+i}"
    service = random.choice(services)
    environment = random.choices(["prod", "non-prod"], weights=[0.65, 0.35])[0]
    deployed_at = rand_dt()
    deployed_by = random.choice(deployers)
    commit_sha = fake.sha1()
    pipeline = random.choice(pipelines)

    # link to a ticket most of the time, but allow missing ticket exceptions
    ticket_id = random.choice(tickets_df["ticket_id"].tolist())
    if random.random() < 0.06 and environment == "prod":
        ticket_id = None

    deployments.append({
        "deployment_id": deployment_id,
        "service": service,
        "environment": environment,
        "deployed_at": deployed_at,
        "deployed_by": deployed_by,
        "commit_sha": commit_sha,
        "ticket_id": ticket_id,
        "pipeline": pipeline
    })

deployments_df = pd.DataFrame(deployments)

# Save
tickets_df.to_csv("data/change_tickets.csv", index=False)
deployments_df.to_csv("data/deployments.csv", index=False)

print("✅ Generated data/change_tickets.csv and data/deployments.csv")