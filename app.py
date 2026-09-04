import streamlit as st
import pandas as pd
from datetime import timedelta
from pathlib import Path

from database import (
    get_rooms,
    get_occupancy,
    get_billing_history,
    get_tenant_bills_by_cycle,
    update_payment_status,
    get_payment_summary,
    update_tenant_move_out
)

from meter_service import (
    get_previous_reading,
    get_latest_reading
)

from billing import (
    calculate_units,
    calculate_room_bill
)

from billing_service import (
    calculate_room_billing_from_database,
    save_complete_billing
)


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Beds & Dreams Men's Hostel Electricity Billing",
    page_icon="⚡",
    layout="wide"
)

# --------------------------------------------------
# Hostel Logo
# --------------------------------------------------

logo_path = Path("assets/sigma_logo.png")

if logo_path.exists():

    st.image(
        str(logo_path),
        width=180
    )

# --------------------------------------------------
# Page Title
# --------------------------------------------------

st.title("⚡ Beds & Dreams Men's Hostel Electricity Billing")

st.write(
    "Welcome to the Beds & Dreams | SIGMA Men's Hostel Electricity Billing System."
)


# --------------------------------------------------
# Dashboard Summary
# --------------------------------------------------

payment_summary = get_payment_summary()

st.subheader("📊 Billing Dashboard")

# --------------------------------------------------
# Dashboard Cards
# --------------------------------------------------

