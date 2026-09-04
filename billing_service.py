from db import get_connection
from billing import calculate_occupied_days, calculate_room_billing
from datetime import timedelta
import psycopg2

def get_previous_reading(room_id, current_reading_date):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            reading_date,
            reading_value
        FROM meter_readings
        WHERE room_id = %s
          AND reading_date < %s
        ORDER BY reading_date DESC
        LIMIT 1;
    """, (room_id, current_reading_date))

    reading = cursor.fetchone()

    cursor.close()
    connection.close()

    if reading is None:
        return None

    return reading

def get_room_details(room_id):
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
        WHERE room_id = %s;
    """, (room_id,))

    room = cursor.fetchone()

    cursor.close()
    connection.close()

    return room

def get_room_tenants(room_id, billing_start_date, billing_end_date):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            o.tenant_id,
            t.full_name,
            o.move_in_date,
            o.move_out_date
        FROM occupancy o
        JOIN tenants t
            ON o.tenant_id = t.tenant_id
        WHERE o.room_id = %s
          AND o.move_in_date <= %s
          AND (o.move_out_date IS NULL OR o.move_out_date >= %s)
        ORDER BY o.move_in_date;
    """, (room_id, billing_end_date, billing_start_date))

    tenants = cursor.fetchall()

    cursor.close()
    connection.close()

    return tenants

def calculate_room_tenant_days(
    tenants,
    billing_start_date,
    billing_end_date
):
    tenant_days = []

    for tenant in tenants:
        tenant_id = tenant[0]
        full_name = tenant[1]
        move_in_date = tenant[2]
        move_out_date = tenant[3]

        occupied_days = calculate_occupied_days(
            move_in_date,
            move_out_date,
            billing_start_date,
            billing_end_date
        )

        if occupied_days > 0:
            tenant_days.append({
                "tenant_id": tenant_id,
                "full_name": full_name,
                "occupied_days": occupied_days
            })

    return tenant_days

def calculate_room_billing_from_database(
    room_id,
    current_reading,
    billing_end_date
):
    room = get_room_details(room_id)

    if room is None:
        raise ValueError("Room not found.")

    # Check the latest meter reading before processing
    latest_reading = get_previous_reading(
        room_id,
        billing_end_date + timedelta(days=1)
    )

    if latest_reading is not None:
        latest_reading_date = latest_reading[0]

        if billing_end_date <= latest_reading_date:
            raise ValueError(
                f"Reading date must be after the latest meter reading "
                f"({latest_reading_date})."
            )

    previous_reading = get_previous_reading(
        room_id,
        billing_end_date
    )

    if previous_reading is None:
        raise ValueError(
            "No previous meter reading found for this room."
        )

    billing_start_date = previous_reading[0] + timedelta(days=1)

    tenants = get_room_tenants(
        room_id,
        billing_start_date,
        billing_end_date
    )

    tenant_days = calculate_room_tenant_days(
        tenants,
        billing_start_date,
        billing_end_date
    )

    if not tenant_days:
        raise ValueError(
            "No tenants found for this billing period."
        )

    occupied_days = [
        tenant["occupied_days"]
        for tenant in tenant_days
    ]

    billing_result = calculate_room_billing(
        previous_reading=float(previous_reading[1]),
        current_reading=float(current_reading),
        rate_per_unit=float(room[4]),
        tenant_occupied_days=occupied_days
    )

    total_tenant_days = billing_result["total_tenant_days"]

    tenant_bill_records = []

    for tenant, amount in zip(
            tenant_days,
            billing_result["tenant_bills"]
    ):
        tenant_bill_records.append({
            "tenant_id": tenant["tenant_id"],
            "full_name": tenant["full_name"],
            "occupied_days": tenant["occupied_days"],
            "total_tenant_days": total_tenant_days,
            "amount": amount
        })

    return {
        "room_id": room[0],
        "room_number": room[1],
        "room_type": room[3],
        "rate_per_unit": room[4],
        "previous_reading_date": previous_reading[0],
        "previous_reading": previous_reading[1],
        "current_reading": current_reading,
        "billing_start_date": billing_start_date,
        "billing_end_date": billing_end_date,
        "units_consumed": billing_result["units_consumed"],
        "total_room_bill": billing_result["total_room_bill"],
        "tenant_days": tenant_days,
        "tenant_bills": tenant_bill_records
    }

def save_billing_cycle(
    connection,
    room_id,
    start_date,
    end_date,
    previous_reading,
    current_reading,
    units_consumed,
    rate_per_unit,
    total_bill
):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO billing_cycles (
            room_id,
            start_date,
            end_date,
            previous_reading,
            current_reading,
            units_consumed,
            rate_per_unit,
            total_bill
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING cycle_id;
    """, (
        room_id,
        start_date,
        end_date,
        previous_reading,
        current_reading,
        units_consumed,
        rate_per_unit,
        total_bill
    ))

    cycle_id = cursor.fetchone()[0]

    cursor.close()

    return cycle_id

def save_tenant_bills(connection, cycle_id, tenant_bills):
    cursor = connection.cursor()

    for bill in tenant_bills:
        cursor.execute("""
            INSERT INTO tenant_bills (
                cycle_id,
                tenant_id,
                occupied_days,
                tenant_days_total,
                amount
            )
            VALUES (%s, %s, %s, %s, %s);
        """, (
            cycle_id,
            bill["tenant_id"],
            bill["occupied_days"],
            bill["total_tenant_days"],
            bill["amount"]
        ))

    cursor.close()

def save_complete_billing(billing_result):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # 1. Save meter reading
        cursor.execute("""
            INSERT INTO meter_readings (
                room_id,
                reading_date,
                reading_value
            )
            VALUES (%s, %s, %s);
        """, (
            billing_result["room_id"],
            billing_result["billing_end_date"],
            billing_result["current_reading"]
        ))

        # 2. Save billing cycle
        cursor.execute("""
            INSERT INTO billing_cycles (
                room_id,
                start_date,
                end_date,
                previous_reading,
                current_reading,
                units_consumed,
                rate_per_unit,
                total_bill
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING cycle_id;
        """, (
            billing_result["room_id"],
            billing_result["billing_start_date"],
            billing_result["billing_end_date"],
            billing_result["previous_reading"],
            billing_result["current_reading"],
            billing_result["units_consumed"],
            billing_result["rate_per_unit"],
            billing_result["total_room_bill"]
        ))

        cycle_id = cursor.fetchone()[0]

        # 3. Save tenant bills
        for bill in billing_result["tenant_bills"]:

            cursor.execute("""
                INSERT INTO tenant_bills (
                    cycle_id,
                    tenant_id,
                    occupied_days,
                    tenant_days_total,
                    amount
                )
                VALUES (%s, %s, %s, %s, %s);
            """, (
                cycle_id,
                bill["tenant_id"],
                bill["occupied_days"],
                bill["total_tenant_days"],
                bill["amount"]
            ))

        # 4. Commit everything together
        connection.commit()

        return cycle_id

    except psycopg2.errors.UniqueViolation:

        connection.rollback()

        raise ValueError(
            "A meter reading or billing cycle already exists "
            "for this room and period."
        )

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()

from datetime import date

try:
    result = calculate_room_billing_from_database(
        room_id=3,
        current_reading=599,
        billing_end_date=date(2026, 7, 21)
    )

    print(result)

except ValueError as error:
    print("Billing Error:", error)