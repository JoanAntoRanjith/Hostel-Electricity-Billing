import streamlit as st
from meter_service import get_previous_reading
from database import get_rooms


st.set_page_config(
    page_title="SIGMA Men's Hostel Electricity Billing",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ SIGMA Men's Hostel Electricity Billing")

st.write(
    "Welcome to the SIGMA Men's Hostel Electricity Billing System."
)

rooms = get_rooms()

st.subheader("Rooms")

st.dataframe(
    rooms,
    width="stretch"
)

st.subheader("Enter Meter Reading")

room_options = rooms["room_number"].tolist()

selected_room_number = st.selectbox(
    "Select Room",
    room_options
)

reading_date = st.date_input(
    "Reading Date"
)

selected_room = rooms[
    rooms["room_number"] == selected_room_number
].iloc[0]

room_id = int(selected_room["room_id"])

previous_reading = get_previous_reading(
    room_id,
    reading_date
)

if previous_reading is not None:
    st.info(
        f"Previous Meter Reading: {previous_reading} units"
    )
else:
    st.warning(
        "No previous meter reading found for this room."
    )

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

if previous_reading is not None:
    units_consumed = reading_value - float(previous_reading)

    if previous_reading is not None:
        units_consumed = reading_value - float(previous_reading)

        st.metric(
            "Units Consumed",
            f"{units_consumed:.0f} units"
        )
        
if st.button("Save Meter Reading"):

    selected_room = rooms[
        rooms["room_number"] == selected_room_number
    ].iloc[0]

    room_id = int(selected_room["room_id"])

    try:
        from meter_service import save_meter_reading

        save_meter_reading(
            room_id=room_id,
            reading_date=reading_date,
            reading_value=reading_value
        )

        st.success(
            f"Meter reading saved for Room {selected_room_number}."
        )

    except ValueError as error:
        st.error(str(error))

st.markdown(
    """
    <div style="text-align: center; color: gray; padding-top: 30px;">
        Created by <b>J A Ranjith</b>
    </div>
    """,
    unsafe_allow_html=True
)