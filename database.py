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

def get_tenant_bills_by_cycle(cycle_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            tb.bill_id,
            tb.tenant_id,
            t.full_name,
            t.phone,
            tb.occupied_days,
            tb.tenant_days_total,
            tb.amount,
            tb.payment_status
        FROM tenant_bills tb
        JOIN tenants t
            ON tb.tenant_id = t.tenant_id
        WHERE tb.cycle_id = %s
        ORDER BY t.full_name;
    """, (cycle_id,))

    tenant_bills = cursor.fetchall()

    columns = [
        "bill_id",
        "tenant_id",
        "full_name",
        "phone",
        "occupied_days",
        "tenant_days_total",
        "amount",
        "payment_status"
    ]

    tenant_bills = pd.DataFrame(
        tenant_bills,
        columns=columns
    )

    cursor.close()
    connection.close()

    return tenant_bills

def update_payment_status(bill_id, payment_status):
    allowed_statuses = [
        "Pending",
        "Paid"
    ]

    if payment_status not in allowed_statuses:
        raise ValueError(
            "Invalid payment status."
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE tenant_bills
            SET payment_status = %s
            WHERE bill_id = %s;
        """, (
            payment_status,
            bill_id
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                "Tenant bill not found."
            )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()
        connection.close()

def get_payment_summary():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS billing_cycles,
            COALESCE(SUM(total_bill), 0) AS total_billed
        FROM billing_cycles;
    """)

    billing_summary = cursor.fetchone()

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN payment_status = 'Paid'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_paid,

            COALESCE(
                SUM(
                    CASE
                        WHEN payment_status = 'Pending'
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_pending

        FROM tenant_bills;
    """)

    payment_summary = cursor.fetchone()

    cursor.close()
    connection.close()

    billing_cycles = billing_summary[0]
    total_billed = billing_summary[1]

    total_paid = payment_summary[0]
    total_pending = payment_summary[1]

    if total_billed > 0:
        collection_rate = (
            total_paid / total_billed
        ) * 100
    else:
        collection_rate = 0

    return {
        "billing_cycles": billing_cycles,
        "total_billed": total_billed,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "collection_rate": collection_rate
    }

def update_tenant_move_out(tenant_id, move_out_date):
    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Update occupancy record
        cursor.execute("""
            UPDATE occupancy
            SET move_out_date = %s
            WHERE tenant_id = %s
              AND move_out_date IS NULL;
        """, (
            move_out_date,
            tenant_id
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                "Active occupancy record not found for this tenant."
            )

        # Update tenant status
        cursor.execute("""
            UPDATE tenants
            SET status = 'Inactive'
            WHERE tenant_id = %s;
        """, (
            tenant_id,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                "Tenant record not found."
            )

        # Commit both updates together
        connection.commit()

    except Exception:

        # Undo both changes if anything fails
        connection.rollback()
        raise

    finally:

        cursor.close()
        connection.close()