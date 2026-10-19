# Технические характеристики Tesla Roadster (второе поколение)
ROADSTER_SPECS = {
    "max_speed_kmh": 400,
    "acceleration_0_100": 1.9,
    "battery_capacity_kwh": 200,
    "range_km": 1000,
    "peak_power_kw": 745,
}

DRIVE_MODES = {
    "eco":    {"accel_mult": 0.5,  "consumption_mult": 0.8},
    "normal": {"accel_mult": 1.0,  "consumption_mult": 1.0},
    "sport":  {"accel_mult": 1.8,  "consumption_mult": 1.5},
}


def step_simulation(sim, throttle: float, brake: float, dt: float = 0.1):
    """
    throttle ∈ [0, 1], brake ∈ [0, 1].
    Возвращает словарь с новыми значениями.
    """
    mode = DRIVE_MODES.get(sim.drive_mode, DRIVE_MODES["normal"])
    max_speed = ROADSTER_SPECS["max_speed_kmh"]

    if throttle > 0:
        accel = mode["accel_mult"] * throttle * 30  # км/ч за секунду
        sim.speed_kmh = min(max_speed, sim.speed_kmh + accel * dt)
    elif brake > 0:
        decel = brake * 50
        sim.speed_kmh = max(0, sim.speed_kmh - decel * dt)
    else:
        sim.speed_kmh = max(0, sim.speed_kmh - 2 * dt)

    # Расход батареи
    distance = sim.speed_kmh / 3600 * dt
    sim.odometer_km += distance
    battery_per_km = 100 / ROADSTER_SPECS["range_km"]
    consumption = battery_per_km * mode["consumption_mult"] * distance
    sim.battery_percent = max(0, sim.battery_percent - consumption)

    # Климат жрёт батарею (упрощение)
    sim.battery_percent = max(0, sim.battery_percent - 0.001 * dt)

    # Запас хода
    range_km = (sim.battery_percent / 100) * ROADSTER_SPECS["range_km"]

    return {
        "speed_kmh": round(sim.speed_kmh, 1),
        "battery_percent": round(sim.battery_percent, 2),
        "range_km": round(range_km, 1),
        "odometer_km": round(sim.odometer_km, 2),
        "drive_mode": sim.drive_mode,
        "autopilot": sim.autopilot,
        "climate_temp": sim.climate_temp,
    }


def check_alerts(sim):
    alerts = []
    if sim.battery_percent < 10:
        alerts.append(("critical", "Батарея почти пуста! Найдите зарядку."))
    elif sim.battery_percent < 20:
        alerts.append(("warning", "Низкий заряд батареи — 20%."))
    if sim.speed_kmh > 250:
        alerts.append(("warning", "Высокая скорость — снизьте!"))
    return alerts