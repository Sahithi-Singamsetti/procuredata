
import streamlit as st
import plotly.express as px
import pandas as pd

from shared.database.connection import get_connection

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Spend Analytics",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("NASA Spend Analytics Dashboard")
st.caption("Fiscal Year 2025 | October 2024 – September 2025")

# --------------------------------------------------
# FETCH FILTER OPTIONS
# --------------------------------------------------

def get_filter_options():

    query = """
        SELECT MIN(action_date), MAX(action_date)
        FROM spend_transactions;
    """

    with get_connection() as connection:
        date_range = connection.execute(query).fetchone()

    with get_connection() as connection:
        suppliers = connection.execute(
            """
            SELECT DISTINCT recipient_name
            FROM spend_transactions
            ORDER BY recipient_name;
            """
        ).fetchall()

    with get_connection() as connection:
        categories = connection.execute(
            """
            SELECT DISTINCT product_or_service_code
            FROM spend_transactions
            WHERE product_or_service_code IS NOT NULL
            ORDER BY product_or_service_code;
            """
        ).fetchall()

    return date_range, suppliers, categories

# --------------------------------------------------
# BUILD FILTER CONDITIONS
# --------------------------------------------------

def build_filters(start_date, end_date, supplier, category):

    conditions = [
        "action_date >= %s",
        "action_date <= %s"
    ]

    parameters = [start_date, end_date]

    if supplier != "All Suppliers":
        conditions.append("recipient_name = %s")
        parameters.append(supplier)

    if category != "All Categories":
        conditions.append("product_or_service_code = %s")
        parameters.append(category)

    where_clause = " WHERE " + " AND ".join(conditions)

    return where_clause, parameters

# --------------------------------------------------
# FETCH KPI METRICS
# --------------------------------------------------

def get_spend_metrics(start_date, end_date, supplier, category):

    where_clause, parameters = build_filters(
        start_date, end_date, supplier, category
    )

    query = f"""
        SELECT
            COALESCE(SUM(federal_action_obligation), 0),
            COUNT(DISTINCT recipient_uei),
            COUNT(DISTINCT award_id_piid),
            COUNT(*)
        FROM spend_transactions
        {where_clause};
    """

    with get_connection() as connection:
        result = connection.execute(
            query, parameters
        ).fetchone()

    return result

# --------------------------------------------------
# FETCH MONTHLY SPENDING
# --------------------------------------------------

def get_monthly_spending(start_date, end_date, supplier, category):

    where_clause, parameters = build_filters(
        start_date, end_date, supplier, category
    )

    query = f"""
        SELECT
            DATE_TRUNC('month', action_date)::date AS spending_month,
            SUM(federal_action_obligation) AS monthly_net_spend
        FROM spend_transactions
        {where_clause}
        GROUP BY DATE_TRUNC('month', action_date)
        ORDER BY spending_month;
    """

    with get_connection() as connection:
        result = connection.execute(
            query, parameters
        ).fetchall()

    return result

# --------------------------------------------------
# FETCH TOP 10 SUPPLIERS
# --------------------------------------------------

def get_top_suppliers(start_date, end_date, supplier, category):

    where_clause, parameters = build_filters(
        start_date, end_date, supplier, category
    )

    query = f"""
        SELECT
            recipient_name,
            SUM(federal_action_obligation) AS total_spend
        FROM spend_transactions
        {where_clause}
        GROUP BY recipient_name
        ORDER BY total_spend DESC
        LIMIT 10;
    """

    with get_connection() as connection:
        result = connection.execute(
            query, parameters
        ).fetchall()

    return result

# --------------------------------------------------
# FETCH TOP 10 PROCUREMENT CATEGORIES
# --------------------------------------------------

def get_top_categories(start_date, end_date, supplier, category):

    where_clause, parameters = build_filters(
        start_date, end_date, supplier, category
    )

    query = f"""
        SELECT
            product_or_service_code,
            product_or_service_code_description,
            SUM(federal_action_obligation) AS total_spend
        FROM spend_transactions
        {where_clause}
        GROUP BY
            product_or_service_code,
            product_or_service_code_description
        ORDER BY total_spend DESC
        LIMIT 10;
    """

    with get_connection() as connection:
        result = connection.execute(
            query, parameters
        ).fetchall()

    return result

# --------------------------------------------------
# FETCH SPEND BREAKDOWN BY PROCUREMENT CATEGORY
# --------------------------------------------------

