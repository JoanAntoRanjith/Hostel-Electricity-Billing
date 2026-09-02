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

print(rooms)
print()
print("Data type:", type(rooms))

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