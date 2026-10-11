"""Pravi izmisljenu tabelu support tiketa (ne koristimo tudje/poverljive podatke)."""
import random
import pandas as pd

random.seed(1)
rows = []
for i in range(1, 501):
    rows.append({
        "TicketNumber": f"TCK-{i:06d}",
        "Priority": random.choice(["P1", "P2", "P3", "P4"]),
        "Channel": random.choice(["Email", "Chat", "Phone", "WebForm"]),
        "ProductArea": random.choice(["Billing", "Security", "Telephony", "Integrations"]),
        "Summary": random.choice(["Billing invoice mismatch detected", "High latency during peak hours",
                                  "Customer reports call interruptions", "Password reset not working"]),
        "ResolutionHours": round(random.uniform(1, 120), 1) if random.random() > 0.05 else None,
    })
pd.DataFrame(rows).to_excel("data/support_tickets.xlsx", index=False)
print("OK: data/support_tickets.xlsx")
