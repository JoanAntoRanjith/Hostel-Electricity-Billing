from db import get_connection
import pandas as pd

def get_rooms():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            room_id,
            room_number,
            capacity,
            room_type,
            rate_per_unit
        FROM rooms
        ORDER BY room_number;
    """)

    rooms = cursor.fetchall()

    columns = [
        "room_id",
        "room_number",
        "capacity",
        "room_type",
        "rate_per_unit"
    ]

    rooms = pd.DataFrame(rooms, columns=columns)

    cursor.close()
    connection.close()

    return rooms

rooms = get_rooms()

'''get_tenants() function'''

def get_tenants():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            tenant_id,
            full_name,
            phone,
            telegram_chat_id,
            status
        FROM tenants
        ORDER BY full_name;
    """)

    tenants = cursor.fetchall()

    columns = [
        "tenant_id",
        "full_name",
        "phone",
        "telegram_chat_id",
        "status"
    ]

    tenants = pd.DataFrame(tenants, columns=columns)

    cursor.close()
    connection.close()

    return tenants



'''get_occupancy() function'''

def get_occupancy():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            o.occupancy_id,
            o.tenant_id,
            t.full_name,
            o.room_id,
            r.room_number,
            o.move_in_date,
            o.move_out_date
        FROM occupancy o
        JOIN tenants t
            ON o.tenant_id = t.tenant_id
        JOIN rooms r
            ON o.room_id = r.room_id
        ORDER BY r.room_number, o.move_in_date;
    """)

    occupancy = cursor.fetchall()

    columns = [
        "occupancy_id",
        "tenant_id",
        "full_name",
        "room_id",
        "room_number",
        "move_in_date",
        "move_out_date"
    ]

    occupancy = pd.DataFrame(occupancy, columns=columns)

    cursor.close()
    connection.close()

    return occupancy

def get_billing_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            bc.cycle_id,
            r.room_number,
            bc.start_date,
            bc.end_date,
            bc.previous_reading,
            bc.current_reading,
            bc.units_consumed,
            bc.rate_per_unit,
            bc.total_bill,
            COUNT(tb.bill_id) AS tenant_count
        FROM billing_cycles bc
        JOIN rooms r
            ON bc.room_id = r.room_id
        LEFT JOIN tenant_bills tb
            ON bc.cycle_id = tb.cycle_id
        GROUP BY
            bc.cycle_id,
            r.room_number,
            bc.start_date,
            bc.end_date,
            bc.previous_reading,
            bc.current_reading,
            bc.units_consumed,
            bc.rate_per_unit,
            bc.total_bill
        ORDER BY
            bc.end_date DESC,
            r.room_number;
    """)

    billing_history = cursor.fetchall()

    columns = [
        "cycle_id",
        "room_number",
        "start_date",
        "end_date",
        "previous_reading",
        "current_reading",
        "units_consumed",
        "rate_per_unit",
        "total_bill",
        "tenant_count"
    ]

    billing_history = pd.DataFrame(
        billing_history,
        columns=columns
    )

    cursor.close()
    connection.close()

    return billing_history