st.markdown(
    """
    <style>

    .dashboard-card {
        background: #FFFDF7;
        border: 1px solid #D6B15A;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 10px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
        min-height: 125px;
    }

    .dashboard-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }

    .dashboard-title {
        color: #0B243B;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .dashboard-value {
        color: #0B243B;
        font-size: 25px;
        font-weight: 700;
    }

    .dashboard-subtitle {
        color: #8A6A20;
        font-size: 12px;
        margin-top: 4px;
    }
     
    .stApp {
    background-color: #F7F3E8;
    }

    .main .block-container {
    background-color: #F7F3E8;
    padding-top: 2rem;
    padding-bottom: 3rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.html(
        f"""
        <div class="dashboard-card">
            <div class="dashboard-icon">⚡</div>
            <div class="dashboard-title">Billing Cycles</div>
            <div class="dashboard-value">
                {payment_summary["billing_cycles"]}
            </div>
            <div class="dashboard-subtitle">
                Completed billing periods
            </div>
        </div>
        """
    )


with col2:

    st.html(
        f"""
        <div class="dashboard-card">
            <div class="dashboard-icon">💰</div>
            <div class="dashboard-title">Total Billed</div>
            <div class="dashboard-value">
                ₹{float(payment_summary["total_billed"]):,.2f}
            </div>
            <div class="dashboard-subtitle">
                Total electricity billing
            </div>
        </div>
        """
    )


with col3:

    st.html(
        f"""
        <div class="dashboard-card">
            <div class="dashboard-icon">✅</div>
            <div class="dashboard-title">Total Paid</div>
            <div class="dashboard-value">
                ₹{float(payment_summary["total_paid"]):,.2f}
            </div>
            <div class="dashboard-subtitle">
                Amount collected
            </div>
        </div>
        """
    )


with col4:

    st.html(
        f"""
        <div class="dashboard-card">
            <div class="dashboard-icon">⏳</div>
            <div class="dashboard-title">Total Pending</div>
            <div class="dashboard-value">
                ₹{float(payment_summary["total_pending"]):,.2f}
            </div>
            <div class="dashboard-subtitle">
                Amount yet to collect
            </div>
        </div>
        """
    )


# --------------------------------------------------
# Collection Rate
# --------------------------------------------------

collection_rate = float(
    payment_summary["collection_rate"]
)

st.html(
    f"""
    <div class="dashboard-card"
         style="text-align: center; margin-top: 8px;">

        <div class="dashboard-icon">📈</div>

        <div class="dashboard-title">
            Overall Collection Rate
        </div>

        <div class="dashboard-value">
            {collection_rate:.1f}%
        </div>

        <div class="dashboard-subtitle">
            Paid amount ÷ total billed amount
        </div>

    </div>
    """
)

# --------------------------------------------------
# Load Rooms
# --------------------------------------------------

rooms = get_rooms()


# --------------------------------------------------
# Display Rooms
# --------------------------------------------------

st.subheader("Rooms")

st.dataframe(
    rooms,
    width="stretch"
)


# --------------------------------------------------
# Meter Reading Entry
# --------------------------------------------------

st.subheader("Enter Meter Reading")

room_options = rooms[
    "room_number"
].tolist()

selected_room_number = st.selectbox(
    "Select Room",
    room_options
)

selected_room = rooms[
    rooms["room_number"] == selected_room_number
].iloc[0]

room_id = int(
    selected_room["room_id"]
)

rate_per_unit = float(
    selected_room["rate_per_unit"]
)


# --------------------------------------------------
# Determine Reading Date
# --------------------------------------------------

latest_reading = get_latest_reading(
    room_id
)

if latest_reading is not None:

    latest_reading_date = latest_reading[0]

    minimum_date = (
        latest_reading_date
        + timedelta(days=1)
    )

    reading_date = st.date_input(
        "Reading Date",
        min_value=minimum_date,
        value=minimum_date
    )

else:

    reading_date = st.date_input(
        "Reading Date"
    )


# --------------------------------------------------
# Room Information
# --------------------------------------------------

st.caption(
    f"Room Type: {selected_room['room_type']}  |  "
    f"Capacity: {int(selected_room['capacity'])}  |  "
    f"Rate: ₹{rate_per_unit:.2f}/unit"
)


# --------------------------------------------------
# Previous Meter Reading
# --------------------------------------------------

previous_reading = get_previous_reading(
    room_id,
    reading_date
)

if previous_reading is not None:

    st.info(
        f"Previous Meter Reading: "
        f"{float(previous_reading):.2f} units"
    )

else:

    st.warning(
        "No previous meter reading found for this room."
    )


# --------------------------------------------------
# Electricity Rate
# --------------------------------------------------

st.info(
    f"Electricity Rate: ₹{rate_per_unit:.2f} per unit"
)


# --------------------------------------------------
# Current Meter Reading
# --------------------------------------------------

if previous_reading is not None:

    reading_value = st.number_input(
        "Current Meter Reading",
        min_value=float(previous_reading),
        value=float(previous_reading),
        step=1.0
    )

else:

    reading_value = st.number_input(
        "Current Meter Reading",
        min_value=0.0,
        value=0.0,
        step=1.0
    )


# --------------------------------------------------
# Estimated Room Bill
# --------------------------------------------------

if previous_reading is not None:

    units_consumed = calculate_units(
        float(previous_reading),
        reading_value
    )

    estimated_bill = calculate_room_bill(
        units_consumed,
        rate_per_unit
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Units Consumed",
        f"{units_consumed:.0f} units"
    )

    col2.metric(
        "Estimated Room Bill",
        f"₹{estimated_bill:,.2f}"
    )


# --------------------------------------------------
# Preview Billing
# --------------------------------------------------

if st.button("Preview Billing"):

    try:

        billing_preview = calculate_room_billing_from_database(
            room_id=room_id,
            current_reading=reading_value,
            billing_end_date=reading_date
        )

        # Store preview so it survives Streamlit reruns
        st.session_state["billing_preview"] = billing_preview

        # Store the room and reading information used
        # for this preview
        st.session_state["preview_room_id"] = room_id
        st.session_state["preview_reading_date"] = reading_date

    except ValueError as error:

        st.error(str(error))

    except Exception as error:

        st.error(
            f"Unexpected error: {error}"
        )


# --------------------------------------------------
# Display Stored Billing Preview
# --------------------------------------------------

if "billing_preview" in st.session_state:

    billing_preview = st.session_state[
        "billing_preview"
    ]

    st.divider()

    st.subheader(
        f"Billing Preview — Room "
        f"{billing_preview['room_number']}"
    )

    # ----------------------------------------------
    # Billing Period
    # ----------------------------------------------

    st.write(
        f"**Billing Period:** "
        f"{billing_preview['billing_start_date']} "
        f"to "
        f"{billing_preview['billing_end_date']}"
    )

    # ----------------------------------------------
    # Summary Metrics
    # ----------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Previous Reading",
        f"{float(billing_preview['previous_reading']):.0f}"
    )

    col2.metric(
        "Current Reading",
        f"{float(billing_preview['current_reading']):.0f}"
    )

    col3.metric(
        "Units Consumed",
        f"{float(billing_preview['units_consumed']):.0f}"
    )

    col4.metric(
        "Rate / Unit",
        f"₹{float(billing_preview['rate_per_unit']):,.2f}"
    )

    st.metric(
        "Total Room Bill",
        f"₹{float(billing_preview['total_room_bill']):,.2f}"
    )

    # ----------------------------------------------
    # Tenant Bill Allocation
    # ----------------------------------------------

    st.subheader("Tenant Bill Allocation")

    tenant_rows = []

    for tenant in billing_preview["tenant_bills"]:

        tenant_rows.append({
            "Tenant": tenant["full_name"],
            "Occupied Days": tenant["occupied_days"],
            "Amount (₹)": float(tenant["amount"])
        })

    tenant_df = pd.DataFrame(
        tenant_rows
    )

    st.dataframe(
        tenant_df,
        width="stretch",
        hide_index=True
    )

    # ----------------------------------------------
    # Reconciliation Check
    # ----------------------------------------------

    tenant_total = sum(
        float(tenant["amount"])
        for tenant in billing_preview["tenant_bills"]
    )

    room_total = float(
        billing_preview["total_room_bill"]
    )

    if abs(tenant_total - room_total) < 0.01:

        st.success(
            f"Bill allocation verified: "
            f"₹{tenant_total:,.2f}"
        )

        # ------------------------------------------
        # Finalize Billing
        # ------------------------------------------

        if st.button("Finalize Billing"):

            try:

                cycle_id = save_complete_billing(
                    billing_preview
                )

                st.success(
                    f"Billing finalized successfully. "
                    f"Cycle ID: {cycle_id}"
                )

                # Clear preview after successful save
                del st.session_state[
                    "billing_preview"
                ]

                if "preview_room_id" in st.session_state:
                    del st.session_state[
                        "preview_room_id"
                    ]

                if "preview_reading_date" in st.session_state:
                    del st.session_state[
                        "preview_reading_date"
                    ]

            except ValueError as error:

                st.error(
                    str(error)
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )

    else:

        st.error(
            f"Billing mismatch! "
            f"Room bill = ₹{room_total:,.2f}, "
            f"Tenant bills = ₹{tenant_total:,.2f}"
        )


# --------------------------------------------------
# Tenant Management
# --------------------------------------------------

st.divider()

st.subheader("👤 Tenant Management")

occupancy = get_occupancy()

if occupancy.empty:

    st.info(
        "No tenant occupancy records found."
    )

else:

    active_tenants = occupancy[
        occupancy["move_out_date"].isna()
    ].copy()

    if active_tenants.empty:

        st.info(
            "No active tenants found."
        )

    else:

        tenant_options = active_tenants[
            "tenant_id"
        ].tolist()

        selected_tenant_id = st.selectbox(
            "Select Tenant",
            tenant_options,
            format_func=lambda tenant_id:
                active_tenants.loc[
                    active_tenants["tenant_id"] == tenant_id,
                    "full_name"
                ].iloc[0]
        )

        selected_tenant = active_tenants[
            active_tenants["tenant_id"] == selected_tenant_id
        ].iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.write(
            f"**Room:** {selected_tenant['room_number']}"
        )

        col2.write(
            f"**Move-in Date:** "
            f"{selected_tenant['move_in_date']}"
        )

        col3.write(
            "**Status:** Active"
        )

        move_out_date = st.date_input(
            "Move-out Date"
        )

        if st.button("Record Move-Out"):

            try:

                update_tenant_move_out(
                    tenant_id=selected_tenant_id,
                    move_out_date=move_out_date
                )

                st.success(
                    "Tenant move-out recorded successfully."
                )

                st.rerun()

            except ValueError as error:

                st.error(
                    str(error)
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# --------------------------------------------------
# Billing History
# --------------------------------------------------

st.divider()

st.subheader("📋 Billing History")

billing_history = get_billing_history()

if billing_history.empty:

    st.info(
        "No finalized billing records found."
    )

else:

    # ----------------------------------------------
    # Room Filter
    # ----------------------------------------------

    room_filter_options = ["All Rooms"] + sorted(
        billing_history["room_number"].unique().tolist()
    )

    selected_history_room = st.selectbox(
        "Filter by Room",
        room_filter_options
    )

    if selected_history_room != "All Rooms":

        filtered_history = billing_history[
            billing_history["room_number"]
            == selected_history_room
        ].copy()

    else:

        filtered_history = billing_history.copy()

    # ----------------------------------------------
    # Prepare Display Data
    # ----------------------------------------------

    display_history = filtered_history.copy()

    display_history["Billing Period"] = (
        display_history["start_date"].astype(str)
        + " → "
        + display_history["end_date"].astype(str)
    )

    display_history["Rate / Unit"] = (
        display_history["rate_per_unit"]
        .apply(lambda x: f"₹{float(x):,.2f}")
    )

    display_history["Total Bill"] = (
        display_history["total_bill"]
        .apply(lambda x: f"₹{float(x):,.2f}")
    )

    display_history = display_history[
        [
            "cycle_id",
            "room_number",
            "Billing Period",
            "previous_reading",
            "current_reading",
            "units_consumed",
            "Rate / Unit",
            "Total Bill",
            "tenant_count"
        ]
    ]

    display_history.columns = [
        "Cycle ID",
        "Room",
        "Billing Period",
        "Previous Reading",
        "Current Reading",
        "Units",
        "Rate / Unit",
        "Total Bill",
        "Tenants"
    ]

    st.dataframe(
        display_history,
        width="stretch",
        hide_index=True
    )

    # ----------------------------------------------
    # Billing Cycle Details
    # ----------------------------------------------

    st.subheader("🔍 Billing Cycle Details")

    cycle_options = filtered_history[
        "cycle_id"
    ].tolist()

    selected_cycle_id = st.selectbox(
        "Select Billing Cycle",
        cycle_options
    )

    tenant_bills = get_tenant_bills_by_cycle(
        selected_cycle_id
    )

    # ----------------------------------------------
    # Payment Summary
    # ----------------------------------------------

    if not tenant_bills.empty:

        total_bill = tenant_bills["amount"].sum()

        paid_bill = tenant_bills.loc[
            tenant_bills["payment_status"] == "Paid",
            "amount"
        ].sum()

        pending_bill = tenant_bills.loc[
            tenant_bills["payment_status"] == "Pending",
            "amount"
        ].sum()

        if total_bill > 0:

            collection_rate = (
                paid_bill / total_bill
            ) * 100

        else:

            collection_rate = 0

        st.subheader("💰 Payment Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Bill",
            f"₹{float(total_bill):,.2f}"
        )

        col2.metric(
            "Paid",
            f"₹{float(paid_bill):,.2f}"
        )

        col3.metric(
            "Pending",
            f"₹{float(pending_bill):,.2f}"
        )

        col4.metric(
            "Collection Rate",
            f"{float(collection_rate):.1f}%"
        )

    if tenant_bills.empty:

        st.info(
            "No tenant bills found for this billing cycle."
        )

    else:

        display_tenant_bills = tenant_bills.copy()

        display_tenant_bills["Amount"] = (
            display_tenant_bills["amount"]
            .apply(lambda x: f"₹{float(x):,.2f}")
        )

        display_tenant_bills = display_tenant_bills[
            [
                "bill_id",
                "full_name",
                "occupied_days",
                "tenant_days_total",
                "Amount",
                "payment_status"
            ]
        ]

        display_tenant_bills.columns = [
            "Bill ID",
            "Tenant",
            "Occupied Days",
            "Total Tenant Days",
            "Amount",
            "Payment Status"
        ]

        st.dataframe(
            display_tenant_bills,
            width="stretch",
            hide_index=True
        )

        # ------------------------------------------
        # Update Payment Status
        # ------------------------------------------

        st.subheader("💳 Update Payment Status")

        tenant_options = tenant_bills[
            "bill_id"
        ].tolist()

        selected_bill_id = st.selectbox(
            "Select Tenant Bill",
            tenant_options,
            format_func=lambda bill_id: (
                tenant_bills.loc[
                    tenant_bills["bill_id"] == bill_id,
                    "full_name"
                ].iloc[0]
            )
        )

        selected_status = st.selectbox(
            "Payment Status",
            [
                "Pending",
                "Paid"
            ]
        )

        if st.button("Update Payment Status"):

            try:

                update_payment_status(
                    bill_id=selected_bill_id,
                    payment_status=selected_status
                )

                st.success(
                    "Payment status updated successfully."
                )

                st.rerun()

            except ValueError as error:

                st.error(
                    str(error)
                )

            except Exception as error:

                st.error(
                    f"Unexpected error: {error}"
                )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    """
    <div style="text-align: center; color: gray; padding-top: 30px;">
        Created by <b>J A Ranjith</b>
    </div>
    """,
    unsafe_allow_html=True
)