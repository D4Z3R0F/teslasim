from flask import Blueprint, jsonify, request
from models import db, Simulation, Alert, Trip, User
from services.physics import step_simulation, check_alerts

sim_bp = Blueprint("simulations", __name__)

# Вспомогательная функция для красивого имени
def get_next_roadster_name():
    count = Simulation.query.count() + 1
    return f"Roadster {count}"


@sim_bp.route("/api/simulations", methods=["POST"])
def create_simulation():
    # В учебных целях берем первого пользователя из базы (или создаем тестового)
    user = User.query.first()
    if not user:
        user = User(username="demo_driver", email="demo@tesla.com", role="driver")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    sim = Simulation(user_id=user.id, name=get_next_roadster_name())
    db.session.add(sim)
    db.session.commit()
    
    return jsonify({"id": sim.id, "name": sim.name}), 201


@sim_bp.route("/api/simulations/<int:sim_id>", methods=["GET"])
def get_simulation(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    return jsonify({
        "id": sim.id,
        "speed_kmh": sim.speed_kmh,
        "battery_percent": sim.battery_percent,
        "odometer_km": sim.odometer_km,
        "drive_mode": sim.drive_mode,
        "autopilot": sim.autopilot,
        "climate_temp": sim.climate_temp,
        "is_running": sim.is_running,
    })


@sim_bp.route("/api/simulations/<int:sim_id>/tick", methods=["POST"])
def tick(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    if not sim.is_running:
        return jsonify({"error": "Симуляция не запущена"}), 400

    data = request.get_json() or {}
    throttle = float(data.get("throttle", 0))
    brake = float(data.get("brake", 0))

    state = step_simulation(sim, throttle, brake)

    for severity, msg in check_alerts(sim):
        db.session.add(Alert(simulation_id=sim.id, severity=severity, message=msg))

    db.session.commit()
    return jsonify(state), 200


@sim_bp.route("/api/simulations/<int:sim_id>/start", methods=["POST"])
def start(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    sim.is_running = True
    trip = Trip(simulation_id=sim.id)
    db.session.add(trip)
    db.session.commit()
    return jsonify({"message": "Симуляция запущена", "trip_id": trip.id}), 200


@sim_bp.route("/api/simulations/<int:sim_id>/stop", methods=["POST"])
def stop(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    sim.is_running = False
    sim.speed_kmh = 0
    db.session.commit()
    return jsonify({"message": "Симуляция остановлена"}), 200


@sim_bp.route("/api/simulations/<int:sim_id>/charge", methods=["POST"])
def charge(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    data = request.get_json() or {}
    mode = data.get("mode", "normal")
    rates = {"slow": 1, "normal": 10, "supercharger": 60}
    sim.battery_percent = min(100, sim.battery_percent + rates.get(mode, 10))
    db.session.commit()
    return jsonify({"battery_percent": sim.battery_percent}), 200