def get_category_breakdown(start_date, end_date, supplier, category):

    where_clause, parameters = build_filters(
        start_date, end_date, supplier, category
    )

    query = f"""
        SELECT
            product_or_service_code,
            product_or_service_code_description,
            SUM(federal_action_obligation) AS total_spend
        FROM spend_transactions
        {where_clause}
        GROUP BY
            product_or_service_code,
            product_or_service_code_description
        ORDER BY total_spend DESC
        LIMIT 10;
    """

    with get_connection() as connection:
        result = connection.execute(
            query, parameters
        ).fetchall()

    return result

# --------------------------------------------------
# FETCH TRANSACTION DETAILS
# --------------------------------------------------

def get_transaction_details(start_date, end_date, supplier, category):

    where_clause, parameters = build_filters(
        start_date, end_date, supplier, category
    )

    query = f"""
        SELECT
            action_date,
            award_id_piid,
            recipient_name,
            product_or_service_code,
            product_or_service_code_description,
            federal_action_obligation
        FROM spend_transactions
        {where_clause}
        ORDER BY action_date DESC
        LIMIT 500;
    """

    with get_connection() as connection:
        result = connection.execute(
            query, parameters
        ).fetchall()

    return result
# ==================================================
# DASHBOARD FILTERS
# ==================================================

st.subheader("Filters")

