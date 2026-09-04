import psycopg2

from db import get_connection


def get_previous_reading(room_id, reading_date):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT reading_value
        FROM meter_readings
        WHERE room_id = %s
          AND reading_date < %s
        ORDER BY reading_date DESC
        LIMIT 1;
    """, (room_id, reading_date))

    reading = cursor.fetchone()

    cursor.close()
    connection.close()

    if reading is None:
        return None

    return reading[0]


def save_meter_reading(room_id, reading_date, reading_value):

    if room_id is None:
        raise ValueError("Room ID is required.")

    if reading_date is None:
        raise ValueError("Reading date is required.")

    if reading_value is None:
        raise ValueError("Reading value is required.")

    if reading_value < 0:
        raise ValueError("Reading value cannot be negative.")

    previous_reading = get_previous_reading(
        room_id,
        reading_date
    )

    if previous_reading is not None and reading_value < previous_reading:
        raise ValueError(
            f"Current reading ({reading_value}) cannot be less than "
            f"previous reading ({previous_reading})."
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO meter_readings (
                room_id,
                reading_date,
                reading_value
            )
            VALUES (%s, %s, %s);
        """, (
            room_id,
            reading_date,
            reading_value
        ))

        connection.commit()

        cursor.close()

    except psycopg2.errors.UniqueViolation:
        connection.rollback()

        raise ValueError(
            "A meter reading already exists for this room and date."
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()