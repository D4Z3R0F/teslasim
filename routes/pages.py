from flask import Blueprint, render_template, request, redirect, url_for
from models import db, User, Simulation

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    return render_template("index.html")


@pages_bp.route("/simulation/<int:sim_id>")
def simulation_page(sim_id):
    sim = db.session.get(Simulation, sim_id)
    if not sim:
        return "Симуляция не найдена", 404
    return render_template("simulation.html", sim=sim)


@pages_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # При успешном входе перекидываем на список симуляций (дашборд)
            return redirect(url_for("pages.dashboard"))
        return render_template("login.html", error="Неверный email или пароль"), 401
    return render_template("login.html")


@pages_bp.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        
        if not username or len(password) < 8 or "@" not in email:
            return render_template("register.html", error="Проверьте поля: имя, email, пароль минимум 8 символов"), 400
            
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="Email уже занят"), 400
            
        user = User(username=username, email=email, role="driver")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("pages.login_page"))
    return render_template("register.html")


@pages_bp.route("/dashboard")
def dashboard():
    # В учебных целях показываем все симуляции в базе
    sims = Simulation.query.all()
    return render_template("dashboard.html", simulations=sims)