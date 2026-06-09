import streamlit as st
from scheduler import build_schedule

st.set_page_config(page_title="Physician Scheduler", layout="wide")

st.title("Physician Scheduling Tool")

option = st.radio("Mode", ["C (Balanced)", "B (Strict)"])

blocks = list(range(24))

st.subheader("Enter vacations (comma-separated block numbers)")

vacations = {}
for d in ["D1","D2","D3","D4","D5","D6"]:
    txt = st.text_input(d)
    vacations[d] = [int(x) for x in txt.split(",") if x.strip().isdigit()]

st.write("Click generate to create schedule")

if st.button("Generate Schedule"):
    df = build_schedule(
        blocks=blocks,
        vacations=vacations,
        preferences={},
        option=option[0]
    )

    st.dataframe(df)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "schedule.csv",
        "text/csv"
    )