try:

    date_range, suppliers, categories = get_filter_options()

    min_date = date_range[0]
    max_date = date_range[1]

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_dates = st.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    with col2:

        supplier_options = ["All Suppliers"] + [
            row[0] for row in suppliers
        ]

        selected_supplier = st.selectbox(
            "Select supplier",
            supplier_options
        )

    with col3:

        category_options = ["All Categories"] + [
            row[0] for row in categories
        ]

        selected_category = st.selectbox(
            "Select procurement category",
            category_options
        )

    # Make sure the user has selected both dates

    if len(selected_dates) != 2:

        st.warning("Please select both a start date and an end date.")
        st.stop()

    start_date = selected_dates[0]
    end_date = selected_dates[1]

    if start_date > end_date:

        st.warning("Start date cannot be after end date.")
        st.stop()

    # ==================================================
    # KPI CARDS
    # ==================================================

    st.subheader("Spending Overview")

    metrics = get_spend_metrics(
        start_date,
        end_date,
        selected_supplier,
        selected_category
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Net Spend",
            f"${metrics[0] / 1_000_000_000:.2f}B"
        )

    with col2:
        st.metric(
            "Unique Suppliers",
            f"{metrics[1]:,}"
        )

    with col3:
        st.metric(
            "Total Awards",
            f"{metrics[2]:,}"
        )

    with col4:
        st.metric(
            "Total Transactions",
            f"{metrics[3]:,}"
        )

        # ==================================================
    # MONTHLY SPENDING CHART
    # ==================================================

    st.subheader("Monthly Net Spending")

    monthly_data = get_monthly_spending(
        start_date,
        end_date,
        selected_supplier,
        selected_category
    )

    if monthly_data:

        # Prepare data for the monthly spending chart

        months = [
            row[0].strftime("%b %Y")
            for row in monthly_data
        ]

        spending = [
            float(row[1]) / 1_000_000
            for row in monthly_data
        ]

        chart_data = pd.DataFrame({
            "Month": months,
            "Net Spending (USD Millions)": spending
        })

        # Create monthly spending line chart

        fig = px.line(
            chart_data,
            x="Month",
            y="Net Spending (USD Millions)",
            markers=True,
            category_orders={"Month": months},
            labels={
                "Month": "Month",
                "Net Spending (USD Millions)": "Net Spending (USD Millions)"
            }
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Net Spending: $%{y:,.2f}M"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            height=450,
            showlegend=False,
            xaxis_title="Month",
            yaxis_title="Net Spending (USD Millions)",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ==================================================
        # MONTHLY SPENDING INSIGHTS
        # ==================================================

        highest_month = max(
            monthly_data,
            key=lambda row: row[1]
        )

        lowest_month = min(
            monthly_data,
            key=lambda row: row[1]
        )

        highest_spend = float(highest_month[1])
        lowest_spend = float(lowest_month[1])

        # Calculate percentage difference

        percentage_difference = (
            ((highest_spend - lowest_spend) / lowest_spend) * 100
            if lowest_spend > 0 else None
        )

        # Display monthly spending insights

        st.subheader("Monthly Spending Insights")

        insight_col1, insight_col2, insight_col3 = st.columns(3)

        with insight_col1:

            st.metric(
                "Highest Spending Month",
                highest_month[0].strftime("%B %Y")
            )

            st.caption(
                f"Net spend: ${highest_spend / 1_000_000:,.2f}M"
            )

        with insight_col2:

            st.metric(
                "Lowest Spending Month",
                lowest_month[0].strftime("%B %Y")
            )

            st.caption(
                f"Net spend: ${lowest_spend / 1_000_000:,.2f}M"
            )

        with insight_col3:

            if percentage_difference is not None:

                st.metric(
                    "Highest vs. Lowest",
                    f"{percentage_difference:,.1f}%"
                )

            else:

                st.metric(
                    "Highest vs. Lowest",
                    "Not available"
                )

    else:

        st.info("No monthly spending data for these filters.")

    # ==================================================
    # TOP 10 SUPPLIERS CHART
    # ==================================================

    st.subheader("Top 10 Suppliers by Net Spending")

    supplier_data = get_top_suppliers(
        start_date,
        end_date,
        selected_supplier,
        selected_category
    )

    if supplier_data:

        supplier_names = [
            row[0] for row in supplier_data
        ]

        supplier_spending = [
            float(row[1]) / 1_000_000
            for row in supplier_data
        ]

        supplier_names.reverse()
        supplier_spending.reverse()

        fig = px.bar(
            x=supplier_spending,
            y=supplier_names,
            orientation="h",
            labels={
                "x": "Net Spending (USD Millions)",
                "y": "Supplier"
            }
        )

        fig.update_layout(
            yaxis_title="",
            xaxis_title="Net Spending (USD Millions)",
            showlegend=False,
            height=550
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No supplier data for these filters.")
    # ==================================================
    # TOP 10 PROCUREMENT CATEGORIES CHART
    # ==================================================

    st.subheader("Top 10 Procurement Categories by Net Spending")

    category_data = get_top_categories(
        start_date,
        end_date,
        selected_supplier,
        selected_category
    )

    if category_data:

        category_codes = [
            row[0] for row in category_data
        ]

        category_descriptions = [
            row[1] for row in category_data
        ]

        category_spending = [
            float(row[2]) / 1_000_000
            for row in category_data
        ]

        fig = px.bar(
            x=category_spending,
            y=category_codes,
            orientation="h",
            custom_data=[category_descriptions],
            labels={
                "x": "Net Spending (USD Millions)",
                "y": "PSC Code"
            }
        )

        fig.update_traces(
            hovertemplate=(
                "<b>PSC Code:</b> %{y}<br>"
                "<b>Description:</b> %{customdata[0]}<br>"
                "<b>Net Spending:</b> $%{x:,.2f} Million"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            yaxis_title="PSC Code",
            xaxis_title="Net Spending (USD Millions)",
            showlegend=False,
            height=550,
            yaxis=dict(autorange="reversed")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No category data for these filters.")

    # ==================================================
    # SPEND BREAKDOWN BY PROCUREMENT CATEGORY
    # ==================================================

    st.subheader("Spend Breakdown by Procurement Category")

    breakdown_data = get_category_breakdown(
        start_date,
        end_date,
        selected_supplier,
        selected_category
    )

    if breakdown_data:

        breakdown_codes = [
            f"{row[0]} - {row[1]}"
            for row in breakdown_data
        ]

        breakdown_spending = [
            float(row[2]) / 1_000_000
            for row in breakdown_data
        ]

        fig = px.pie(
            names=breakdown_codes,
            values=breakdown_spending,
            hole=0.5,
            title="Top 10 Categories — Share of Net Spend"
        )

        fig.update_traces(
            textinfo="percent",
            hovertemplate=(
                "<b>PSC Category:</b> %{label}<br>"
                "<b>Net Spending:</b> $%{value:,.2f} Million<br>"
                "<b>Share:</b> %{percent}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No spend breakdown data for these filters.")

except Exception as error:

    st.error(f"Unable to load dashboard data: {error}")

# --------------------------------------------------
# TRANSACTION DETAILS
# --------------------------------------------------

st.subheader("Transaction Details")

transaction_data = get_transaction_details(
    start_date,
    end_date,
    selected_supplier,
    selected_category
)

transaction_df = pd.DataFrame(
    transaction_data,
    columns=[
        "Action Date",
        "Award ID",
        "Supplier",
        "PSC Code",
        "PSC Description",
        "Net Obligation (USD)"
    ]
)

st.caption("Showing up to 500 most recent transactions matching your selected filters.")

if transaction_df.empty:
    st.info("No transactions found for the selected filters.")
else:
    st.dataframe(
        transaction_df,
        use_container_width=True,
        hide_index=True
    )

csv_data = transaction_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Transactions as CSV",
    data=csv_data,
    file_name="spend_transactions.csv",
    mime="text/csv"
)
