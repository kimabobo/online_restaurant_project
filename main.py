import json
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, Menu, Users, Orders, Reservation
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-key-123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    admin_user = Users.query.filter_by(username="Admin").first()
    if not admin_user:
        admin_account = Users(
            username="Admin",
            password=generate_password_hash("SuperSecretAdminPass123")
        )
        db.session.add(admin_account)
        db.session.commit()

    if not Menu.query.first():
        test_items = [
            Menu(
                name="Маргарита",
                category="Піца",
                description="Класична італійська піца з томатним соусом та сиром",
                ingredients="Томатний соус, моцарела, базилік, оливкова олія",
                weight=420,
                price=180.0,
                image="https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500",
                is_active=True
            ),
            Menu(
                name="Пепероні",
                category="Піца",
                description="Пікантна піца з гострими ковбасками",
                ingredients="Томатний соус, моцарела, салямі пепероні",
                weight=450,
                price=220.0,
                image="https://images.unsplash.com/photo-1628840042765-356cda07504e?w=500",
                is_active=True
            ),
            Menu(
                name="Чотири сири",
                category="Піца",
                description="Ніжна сирна піца з вершковою основою",
                ingredients="Вершковий соус, моцарела, пармезан, горгонзола, дорблю",
                weight=400,
                price=240.0,
                image="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500",
                is_active=True
            ),
            Menu(
                name="Картопля фрі",
                category="Закуски",
                description="Хрустка картопля з сіллю та фірмовим кетчупом",
                ingredients="Картопля, сіль, олія рослинна",
                weight=200,
                price=95.0,
                image="https://images.unsplash.com/photo-1630384060421-cb20d0e0649d?w=500",
                is_active=True
            ),
            Menu(
                name="Курячі нагетси",
                category="Закуски",
                description="Соковите куряче філе в хрусткій паніровці",
                ingredients="Куряче філе, сухарі панко, спеції, часниковий соус",
                weight=220,
                price=135.0,
                image="https://images.unsplash.com/photo-1562967914-608f82629710?w=500",
                is_active=True
            ),
            Menu(
                name="Сирні палички",
                category="Закуски",
                description="Тягуча моцарела в золотистій скоринці з соусом тар-тар",
                ingredients="Сир моцарела, панірувальні сухарі, трави",
                weight=180,
                price=145.0,
                image="https://images.unsplash.com/photo-1548340748-6d2b7d7da280?w=500",
                is_active=True
            ),
            Menu(
                name="Тірамісу",
                category="Десерти",
                description="Традиційний італійський кавовий десерт",
                ingredients="Савоярді, маскарпоне, еспресо, какао-порошок",
                weight=150,
                price=120.0,
                image="https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500",
                is_active=True
            ),
            Menu(
                name="Чизкейк Нью-Йорк",
                category="Десерти",
                description="Класичний запечений чизкейк із ніжним сирним кремом",
                ingredients="Крем-сир, пісочна основа, ваніль, полуничний топінг",
                weight=160,
                price=130.0,
                image="https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500",
                is_active=True
            ),
            Menu(
                name="Лимонад Класичний",
                category="Напої",
                description="Освіжаючий домашній напій з лимоном і м'ятою",
                ingredients="Вода очищена, свіжий сік лимона, цукровий сироп, м'ята",
                weight=500,
                price=65.0,
                image="https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500",
                is_active=True
            ),
            Menu(
                name="Кока-Кола",
                category="Напої",
                description="Охолоджений класичний газований напій",
                ingredients="Вода, карамельний колер, кофеїн, діоксид вуглецю",
                weight=500,
                price=50.0,
                image="https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500",
                is_active=True
            )
        ]
        db.session.bulk_save_objects(test_items)
        db.session.commit()

@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = Users.query.get(user_id)

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/menu")
def menu():
    all_items = Menu.query.filter_by(is_active=True).all()
    
    categories = {}
    for item in all_items:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item)

    return render_template("menu.html", categories=categories)

@app.route("/random_dish")
def random_dish():
    dishes = Menu.query.filter_by(is_active=True).all()
    if dishes:
        lucky_dish = random.choice(dishes)
        return redirect(url_for("position", name=lucky_dish.name))
    return redirect(url_for("menu"))

