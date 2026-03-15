# db.py
import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash


def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="eboldaun23",
        database="phytoshop",
        port=3306,
        cursorclass=DictCursor,
        autocommit=True
    )


# ---------- USERS ----------

def get_user_by_email(email: str):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            return cur.fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            return cur.fetchone()
    finally:
        conn.close()


def create_user(full_name, email, password, phone=None, address=None, city=None, role="customer"):
    password_hash = generate_password_hash(password)
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (full_name, email, password_hash, phone, address, city, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (full_name, email, password_hash, phone, address, city, role)
            )
            return cur.lastrowid
    finally:
        conn.close()


def verify_user(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


# ---------- CATEGORIES / PRODUCTS ----------

def get_categories():
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM categories ORDER BY name")
            return cur.fetchall()
    finally:
        conn.close()


def get_products(category_id=None, price_min=None, price_max=None, sort="name_asc"):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT p.*, c.name AS category_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1
            """
            params = []

            if category_id:
                query += " AND p.category_id = %s"
                params.append(category_id)

            if price_min is not None:
                query += " AND p.price >= %s"
                params.append(price_min)

            if price_max is not None:
                query += " AND p.price <= %s"
                params.append(price_max)

            # Сортировка
            if sort == "price_asc":
                query += " ORDER BY p.price ASC"
            elif sort == "price_desc":
                query += " ORDER BY p.price DESC"
            elif sort == "rating_desc":
                # Сначала товары с рейтингом, затем без
                query += " ORDER BY p.rating_avg IS NULL ASC, p.rating_avg DESC, p.name ASC"
            elif sort == "name_desc":
                query += " ORDER BY p.name DESC"
            else:  # name_asc по умолчанию
                query += " ORDER BY p.name ASC"

            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()


def get_product(product_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.*, c.name AS category_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.id=%s
                """,
                (product_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()


def get_product_reviews(product_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.*, u.full_name
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.product_id=%s
                ORDER BY r.created_at DESC
                """,
                (product_id,)
            )
            return cur.fetchall()
    finally:
        conn.close()
def update_cart_quantity(cart_id: int, user_id: int, quantity: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            if quantity <= 0:
                # если количество 0 или меньше — удаляем позицию
                cur.execute(
                    "DELETE FROM cart WHERE id=%s AND user_id=%s",
                    (cart_id, user_id)
                )
            else:
                cur.execute(
                    "UPDATE cart SET quantity=%s WHERE id=%s AND user_id=%s",
                    (quantity, cart_id, user_id)
                )
    finally:
        conn.close()
def create_order_from_cart(user_id: int):
    """
    Создаёт заказ на основании текущей корзины пользователя.
    Возвращает ID заказа или None, если корзина пуста.
    """
    conn = connect_db()
    try:
        conn.autocommit(False)
        with conn.cursor() as cur:
            # Берём позиции корзины вместе с ценами товаров
            cur.execute(
                """
                SELECT c.id AS cart_id, c.product_id, c.quantity, p.price
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id=%s
                """,
                (user_id,)
            )
            items = cur.fetchall()
            if not items:
                conn.rollback()
                return None

            total = sum(row["price"] * row["quantity"] for row in items)

            # Создаём заказ
            cur.execute(
                """
                INSERT INTO orders (user_id, status, total_amount)
                VALUES (%s, 'new', %s)
                """,
                (user_id, total)
            )
            order_id = cur.lastrowid

            # Позиции заказа
            for row in items:
                cur.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, row["product_id"], row["quantity"], row["price"])
                )

            # Чистим корзину
            cur.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))

        conn.commit()
        return order_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit(True)
        conn.close()

def get_orders_by_user(user_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM orders
                WHERE user_id=%s
                ORDER BY order_date DESC
                """,
                (user_id,)
            )
            return cur.fetchall()
    finally:
        conn.close()

def add_review(user_id: int, product_id: int, rating: int, comment: str):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reviews (user_id, product_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, product_id, rating, comment)
            )
    finally:
        conn.close()


# ---------- CART ----------

def get_cart_items(user_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id AS cart_id,
                       c.quantity,
                       p.*
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id=%s
                """,
                (user_id,)
            )
            return cur.fetchall()
    finally:
        conn.close()


def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            # Если уже есть, увеличим количество
            cur.execute(
                "SELECT id, quantity FROM cart WHERE user_id=%s AND product_id=%s",
                (user_id, product_id)
            )
            row = cur.fetchone()
            if row:
                new_qty = row["quantity"] + quantity
                cur.execute(
                    "UPDATE cart SET quantity=%s WHERE id=%s",
                    (new_qty, row["id"])
                )
            else:
                cur.execute(
                    """
                    INSERT INTO cart (user_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, product_id, quantity)
                )
    finally:
        conn.close()


def remove_from_cart(cart_id: int, user_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cart WHERE id=%s AND user_id=%s", (cart_id, user_id))
    finally:
        conn.close()
def get_all_orders():
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT o.*, u.full_name
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.order_date DESC
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


def update_order_status(order_id: int, status: str):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE orders SET status=%s WHERE id=%s",
                (status, order_id)
            )
    finally:
        conn.close()


def delete_order(order_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM orders WHERE id=%s", (order_id,))
    finally:
        conn.close()
def add_category(name: str, description: str):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO categories (name, description) VALUES (%s, %s)",
                (name, description)
            )
    finally:
        conn.close()


def update_category(category_id: int, name: str, description: str):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE categories SET name=%s, description=%s WHERE id=%s",
                (name, description, category_id)
            )
    finally:
        conn.close()


def delete_category(category_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM categories WHERE id=%s", (category_id,))
    finally:
        conn.close()
def add_product(category_id, name, description, price, stock, is_active, image_url):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO products (category_id, name, description, price, stock, is_active, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (category_id, name, description, price, stock, is_active, image_url)
            )
    finally:
        conn.close()


def update_product(product_id, category_id, name, description, price, stock, is_active, image_url):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE products
                SET category_id=%s,
                    name=%s,
                    description=%s,
                    price=%s,
                    stock=%s,
                    is_active=%s,
                    image_url=%s
                WHERE id=%s
                """,
                (category_id, name, description, price, stock, is_active, image_url, product_id)
            )
    finally:
        conn.close()


def delete_product(product_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    finally:
        conn.close()
def get_all_users():
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, full_name, email, phone, city, role, created_at
                FROM users
                ORDER BY created_at DESC
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


def update_user_admin(user_id, full_name, email, phone, address, city, role):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET full_name=%s,
                    email=%s,
                    phone=%s,
                    address=%s,
                    city=%s,
                    role=%s
                WHERE id=%s
                """,
                (full_name, email, phone, address, city, role, user_id)
            )
    finally:
        conn.close()


def delete_user(user_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    finally:
        conn.close()
def get_all_reviews():
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT r.*, u.full_name, p.name AS product_name
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                JOIN products p ON r.product_id = p.id
                ORDER BY r.created_at DESC
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


def delete_review(review_id: int):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM reviews WHERE id=%s", (review_id,))
    finally:
        conn.close()
