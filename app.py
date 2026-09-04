import streamlit as st
import pandas as pd
from datetime import timedelta

from database import get_rooms

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
    page_title="Hostel Electricity Billing",
    page_icon="⚡",
    layout="wide"
)


# --------------------------------------------------
# Page Title
# --------------------------------------------------

st.title("⚡ Hostel Electricity Billing")

st.write(
    "Welcome to the Hostel Electricity Billing System."
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