@app.route("/position/<name>")
def position(name):
    item = Menu.query.filter_by(name=name, is_active=True).first_or_404()
    return render_template("position.html", item=item)

@app.route("/add_to_cart/<int:item_id>", methods=["POST"])
def add_to_cart(item_id):
    item = Menu.query.get_or_404(item_id)
    cart = session.get("cart", {})

    quantity = int(request.form.get("quantity", 1))
    if quantity < 1:
        quantity = 1

    str_id = str(item_id)
    if str_id in cart:
        cart[str_id]["quantity"] += quantity
    else:
        cart[str_id] = {
            "name": item.name,
            "price": item.price,
            "quantity": quantity
        }

    session["cart"] = cart
    session.modified = True
    return redirect(url_for("position", name=item.name))

@app.route("/create_order", methods=["GET", "POST"])
def create_order():
    cart = session.get("cart", {})
    total_price = sum(item["price"] * item["quantity"] for item in cart.values())

    if request.method == "POST":
        if not g.user:
            return redirect(url_for("login"))

        if cart:
            new_order = Orders(
                user_id=g.user.id,
                total_amount=total_price,
                items_data=json.dumps(cart)
            )
            db.session.add(new_order)
            db.session.commit()

            session.pop("cart", None)
            session.modified = True

            return redirect(url_for("my_orders"))

    return render_template("create_order.html", cart=cart, total_price=total_price)

@app.route("/clear_cart", methods=["POST"])
def clear_cart():
    session.pop("cart", None)
    session.modified = True
    return redirect(url_for("create_order"))

@app.route("/my_orders")
def my_orders():
    if not g.user:
        return redirect(url_for("login"))

    orders = Orders.query.filter_by(user_id=g.user.id).order_by(Orders.created_at.desc()).all()
    return render_template("my_orders.html", orders=orders)

@app.route("/my_order/<int:id>")
def my_order(id):
    if not g.user:
        return redirect(url_for("login"))

    order = Orders.query.filter_by(id=id, user_id=g.user.id).first_or_404()
    items = json.loads(order.items_data)
    return render_template("my_order.html", order=order, items=items)

@app.route("/cancel_order/<int:id>", methods=["POST"])
def cancel_order(id):
    if not g.user:
        return redirect(url_for("login"))

    order = Orders.query.filter_by(id=id, user_id=g.user.id).first_or_404()
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for("my_orders"))

@app.route("/reservation", methods=["GET", "POST"])
def reservation():
    if not g.user:
        return redirect(url_for("login"))

    success = False
    if request.method == "POST":
        table_number = int(request.form.get("table_number"))
        guests_count = int(request.form.get("guests_count"))
        reservation_time = request.form.get("reservation_time")

        new_reservation = Reservation(
            user_id=g.user.id,
            table_number=table_number,
            guests_count=guests_count,
            reservation_time=reservation_time
        )
        db.session.add(new_reservation)
        db.session.commit()
        success = True

    return render_template("reservation.html", success=success)

@app.route("/add_position", methods=["GET", "POST"])
def add_position():
    if not g.user or g.user.username != "Admin":
        return "Доступ заборонено: потрібні права адміністратора (Admin).", 403

    error = None
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category", "Піца")
        description = request.form.get("description")
        ingredients = request.form.get("ingredients")
        price = request.form.get("price")
        weight = request.form.get("weight")
        image = request.form.get("image")

        existing_item = Menu.query.filter_by(name=name).first()
        if existing_item:
            error = "Позиція з такою назвою вже існує!"
        else:
            new_item = Menu(
                name=name,
                category=category,
                description=description,
                ingredients=ingredients,
                price=float(price),
                weight=int(weight),
                image=image,
                is_active=True
            )
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for("menu"))

    return render_template("add_position.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")

        if username.lower() == "admin":
            error = "Цей логін зарезервовано системою. Будь ласка, оберіть інший."
        else:
            existing_user = Users.query.filter_by(username=username).first()
            if existing_user:
                error = "Користувач із таким логіном вже існує."
            else:
                hashed_password = generate_password_hash(password)
                new_user = Users(username=username, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("login"))

    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.password, password):
            error = "Невірний логін або пароль."
        else:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)