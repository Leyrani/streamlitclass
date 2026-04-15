

import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="Hand-Washing and Mortality Rates",
    layout="wide"
)

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv("yearly_deaths_by_clinic-1.csv")
    df["Mortality Rate"] = df["Deaths"] / df["Birth"]
    df["Mortality %"] = df["Mortality Rate"] * 100
    df["Period"] = df["Year"].apply(lambda x: "Before hand-washing (1841–1846)" if x < 1847 else "After hand-washing (1847–1849)")
    return df

df = load_data()

# Title and description

st.title("The Impact of Hand-Washing on Maternal Mortality")
st.write(
    """
    This Streamlit app uses data from Dr. Ignaz Semmelweis's clinics to show how mortality changed over time.
    The visualizations compare yearly deaths and mortality rates across two clinics, with special attention to the introduction of hand-washing in 1847.
    """
)

# Sidebar filter

st.sidebar.header("Filters")
selected_clinics = st.sidebar.multiselect(
    "Select clinic(s):",
    options=sorted(df["Clinic"].unique()),
    default=sorted(df["Clinic"].unique())
)

year_range = st.sidebar.slider(
    "Select year range:",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=(int(df["Year"].min()), int(df["Year"].max()))
)

filtered_df = df[
    (df["Clinic"].isin(selected_clinics)) &
    (df["Year"].between(year_range[0], year_range[1]))
].copy()

# Summary metrics

st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

overall_avg = filtered_df["Mortality %"].mean()

clinic1_before = df[(df["Clinic"] == "clinic 1") & (df["Year"] < 1847)]["Mortality %"].mean()
clinic1_after = df[(df["Clinic"] == "clinic 1") & (df["Year"] >= 1847)]["Mortality %"].mean()
clinic1_drop = clinic1_before - clinic1_after

with col1:
    st.metric("Average mortality rate", f"{overall_avg:.2f}%")

with col2:
    st.metric("Clinic 1 avg. before 1847", f"{clinic1_before:.2f}%")

with col3:
    st.metric("Clinic 1 drop after 1847", f"{clinic1_drop:.2f} percentage points")

# Visualization 1: Mortality rate over time

st.subheader("Mortality Rate by Year")

line_chart = (
    alt.Chart(filtered_df)
    .mark_line(point=True, strokeWidth=3)
    .encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Mortality %:Q", title="Mortality Rate (%)"),
        color=alt.Color("Clinic:N", title="Clinic"),
        tooltip=["Year", "Clinic", "Birth", "Deaths", alt.Tooltip("Mortality %:Q", format=".2f")]
    )
    .properties(height=420)
)

rule_df = pd.DataFrame({"Year": [1847]})
rule = (
    alt.Chart(rule_df)
    .mark_rule(strokeDash=[6, 6], size=2)
    .encode(x="Year:O")
)

label_df = pd.DataFrame({
    "Year": [1847],
    "Mortality %": [filtered_df["Mortality %"].max() if not filtered_df.empty else 0],
    "label": ["Hand-washing introduced"]
})

label = (
    alt.Chart(label_df)
    .mark_text(align="left", dx=6, dy=-10, fontSize=12)
    .encode(
        x="Year:O",
        y="Mortality %:Q",
        text="label:N"
    )
)

st.altair_chart(line_chart + rule + label, use_container_width=True)

# Visualization 2: Before vs. after comparison

st.subheader("Average Mortality Rate Before and After Hand-Washing")

summary = (
    df[df["Clinic"].isin(selected_clinics)]
    .groupby(["Clinic", "Period"], as_index=False)["Mortality %"]
    .mean()
)

bar_chart = (
    alt.Chart(summary)
    .mark_bar()
    .encode(
        x=alt.X("Clinic:N", title="Clinic"),
        y=alt.Y("Mortality %:Q", title="Average Mortality Rate (%)"),
        color=alt.Color("Period:N", title="Period"),
        column=alt.Column("Period:N", title=None),
        tooltip=["Clinic", "Period", alt.Tooltip("Mortality %:Q", format=".2f")]
    )
    .properties(height=400)
)

st.altair_chart(bar_chart, use_container_width=True)

# Optional data table

with st.expander("Show cleaned dataset"):
    st.dataframe(
        filtered_df[["Year", "Clinic", "Birth", "Deaths", "Mortality %"]]
        .sort_values(["Clinic", "Year"]),
        use_container_width=True
    )

# Findings / interpretation

st.subheader("Findings")
st.write(
    """
    The mortality rate in Clinic 1 was much higher than in Clinic 2 during the early years, but it dropped sharply after 1847.
    This pattern supports Semmelweis's argument that hand-washing significantly reduced deaths.
    Comparing mortality rates instead of raw death counts makes the change easier to see because the number of births varies from year to year.
    """
)

st.caption("Made by Rai Karpen and Johanne Rigaud")
