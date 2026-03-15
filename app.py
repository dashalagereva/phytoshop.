# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import os

from db import (
    get_categories, get_products, get_product, get_product_reviews,
    add_review, get_cart_items, add_to_cart, remove_from_cart,
    verify_user, create_user, get_user_by_id, get_user_by_email,
    update_cart_quantity, create_order_from_cart, get_orders_by_user,
    get_all_orders, update_order_status, delete_order,
    add_category, update_category, delete_category,
    add_product, update_product, delete_product,
    get_all_users, update_user_admin, delete_user,
    get_all_reviews, delete_review
)


from datetime import timedelta

app = Flask(__name__)
app.secret_key = "super_secret_key_change_me"
app.permanent_session_lifetime = timedelta(days=7)

# Папка для загрузки картинок товаров
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# --------- вспомогательная функция ---------
@app.route("/cart/update", methods=["POST"])
def update_cart_route():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "not_authenticated"}), 401

    data = request.get_json()
    cart_id = data.get("cart_id")
    quantity = data.get("quantity")

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "bad_quantity"}), 400

    update_cart_quantity(cart_id, user["id"], quantity)

    # Пересчёт итоговой суммы корзины
    items = get_cart_items(user["id"])
    total = sum(item["price"] * item["quantity"] for item in items)

    return jsonify({
        "success": True,
        "cart_total": float(total)
    })
@app.route("/checkout", methods=["POST"])
def checkout():
    user = get_current_user()
    if not user:
        flash("Войдите, чтобы оформить заказ", "error")
        return redirect(url_for("index"))

    order_id = create_order_from_cart(user["id"])
    if not order_id:
        flash("Корзина пуста, нечего оформлять", "error")
        return redirect(url_for("cart"))

    flash(f"Заказ №{order_id} успешно создан", "success")
    return redirect(url_for("profile"))

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


# --------- маршруты ---------

@app.route("/")
def index():
    categories = get_categories()
    products = get_products()
    user = get_current_user()
    return render_template(
        "pages/index.html",
        categories=categories,
        products=products,
        user=user
    )


@app.route("/catalog")
def catalog():
    category_id = request.args.get("category_id", type=int)
    sort = request.args.get("sort", default="name_asc")
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)

    categories = get_categories()
    products = get_products(
        category_id=category_id,
        price_min=price_min,
        price_max=price_max,
        sort=sort
    )
    user = get_current_user()
    return render_template(
        "pages/catalog.html",
        categories=categories,
        products=products,
        current_category=category_id,
        sort=sort,
        price_min=price_min,
        price_max=price_max,
        user=user
    )



@app.route("/delivery")
def delivery():
    user = get_current_user()
    return render_template("pages/delivery.html", user=user)


@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_detail(product_id):
    user = get_current_user()
    product = get_product(product_id)
    if not product:
        flash("Товар не найден", "error")
        return redirect(url_for("catalog"))

    if request.method == "POST":
        if not user:
            flash("Нужно войти, чтобы оставлять отзывы", "error")
            return redirect(url_for("index"))
        rating = request.form.get("rating", type=int)
        comment = request.form.get("comment", "").strip()
        if rating and 1 <= rating <= 5:
            add_review(user["id"], product_id, rating, comment)
            flash("Отзыв добавлен", "success")
            return redirect(url_for("product_detail", product_id=product_id))
        else:
            flash("Неверная оценка", "error")

    reviews = get_product_reviews(product_id)
    return render_template(
        "pages/product_detail.html",
        user=user,
        product=product,
        reviews=reviews
    )


@app.route("/cart")
def cart():
    user = get_current_user()
    if not user:
        flash("Войдите, чтобы посмотреть корзину", "error")
        return redirect(url_for("index"))
    items = get_cart_items(user["id"])
    total = sum(item["price"] * item["quantity"] for item in items)
    return render_template(
        "pages/cart.html",
        user=user,
        items=items,
        total=total
    )


@app.route("/add_to_cart/<int:product_id>")
def add_to_cart_route(product_id):
    user = get_current_user()
    if not user:
        flash("Сначала войдите в систему", "error")
        return redirect(url_for("index"))
    add_to_cart(user["id"], product_id, 1)
    flash("Товар добавлен в корзину", "success")
    return redirect(request.referrer or url_for("catalog"))


@app.route("/remove_from_cart/<int:cart_id>")
def remove_from_cart_route(cart_id):
    user = get_current_user()
    if not user:
        flash("Сначала войдите в систему", "error")
        return redirect(url_for("index"))
    remove_from_cart(cart_id, user["id"])
    flash("Товар удалён из корзины", "success")
    return redirect(url_for("cart"))


@app.route("/profile")
def profile():
    user = get_current_user()
    if not user:
        flash("Нужно войти в систему", "error")
        return redirect(url_for("index"))

    orders = get_orders_by_user(user["id"])
    return render_template("pages/profile.html", user=user, orders=orders)


@app.route("/admin")
def admin():
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    active_tab = request.args.get("tab", "orders")

    orders = get_all_orders()
    categories = get_categories()
    products = get_products()
    users = get_all_users()
    reviews = get_all_reviews()

    return render_template(
        "pages/admin.html",
        user=user,
        active_tab=active_tab,
        orders=orders,
        categories=categories,
        products=products,
        users=users,
        reviews=reviews
    )


