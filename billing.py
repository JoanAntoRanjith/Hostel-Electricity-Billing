def calculate_units(previous_reading, current_reading):
    if current_reading < previous_reading:
        raise ValueError("Current reading cannot be less than previous reading.")

    return current_reading - previous_reading

def calculate_room_bill(units_consumed, rate_per_unit):
    if units_consumed < 0:
        raise ValueError("Units consumed cannot be negative.")

    if rate_per_unit < 0:
        raise ValueError("Rate per unit cannot be negative.")

    return units_consumed * rate_per_unit

from datetime import date


def calculate_occupied_days(
    move_in_date,
    move_out_date,
    billing_start_date,
    billing_end_date
):
    effective_start = max(move_in_date, billing_start_date)

    if move_out_date is None:
        effective_end = billing_end_date
    else:
        effective_end = min(move_out_date, billing_end_date)

    if effective_start > effective_end:
        return 0

    return (effective_end - effective_start).days + 1

def calculate_total_tenant_days(occupied_days):
    if any(days < 0 for days in occupied_days):
        raise ValueError("Occupied days cannot be negative.")

    total_tenant_days = sum(occupied_days)

    if total_tenant_days == 0:
        raise ValueError("Total tenant-days cannot be zero.")

    return total_tenant_days

def calculate_tenant_bill(
    total_room_bill,
    tenant_occupied_days,
    total_tenant_days
):
    if total_room_bill < 0:
        raise ValueError("Total room bill cannot be negative.")

    if tenant_occupied_days < 0:
        raise ValueError("Tenant occupied days cannot be negative.")

    if total_tenant_days <= 0:
        raise ValueError("Total tenant-days must be greater than zero.")

    if tenant_occupied_days > total_tenant_days:
        raise ValueError(
            "Tenant occupied days cannot exceed total tenant-days."
        )

    return round(
        total_room_bill * tenant_occupied_days / total_tenant_days,
        2
    )

def calculate_room_billing(
    previous_reading,
    current_reading,
    rate_per_unit,
    tenant_occupied_days
):
    units_consumed = calculate_units(
        previous_reading,
        current_reading
    )

    total_room_bill = calculate_room_bill(
        units_consumed,
        rate_per_unit
    )

    total_tenant_days = calculate_total_tenant_days(
        tenant_occupied_days
    )

    tenant_bills = []

    for occupied_days in tenant_occupied_days:
        amount = calculate_tenant_bill(
            total_room_bill,
            occupied_days,
            total_tenant_days
        )

        tenant_bills.append(amount)

    return {
        "units_consumed": units_consumed,
        "total_room_bill": total_room_bill,
        "total_tenant_days": total_tenant_days,
        "tenant_bills": tenant_bills
    }

