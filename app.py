import streamlit as st
import pandas as pd
import numpy as np
import base64
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title = "Sri Lanka Environmental Dashboard", layout = "wide", initial_sidebar_state = "expanded")

data = pd.read_csv("environment.csv")

# Background image
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(image_path):
    base64_img = get_base64(image_path)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{base64_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .block-container {{
            padding: 5rem 2rem 2rem 2rem;
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 16px;
        }}
        .stPlotlyChart > div {{
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
        }}
        section.main > div {{
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        </style>
    """, unsafe_allow_html=True)

def render_dashboard(filtered_data, name_prefix, color):
    indicators = filtered_data["Indicator Name"].unique()

    st.sidebar.subheader("Line & Bar Chart Filters")
    selected_indicator = st.sidebar.selectbox("Select One Indicator", indicators, key = f"{name_prefix}_line")
    filtered_df = filtered_data[filtered_data["Indicator Name"] == selected_indicator]

    years = filtered_df["Year"].dropna().unique()
    min_year, max_year = int(years.min()), int(years.max())
    year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year), key = f"{name_prefix}_year")
    range_df = filtered_df[(filtered_df["Year"] >= year_range[0]) & (filtered_df["Year"] <= year_range[1])]
     
    st.sidebar.subheader("Area Chart Filters")
    selected_area_indicators = st.sidebar.multiselect("Select Indicators", indicators, default = indicators[:2], key = f"{name_prefix}_area")

    st.sidebar.subheader("Scatter Plot Filters")
    scatter_selection = st.sidebar.multiselect("Select Two Indicators", indicators, default = indicators[:2], key = f"{name_prefix}_scatter")

# Line and Bar Charts
    col1, _, col2 = st.columns([1, 0.05, 1])
    with col1:
        st.markdown("#### :chart_with_upwards_trend: Line Chart")
        fig = px.line(range_df, x =  "Year", y = "Value", title = selected_indicator, markers = True, template = "plotly_dark")
        fig.update_traces(line = dict(color = color, width = 2), marker = dict(size = 8, opacity = 0.75))
        fig.update_layout(
            title = dict(text = selected_indicator, font = dict(size = 14), x = 0.3),
            xaxis_title = "Year", yaxis_title = "Value",
            xaxis = dict(title_font=dict(size = 12), tickfont = dict(size = 11)),
            yaxis = dict(title_font = dict(size = 12), tickfont = dict(size = 11)),
            margin = dict(t = 75)
        )
        st.plotly_chart(fig, use_container_width = True)

    with col2:
        st.markdown("#### :bar_chart: Bar Chart")
        fig = px.bar(range_df.sort_values("Year"), x = "Year", y = "Value", title = selected_indicator, template = "plotly_dark")
        fig.update_traces(marker_color = color, opacity = 0.75)
        fig.update_layout(
            title = dict(text = selected_indicator, font = dict(size = 14), x = 0.3),
            xaxis_title = "Year", yaxis_title = "Value",
            xaxis = dict(title_font = dict(size = 12), tickfont = dict(size = 11)),
            yaxis = dict(title_font = dict(size = 12), tickfont = dict(size = 11)),
            margin = dict(t = 75)
        )
        st.plotly_chart(fig, use_container_width = True)

# Area and Scatter Charts
    col3, _, col4 = st.columns([1, 0.05, 1])
    with col3:
        st.markdown("#### :herb: Area Chart")
        if selected_area_indicators:
            area_df = filtered_data[filtered_data["Indicator Name"].isin(selected_area_indicators)]
            area_df = area_df.pivot_table(index = "Year", columns = "Indicator Name", values = "Value").dropna().sort_index().reset_index()
            fig = px.area(area_df, x="Year", y = area_df.columns[1:], title = "Area Chart of Selected Indicators", template = "plotly_dark")
            fig.update_traces(opacity = 0.75)
            fig.update_layout(
                title = dict(text = "Area Chart of Selected Indicators", font = dict(size = 14), x = 0.3),
                xaxis_title = "Year", yaxis_title="Value",
                legend = dict(title = "Indicators", orientation = "v", yanchor = "bottom", y = 0.15, xanchor = "center", x = 0.60, font = dict(size = 10, color = "white")),
                margin = dict(t = 75)
            )
            st.plotly_chart(fig, use_container_width = True)
        else:
            st.info("Please select at least one indicator.")

    with col4:
        st.markdown("#### :large_blue_circle: Scatter Plot & Correlation")
        if len(scatter_selection) == 2:
            scatter_df = filtered_data[filtered_data["Indicator Name"].isin(scatter_selection)]
            scatter_df = scatter_df.pivot(index = "Year", columns = "Indicator Name", values = "Value").dropna()
            if not scatter_df.empty:
                corr = scatter_df.corr().iloc[0, 1]
                fig = px.scatter(scatter_df, x = scatter_selection[0], y = scatter_selection[1],
                                 title = f"{scatter_selection[0]} vs {scatter_selection[1]}", template = "plotly_dark")
                fig.update_traces(marker = dict(color = color, opacity = 0.75, line = dict(width = 1, color = "white")))
                fig.update_layout(
                    title=dict(text = f"{scatter_selection[0]} vs {scatter_selection[1]}", font = dict(size = 14), x = 0.3),
                    xaxis_title = scatter_selection[0],
                    yaxis_title = scatter_selection[1],
                    legend = dict(orientation = "h", yanchor = "bottom", y = 0.2, xanchor = "center", x = 0.80, font = dict(size = 12, color = "white")),
                    margin = dict(t = 75)
                )
                fig.add_trace(go.Scatter(x = [None], y = [None], mode = 'markers', marker = dict(size = 7, color = color),
                                         name = f"Correlation: {corr:.2f}"))
                st.plotly_chart(fig, use_container_width = True)
            else:
                st.warning("Not enough data for scatter plot.")
        else:
            st.info("Please select exactly 2 indicators.")

# Page navigation
page = st.sidebar.radio("*Go to*", ["Overview", "Agriculture"])

if page == "Overview":
    set_background("sri_lanka.jpg")
    st.title("Sri Lanka Environmental Dashboard")
    st.markdown("### Overview")
    st.markdown("The Sri Lanka Environmental Dashboard is a comprehensive and interactive platform designed to explore key indicators related to the country’s agricultural performance and rural development progress. Developed using data published by the Humanitarian Data Exchange (HDX), along with global indicators compiled by the Food and Agriculture Organization of the United Nations, this tool provides valuable insights about agricultural and rural development trends across multiple years.")
    st.markdown("Agriculture and rural development are of critical importance to Sri Lanka’s economy and social well-being. The 70% of the world's poor who live in rural areas, agriculture remains the main source of income and employment. However, challenges such as land degradation, resource depletion, and water scarcity threaten long-term sustainability. Strengthening rural development not only enhances food security and economic resilience but also plays a vital role in achieving the United Nations Sustainable Development Goals, particularly those related to poverty reduction, hunger, and inclusive growth.")
    st.markdown("### Column Descriptions\n- *Year: The year the data was recorded.\n- **Indicator Name: The name of the indicator. \n- **Indicator Code: A unique identifier for each indicator.\n- **Value*: The numeric value of the indicator for the given year.")
    
    st.sidebar.subheader("Filters")
    search_keyword = st.sidebar.text_input("Search Indicator").strip().lower()
    all_indicators = sorted(data["Indicator Name"].unique())
    selected_indicator = st.sidebar.selectbox("Select Indicator", ["All"] + all_indicators)
    years = data["Year"].dropna().unique()
    min_year, max_year = int(years.min()), int(years.max())
    year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))
    filtered_data = data[(data["Year"] >= year_range[0]) & (data["Year"] <= year_range[1])]
    if selected_indicator != "All":
        filtered_data = filtered_data[filtered_data["Indicator Name"] == selected_indicator]
    if search_keyword:
        filtered_data = filtered_data[filtered_data["Indicator Name"].str.lower().str.contains(search_keyword)]

    if st.checkbox(":open_file_folder: *Show Filtered Dataset*"):
        st.dataframe(filtered_data)
        st.markdown(f":1234: Total Rows: {len(filtered_data)}")

elif page == "Environment":
    set_background("env.jpg")
    st.title(":ear_of_rice: Environmental Insights")



