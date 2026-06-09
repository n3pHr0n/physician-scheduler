from ortools.sat.python import cp_model
import pandas as pd

DOCTORS = ["D1","D2","D3","D4","D5","D6"]
HOSPITALS = ["H1","H2","H3","H4"]

def build_schedule(blocks, vacations, preferences, option="C"):
    model = cp_model.CpModel()

    work = {}
    off = {}

    # VARIABLES
    for d in DOCTORS:
        for b in blocks:
            off[d,b] = model.NewBoolVar(f"off_{d}_{b}")
            for h in HOSPITALS:
                work[d,b,h] = model.NewBoolVar(f"{d}_{h}_{b}")

    # CONSTRAINTS

    for d in DOCTORS:
        for b in blocks:
            model.Add(sum(work[d,b,h] for h in HOSPITALS) + off[d,b] == 1)

    for b in blocks:
        for h in HOSPITALS:
            model.Add(sum(work[d,b,h] for d in DOCTORS) == 1)

        model.Add(sum(off[d,b] for d in DOCTORS) == 2)

    for d in DOCTORS:
        model.Add(sum(work[d,b,h] for b in blocks for h in HOSPITALS) == 16)

    # VACATIONS
    for d, vlist in vacations.items():
        for b in vlist:
            model.Add(off[d,b] == 1)
            for h in HOSPITALS:
                model.Add(work[d,b,h] == 0)

    # D1 cannot do H1
    for b in blocks:
        model.Add(work["D1",b,"H1"] == 0)

    # OPTION B HARD CONSTRAINT
    if option == "B":
        for d in DOCTORS:
            for b in range(len(blocks)-3):
                model.Add(sum(1 - off[d,b+i] for i in range(4)) <= 3)

    # OBJECTIVE (Option C style)
    if option == "C":
        objective = []
        for d in DOCTORS:
            for b in blocks:
                for h in HOSPITALS:
                    weight = preferences.get(d, {}).get(h, 0)
                    objective.append(weight * work[d,b,h])
        model.Maximize(sum(objective))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.Solve(model)

    # BUILD OUTPUT
    rows = []
    for b in blocks:
        row = {"Block": b}
        for h in HOSPITALS:
            for d in DOCTORS:
                if solver.Value(work[d,b,h]):
                    row[h] = d
        row["Off"] = [d for d in DOCTORS if solver.Value(off[d,b])]
        rows.append(row)

    return pd.DataFrame(rows)
