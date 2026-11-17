import csv, sys
from datetime import date
from decimal import Decimal
path = sys.argv[1]
rates = {r["currency"]: Decimal(r["rate_to_brl"]) for r in csv.DictReader(open("data/taxas_cambio.csv", encoding="utf-8"))}
print(f"{'id':7}{'status':10}{'moeda':6}{'noites bug':>11}{'noites ok':>10}{'BRL bug':>12}{'BRL ok':>10}  entra(bug/ok)")
for r in csv.DictReader(open(path, encoding="utf-8")):
    ci, co, rooms = date.fromisoformat(r["checkin_date"]), date.fromisoformat(r["checkout_date"]), int(r["rooms"])
    amt, rate = Decimal(r["amount"]), rates[r["currency"]]
    nb, nok = (co.day - ci.day) * rooms, (co - ci).days * rooms
    bb, bok = Decimal(str(float(amt) / float(rate))), amt * rate
    eb, eok = r["status"] != "CANCELLED", r["status"] == "CONFIRMED"
    flag = "  <==" if (nb != nok or bb != bok or eb != eok) and (eb or eok) else ""
    print(f"{r['reservation_id']:7}{r['status']:10}{r['currency']:6}{nb:>11}{nok:>10}{bb:>12.2f}{bok:>10.2f}  {'S' if eb else 'N'}/{'S' if eok else 'N'}{flag}")
