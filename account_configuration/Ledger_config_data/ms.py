import streamlit as st
import pandas as pd

# Load Excel
ledger_df = pd.read_excel("Ledger_Library.xlsx")

st.title("🧾 Ledger Entry Input")

# Get unique dropdowns
C1_options = sorted(ledger_df['C1'].dropna().unique())
C1 = st.selectbox("Select Main Account Type (C1)", C1_options)

C2_options = sorted(ledger_df[ledger_df['C1'] == C1]['C2'].dropna().unique())
C2 = st.selectbox("Select Sub Account Type (C2)", C2_options)

C3_options = sorted(ledger_df[(ledger_df['C1'] == C1) & (ledger_df['C2'] == C2)]['C3'].dropna().unique())
C3 = st.selectbox("Select Account Name (C3)", C3_options)

st.markdown("---")
st.markdown("### ✍️ Enter Additional Info")

C4 = st.text_input("Enter Account Code (C4)")
C5 = st.text_input("Enter Remarks/Info (C5)")

if st.button("Save Entry"):
    new_entry = {
        "C1": C1, "C2": C2, "C3": C3,
        "C4": C4, "C5": C5, "G_CODE": "G1"
    }

    # Append and Save
    ledger_df = ledger_df.append(new_entry, ignore_index=True)
    ledger_df.to_excel("Updated_Ledger_Library.xlsx", index=False)
    st.success("✅ Entry saved successfully!")

st.markdown("---")
if st.checkbox("🔧 Manually Add All Fields"):
    C1_new = st.text_input("Manual C1")
    C2_new = st.text_input("Manual C2")
    C3_new = st.text_input("Manual C3")
    C4_new = st.text_input("Manual C4")
    C5_new = st.text_input("Manual C5")

    if st.button("Save Manual Entry"):
        new_manual_entry = {
            "C1": C1_new, "C2": C2_new, "C3": C3_new,
            "C4": C4_new, "C5": C5_new, "G_CODE": "G1"
        }
        ledger_df = ledger_df.append(new_manual_entry, ignore_index=True)
        ledger_df.to_excel("Updated_Ledger_Library.xlsx", index=False)
        st.success("✅ Manual entry saved successfully!")