@app.post("/admin/categories/add")
def admin_add_category():
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    name = request.form.get("name")
    description = request.form.get("description", "")

    if not name:
        flash("Название категории обязательно", "error")
    else:
        add_category(name, description)
        flash("Категория добавлена", "success")

    return redirect(url_for("admin", tab="categories"))
@app.post("/admin/categories/<int:category_id>/edit")
def admin_edit_category(category_id):
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    name = request.form.get("name")
    description = request.form.get("description", "")

    if not name:
        flash("Название категории обязательно", "error")
    else:
        update_category(category_id, name, description)
        flash("Категория обновлена", "success")

    return redirect(url_for("admin", tab="categories"))
@app.post("/admin/categories/<int:category_id>/delete")
def admin_delete_category_route(category_id):
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    delete_category(category_id)
    flash("Категория удалена", "success")
    return redirect(url_for("admin", tab="categories"))

@app.post("/admin/orders/<int:order_id>/status")
def admin_update_order_status(order_id):
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    status = request.form.get("status")
    if status not in ("new", "processing", "completed", "cancelled"):
        flash("Неверный статус", "error")
    else:
        update_order_status(order_id, status)
        flash("Статус заказа обновлён", "success")

    return redirect(url_for("admin", tab="orders"))


@app.post("/admin/orders/<int:order_id>/delete")
def admin_delete_order(order_id):
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    delete_order(order_id)
    flash("Заказ удалён", "success")
    return redirect(url_for("admin", tab="orders"))
@app.post("/admin/products/save")
def admin_save_product():
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    product_id = request.form.get("product_id", type=int)
    name = request.form.get("name")
    category_id = request.form.get("category_id", type=int)
    description = request.form.get("description", "")
    price = request.form.get("price", type=float)
    stock = request.form.get("stock", type=int)
    is_active = 1 if request.form.get("is_active") == "on" else 0
    existing_image_url = request.form.get("existing_image_url")

    # Загрузка файла
    file = request.files.get("image_file")
    image_url = existing_image_url

    if file and file.filename:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        image_url = "/" + save_path.replace("\\", "/")

    if not (name and category_id is not None and price is not None and stock is not None):
        flash("Заполните обязательные поля товара", "error")
        return redirect(url_for("admin", tab="products"))

    if product_id:
        update_product(product_id, category_id, name, description, price, stock, is_active, image_url)
        flash("Товар обновлён", "success")
    else:
        add_product(category_id, name, description, price, stock, is_active, image_url)
        flash("Товар добавлен", "success")

    return redirect(url_for("admin", tab="products"))


@app.post("/admin/products/<int:product_id>/delete")
def admin_delete_product_route(product_id):
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    delete_product(product_id)
    flash("Товар удалён", "success")
    return redirect(url_for("admin", tab="products"))
@app.post("/admin/users/add")
def admin_add_user():
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    city = request.form.get("city")
    address = request.form.get("address")
    role = request.form.get("role", "customer")

    if not (full_name and email and password):
        flash("ФИО, email и пароль обязательны", "error")
    else:
        if get_user_by_email(email):
            flash("Пользователь с таким email уже существует", "error")
        else:
            create_user(full_name, email, password, phone, address, city, role)
            flash("Пользователь добавлен", "success")

    return redirect(url_for("admin", tab="users"))


@app.post("/admin/users/<int:user_id>/edit")
def admin_edit_user(user_id):
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    city = request.form.get("city")
    address = request.form.get("address")
    role = request.form.get("role", "customer")

    if not (full_name and email):
        flash("ФИО и email обязательны", "error")
    else:
        update_user_admin(user_id, full_name, email, phone, address, city, role)
        flash("Пользователь обновлён", "success")

    return redirect(url_for("admin", tab="users"))


@app.post("/admin/users/<int:user_id>/delete")
def admin_delete_user_route(user_id):
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    delete_user(user_id)
    flash("Пользователь удалён", "success")
    return redirect(url_for("admin", tab="users"))
@app.post("/admin/reviews/<int:review_id>/delete")
def admin_delete_review_route(review_id):
    user = get_current_user()
    if not user or user["role"] != "admin":
        flash("Доступ запрещён", "error")
        return redirect(url_for("index"))

    delete_review(review_id)
    flash("Отзыв удалён", "success")
    return redirect(url_for("admin", tab="reviews"))


# --------- аутентификация через модальное окно ---------


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    user = verify_user(email, password)
    if user:
        session.permanent = True
        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]
        session["user_role"] = user["role"]
        flash("Вы успешно вошли", "success")
    else:
        flash("Неверный email или пароль", "error")
    return redirect(request.referrer or url_for("index"))


@app.route("/register", methods=["POST"])
def register():
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    city = request.form.get("city")
    address = request.form.get("address")

    if not (full_name and email and password):
        flash("Заполните обязательные поля", "error")
        return redirect(request.referrer or url_for("index"))

    existing = get_user_by_email(email)
    if existing:
        flash("Пользователь с таким email уже существует", "error")
        return redirect(request.referrer or url_for("index"))

    user_id = create_user(full_name, email, password, phone, address, city, role="customer")
    # Автоматический вход
    session.permanent = True
    session["user_id"] = user_id
    session["user_name"] = full_name
    session["user_role"] = "customer"
    flash("Регистрация прошла успешно", "success")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
