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
# Sidebar Navigation
# --------------------------------------------------

with st.sidebar:

    st.markdown("## ⚡ SIGMA Men's PG")

    st.markdown("---")

    st.markdown("### 📌 Quick Navigation")

    st.markdown("""
    - 📊 Billing Dashboard
    - 🚪 Rooms Overview
    - ⚡ Meter Reading
    - 🧾 Billing Preview
    - 👤 Tenant Management
    - 📋 Billing History
    """)

    st.markdown("---")

    st.caption(
        "Beds & Dreams | SIGMA Men's Hostel"
    )
    st.markdown(
        """
        <div style="text-align: center; color: gray; padding-top: 30px;">
            Created by <b>J A Ranjith</b>
        </div>
        """,
        unsafe_allow_html=True
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
    
        .calculation-card {
        background: #FFFDF7;
        border: 1px solid #D6B15A;
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        min-height: 110px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }

    .calculation-title {
        color: #8A6A20;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .calculation-value {
        color: #0B243B;
        font-size: 26px;
        font-weight: 700;
    }
    
    .preview-card {
        background: #FFFDF7;
        border: 1px solid #D6B15A;
        border-radius: 14px;
        padding: 16px 18px;
        text-align: center;
        min-height: 105px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }

    .preview-title {
        color: #8A6A20;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .preview-value {
        color: #0B243B;
        font-size: 23px;
        font-weight: 700;
    }
    
    .reconciliation-card {
        background: #F3F8F3;
        border: 1px solid #9DB89D;
        border-radius: 14px;
        padding: 16px 20px;
        margin: 15px 0;
        text-align: center;
    }

    .reconciliation-title {
        color: #315C31;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .reconciliation-value {
        color: #234523;
        font-size: 22px;
        font-weight: 700;
    }
    
    .payment-card {
        background: #FFFDF7;
        border: 1px solid #D6B15A;
        border-radius: 14px;
        padding: 16px 18px;
        text-align: center;
        min-height: 105px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }

    .payment-title {
        color: #8A6A20;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .payment-value {
        color: #0B243B;
        font-size: 23px;
        font-weight: 700;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0B243B;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #D6B15A;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li {
        color: #FFFDF7;
    }

    [data-testid="stSidebar"] hr {
        border-color: #D6B15A;
    }
    
    .room-info-card {
        background: #FFFDF7;
        border: 1px solid #D6B15A;
        border-radius: 12px;
        padding: 12px 18px;
        margin: 8px 0 18px 0;
        color: #0B243B;
        font-size: 14px;
    }
    
    /* Section spacing */
    .stSubheader {
        margin-top: 28px;
        margin-bottom: 12px;
    }

    /* Divider spacing */
    hr {
        margin-top: 28px;
        margin-bottom: 28px;
    }
    
    .tenant-table {
        width: 100%;
        border-collapse: collapse;
        background: #FFFDF7;
        border: 1px solid #D6B15A;
        border-radius: 12px;
        overflow: hidden;
        margin-top: 10px;
    }

    .tenant-table th {
        background: #0B243B;
        color: #FFFDF7;
        padding: 12px 14px;
        text-align: left;
        font-size: 13px;
        font-weight: 600;
    }

    .tenant-table td {
        padding: 11px 14px;
        border-bottom: 1px solid #E8DFC9;
        color: #0B243B;
        font-size: 14px;
    }

    .tenant-table tr:last-child td {
        border-bottom: none;
    }

    .tenant-table tr:hover td {
        background: #F7F3E8;
    }

    .tenant-amount {
        color: #8A6A20;
        font-weight: 700;
        text-align: right;
    }

    .tenant-days {
     text-align: center;
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
# Rooms Overview
# --------------------------------------------------

st.subheader("🚪 Rooms Overview")

room_columns = st.columns(4)

for index, (_, room) in enumerate(rooms.iterrows()):

    with room_columns[index % 4]:

        room_type_icon = (
            "❄️" if room["room_type"] == "AC"
            else "🌀"
        )

        st.html(
            f"""
            <div class="dashboard-card"
                 style="min-height: 145px;">

                <div class="dashboard-title">
                    ROOM {int(room["room_number"])}
                </div>

                <div style="
                    color: #0B243B;
                    font-size: 14px;
                    margin-top: 8px;
                ">
                    {room_type_icon}
                    {room["room_type"]}
                </div>

                <div style="
                    color: #0B243B;
                    font-size: 13px;
                    margin-top: 6px;
                ">
                    👥 Capacity: {int(room["capacity"])}
                </div>

                <div style="
                    color: #8A6A20;
                    font-size: 13px;
                    font-weight: 600;
                    margin-top: 6px;
                ">
                    ⚡ ₹{float(room["rate_per_unit"]):,.2f} / unit
                </div>

            </div>
            """
        )


# --------------------------------------------------
# Meter Reading Entry
# --------------------------------------------------

st.subheader("⚡ Meter Reading Entry")

st.caption(
    "Enter the latest electricity meter reading for the selected room."
)
st.markdown(
    """
    <style>

    .meter-info-card {
        background: #FFFDF7;
        border: 1px solid #D6B15A;
        border-radius: 14px;
        padding: 16px 20px;
        margin: 10px 0 18px 0;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }

    .meter-label {
        color: #8A6A20;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .meter-value {
        color: #0B243B;
        font-size: 20px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)

room_options = rooms[
    "room_number"
].tolist()

# --------------------------------------------------
# Meter Reading Inputs
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    selected_room_number = st.selectbox(
        "🚪 Select Room",
        room_options
    )

with col2:

    # Get selected room details
    selected_room = rooms[
        rooms["room_number"] == selected_room_number
    ].iloc[0]

    room_id = int(
        selected_room["room_id"]
    )

    rate_per_unit = float(
        selected_room["rate_per_unit"]
    )

    # Determine minimum reading date
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
            "📅 Reading Date",
            min_value=minimum_date,
            value=minimum_date
        )

    else:

        reading_date = st.date_input(
            "📅 Reading Date"
        )


# --------------------------------------------------
# Room Information
# --------------------------------------------------

st.html(f"""
<div class="room-info-card">
    🚪 <b>Room {int(selected_room["room_number"])}</b>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    {"❄️" if selected_room["room_type"] == "AC" else "🌀"}
    <b>{selected_room["room_type"]}</b>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    👥 <b>Capacity:</b> {int(selected_room["capacity"])}
    &nbsp;&nbsp;|&nbsp;&nbsp;
    ⚡ <b>Rate:</b> ₹{rate_per_unit:.2f}/unit
</div>
""")


# --------------------------------------------------
# Previous Meter Reading
# --------------------------------------------------

previous_reading = get_previous_reading(
    room_id,
    reading_date
)

if previous_reading is not None:

    col1, col2 = st.columns(2)

    with col1:

        st.html(
            f"""
            <div class="meter-info-card">
                <div class="meter-label">
                    PREVIOUS METER READING
                </div>
                <div class="meter-value">
                    ⚡ {float(previous_reading):,.0f} units
                </div>
            </div>
            """
        )

    with col2:

        st.html(
            f"""
            <div class="meter-info-card">
                <div class="meter-label">
                    ELECTRICITY RATE
                </div>
                <div class="meter-value">
                    ₹{rate_per_unit:,.2f} / unit
                </div>
            </div>
            """
        )

else:

    st.warning(
        "No previous meter reading found for this room."
    )

# --------------------------------------------------
# Current Meter Reading
# --------------------------------------------------

if previous_reading is not None:

    reading_value = st.number_input(
        "⚡ Current Meter Reading",
        min_value=float(previous_reading),
        value=float(previous_reading),
        step=1.0
    )

else:

    reading_value = st.number_input(
        "⚡ Current Meter Reading",
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

    with col1:
        st.html(
            f"""
            <div class="calculation-card">

                <div class="calculation-title">
                    ⚡ UNITS CONSUMED
                </div>

                <div class="calculation-value">
                    {units_consumed:.0f} units
                </div>

            </div>
            """
        )

    with col2:
        st.html(
            f"""
            <div class="calculation-card">

                <div class="calculation-title">
                    💰 ESTIMATED ROOM BILL
                </div>

                <div class="calculation-value">
                    ₹{estimated_bill:,.2f}
                </div>

            </div>
            """
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
        f"🧾 Billing Preview — Room "
        f"{billing_preview['room_number']}"
    )

    st.caption(
        "Review meter consumption, billing amount, and tenant-wise allocation before finalizing."
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

    with col1:
        st.html(f"""
        <div class="preview-card">
            <div class="preview-title">
                PREVIOUS READING
            </div>
            <div class="preview-value">
                {float(billing_preview["previous_reading"]):,.0f}
            </div>
        </div>
        """)

    with col2:
        st.html(f"""
        <div class="preview-card">
            <div class="preview-title">
                CURRENT READING
            </div>
            <div class="preview-value">
                {float(billing_preview["current_reading"]):,.0f}
            </div>
        </div>
        """)

    with col3:
        st.html(f"""
        <div class="preview-card">
            <div class="preview-title">
                UNITS CONSUMED
            </div>
            <div class="preview-value">
                {float(billing_preview["units_consumed"]):,.0f}
            </div>
        </div>
        """)

    with col4:
        st.html(f"""
        <div class="preview-card">
            <div class="preview-title">
                RATE / UNIT
            </div>
            <div class="preview-value">
                ₹{float(billing_preview["rate_per_unit"]):,.2f}
            </div>
        </div>
        """)

    st.html(f"""
    <div class="preview-card" style="margin-top: 12px;">
        <div class="preview-title">
            TOTAL ROOM BILL
        </div>
        <div class="preview-value">
            ₹{float(billing_preview["total_room_bill"]):,.2f}
        </div>
    </div>
    """)

    # ----------------------------------------------
    # Tenant Bill Allocation
    # ----------------------------------------------

    st.subheader("👥 Tenant Bill Allocation")
    st.caption(
        "Electricity charges are allocated based on each tenant's occupied days."
    )

    tenant_rows = []

    for tenant in billing_preview["tenant_bills"]:

        tenant_rows.append({
            "Tenant": tenant["full_name"],
            "Occupied Days": tenant["occupied_days"],
            "Amount (₹)": float(tenant["amount"])
        })

    tenant_df = pd.DataFrame(tenant_rows)

    # --------------------------------------------------
    # Tenant Bill Allocation Table
    # --------------------------------------------------

    table_rows = ""

    for _, tenant in tenant_df.iterrows():
        table_rows += f"""
        <tr>
            <td>{tenant["Tenant"]}</td>
            <td class="tenant-days">
                {int(tenant["Occupied Days"])}
            </td>
            <td class="tenant-amount">
                ₹{float(tenant["Amount (₹)"]):,.2f}
            </td>
        </tr>
        """

    st.html(f"""
    <table class="tenant-table">

        <thead>
            <tr>
                <th>Tenant</th>
                <th>Occupied Days</th>
                <th style="text-align: right;">Amount (₹)</th>
            </tr>
        </thead>

        <tbody>
            {table_rows}
        </tbody>

    </table>
    """)

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

        st.html(f"""
        <div class="reconciliation-card">
            <div class="reconciliation-title">
                ✅ BILL ALLOCATION VERIFIED
            </div>
            <div class="reconciliation-value">
                ₹{tenant_total:,.2f}
            </div>
        </div>
        """)

        # ------------------------------------------
        # Finalize Billing
        # ------------------------------------------
        st.divider()

        st.subheader("✅ Finalize Billing")
        st.caption(
            "Review the billing details and tenant allocations above before finalizing."
        )

        if st.button("✅ Finalize Billing",
                     use_container_width=True
                     ):
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
st.caption(
    "Manage active tenants and record their move-out dates."
)

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

        with col1:
            st.info(
                f"🚪 **Room**\n\n"
                f"Room {selected_tenant['room_number']}"
            )

        with col2:
            st.info(
                f"📅 **Move-in Date**\n\n"
                f"{selected_tenant['move_in_date']}"
            )

        with col3:
            st.success(
                "🟢 **Status**\n\n"
                "Active"
            )

        move_out_date = st.date_input(
            "📅 Move-out Date",
            help="Select the date on which the tenant moved out."
        )

        if st.button(
                "🚪 Record Move-Out",
                use_container_width=True
        ):

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
st.caption(
    "Review finalized electricity billing cycles and room-wise billing records."
)

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
        hide_index=True,
        column_config={
            "Cycle ID": st.column_config.NumberColumn(
                "Cycle ID",
                format="%d"
            ),
            "Room": st.column_config.NumberColumn(
                "Room",
                format="Room %d"
            ),
            "Previous Reading": st.column_config.NumberColumn(
                "Previous Reading",
                format="%.0f"
            ),
            "Current Reading": st.column_config.NumberColumn(
                "Current Reading",
                format="%.0f"
            ),
            "Units": st.column_config.NumberColumn(
                "⚡ Units",
                format="%.0f"
            ),
            "Rate / Unit": st.column_config.TextColumn(
                "🏷️ Rate / Unit"
            ),
            "Total Bill": st.column_config.TextColumn(
                "💰 Total Bill"
            ),
            "Tenants": st.column_config.NumberColumn(
                "👥 Tenants",
                format="%d"
            )
        }
    )

    # ----------------------------------------------
    # Billing Cycle Details
    # ----------------------------------------------

    st.subheader("🔍 Billing Cycle Details")
    st.caption(
        "Select a billing cycle to view tenant charges and payment status."
    )

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
        st.caption(
            "Track billed, collected, and outstanding electricity payments."
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.html(f"""
            <div class="payment-card">
                <div class="payment-title">
                    💰 TOTAL BILL
                </div>
                <div class="payment-value">
                    ₹{float(total_bill):,.2f}
                </div>
            </div>
            """)

        with col2:
            st.html(f"""
            <div class="payment-card">
                <div class="payment-title">
                    ✅ PAID
                </div>
                <div class="payment-value">
                    ₹{float(paid_bill):,.2f}
                </div>
            </div>
            """)

        with col3:
            st.html(f"""
            <div class="payment-card">
                <div class="payment-title">
                    ⏳ PENDING
                </div>
                <div class="payment-value">
                    ₹{float(pending_bill):,.2f}
                </div>
            </div>
            """)

        with col4:
            st.html(f"""
            <div class="payment-card">
                <div class="payment-title">
                    📈 COLLECTION RATE
                </div>
                <div class="payment-value">
                    {float(collection_rate):.1f}%
                </div>
            </div>
            """)

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
        st.caption(
            "Mark an individual tenant bill as Pending or Paid."
        )

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

        if st.button(
                "💳 Update Payment Status",
                use_container_width=True
        ):

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

#end