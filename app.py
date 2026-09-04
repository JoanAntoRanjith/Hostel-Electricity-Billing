import streamlit as st
from datetime import timedelta

from database import get_rooms

from meter_service import (
    get_previous_reading,
    get_latest_reading,
    save_meter_reading
)

from billing import (
    calculate_units,
    calculate_room_bill
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
# Application Title
# --------------------------------------------------

st.title("⚡ Hostel Electricity Billing")

st.write(
    "Welcome to the Hostel Electricity Billing System."
)


# --------------------------------------------------
# Load Room Data
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


# --------------------------------------------------
# Get Selected Room Details
# --------------------------------------------------

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
# Get Latest Meter Reading
# --------------------------------------------------

latest_reading = get_latest_reading(
    room_id
)


# --------------------------------------------------
# Restrict Reading Date
# --------------------------------------------------

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
# Display Room Information
# --------------------------------------------------

st.caption(
    f"Room Type: {selected_room['room_type']}  |  "
    f"Capacity: {int(selected_room['capacity'])}  |  "
    f"Rate: ₹{rate_per_unit:.2f}/unit"
)


# --------------------------------------------------
# Get Previous Meter Reading
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
        "No previous meter reading found "
        "for this room."
    )


# --------------------------------------------------
# Display Electricity Rate
# --------------------------------------------------

st.info(
    f"Electricity Rate: "
    f"₹{rate_per_unit:.2f} per unit"
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
# Calculate Units & Estimated Bill
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

    st.metric(
        "Units Consumed",
        f"{units_consumed:.0f} units"
    )

    st.metric(
        "Estimated Room Bill",
        f"₹{estimated_bill:,.2f}"
    )


# --------------------------------------------------
# Save Meter Reading
# --------------------------------------------------

if st.button("Save Meter Reading"):

    try:

        save_meter_reading(
            room_id=room_id,
            reading_date=reading_date,
            reading_value=reading_value
        )

        st.success(
            f"Meter reading saved for "
            f"Room {selected_room_number}."
        )

    except ValueError as error:

        st.error(str(error))


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