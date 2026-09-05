import psycopg2
from db import get_connection
from billing import (
    calculate_occupied_days,
    calculate_room_billing
)


def restore_historical_billing():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # --------------------------------------------------
        # Get all rooms
        # --------------------------------------------------

        cursor.execute("""
            SELECT
                room_id,
                room_number,
                rate_per_unit
            FROM rooms
            ORDER BY room_number;
        """)

        rooms = cursor.fetchall()

        for room_id, room_number, rate_per_unit in rooms:

            # --------------------------------------------------
            # Get May 7 and July 21 meter readings
            # --------------------------------------------------

            cursor.execute("""
                SELECT
                    reading_date,
                    reading_value
                FROM meter_readings
                WHERE room_id = %s
                  AND reading_date IN ('2026-05-07', '2026-07-21')
                ORDER BY reading_date;
            """, (room_id,))

            readings = cursor.fetchall()

            if len(readings) != 2:
                raise ValueError(
                    f"Expected 2 readings for Room {room_number}, "
                    f"found {len(readings)}."
                )

            previous_reading_date = readings[0][0]
            previous_reading = float(readings[0][1])

            current_reading = float(readings[1][1])
            billing_end_date = readings[1][0]

            billing_start_date = (
                previous_reading_date
            )

            # --------------------------------------------------
            # Billing period
            # --------------------------------------------------

            billing_start_date = (
                previous_reading_date
            )

            # Meter reading date itself belongs to the
            # previous period, so billing starts next day.
            from datetime import timedelta

            billing_start_date = (
                previous_reading_date
                + timedelta(days=1)
            )

            # --------------------------------------------------
            # Get tenants in this room
            # --------------------------------------------------

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
                  AND (
                      o.move_out_date IS NULL
                      OR o.move_out_date >= %s
                  )
                ORDER BY o.move_in_date;
            """, (
                room_id,
                billing_end_date,
                billing_start_date
            ))

            tenants = cursor.fetchall()

            tenant_occupied_days = []
            tenant_records = []

            for tenant_id, full_name, move_in_date, move_out_date in tenants:

                occupied_days = calculate_occupied_days(
                    move_in_date,
                    move_out_date,
                    billing_start_date,
                    billing_end_date
                )

                if occupied_days > 0:

                    tenant_occupied_days.append(
                        occupied_days
                    )

                    tenant_records.append({
                        "tenant_id": tenant_id,
                        "full_name": full_name,
                        "occupied_days": occupied_days
                    })

            # --------------------------------------------------
            # Calculate billing
            # --------------------------------------------------

            billing_result = calculate_room_billing(
                previous_reading=previous_reading,
                current_reading=current_reading,
                rate_per_unit=float(rate_per_unit),
                tenant_occupied_days=tenant_occupied_days
            )

            # --------------------------------------------------
            # Insert billing cycle
            # --------------------------------------------------

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
                billing_start_date,
                billing_end_date,
                previous_reading,
                current_reading,
                billing_result["units_consumed"],
                rate_per_unit,
                billing_result["total_room_bill"]
            ))

            cycle_id = cursor.fetchone()[0]

            # --------------------------------------------------
            # Insert tenant bills
            # --------------------------------------------------

            for tenant, amount in zip(
                tenant_records,
                billing_result["tenant_bills"]
            ):

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
                    tenant["tenant_id"],
                    tenant["occupied_days"],
                    billing_result["total_tenant_days"],
                    amount
                ))

            print(
                f"Room {room_number}: "
                f"₹{billing_result['total_room_bill']:,.2f} "
                f"restored successfully."
            )

        connection.commit()

        print()
        print("Historical billing restoration completed.")

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    restore_historical_billing()