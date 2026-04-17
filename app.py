from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DB_NAME = "liquor.db"

# ---------------------------
# DATABASE INIT (รองรับ upgrade)
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # categories
    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # liquors
    c.execute("""
    CREATE TABLE IF NOT EXISTS liquors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        image TEXT,
        stock INTEGER,
        category_id INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )
    """)

    # upgrade columns
    try:
        c.execute("ALTER TABLE liquors ADD COLUMN alcohol_content REAL")
    except:
        pass

    try:
        c.execute("ALTER TABLE liquors ADD COLUMN volume INTEGER")
    except:
        pass

    # insert default categories
    default_categories = ["Whiskey", "Wine", "Gin", "Vodka", "Craft Beer"]
    for cat in default_categories:
        c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

    conn.commit()
    conn.close()

# ---------------------------
# HOME (LEFT JOIN + newest first)
# ---------------------------
@app.route("/")
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    SELECT liquors.*, categories.name
    FROM liquors
    LEFT JOIN categories ON liquors.category_id = categories.id
    ORDER BY liquors.id DESC
    """)

    data = c.fetchall()
    conn.close()
    return render_template("index.html", liquors=data)

# ---------------------------
# ADD
# ---------------------------
@app.route("/append", methods=["GET", "POST"])
def append():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        image = request.form["image"]
        category_id = request.form["category"]

        try:
            price = float(request.form["price"])
            stock = int(request.form["stock"])
            alcohol = float(request.form["alcohol"])
            volume = int(request.form["volume"])
        except:
            return "❌ กรอกข้อมูลตัวเลขผิด"

        c.execute("""
        INSERT INTO liquors (name, price, image, stock, category_id, alcohol_content, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, price, image, stock, category_id, alcohol, volume))

        conn.commit()
        conn.close()
        return redirect("/")

    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    conn.close()

    return render_template("form.html", categories=categories, liquor=None)

# ---------------------------
# EDIT
# ---------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == "POST":
        try:
            price = float(request.form["price"])
            stock = int(request.form["stock"])
            alcohol = float(request.form["alcohol"])
            volume = int(request.form["volume"])
        except:
            return "❌ กรอกข้อมูลตัวเลขผิด"

        c.execute("""
        UPDATE liquors
        SET name=?, price=?, image=?, stock=?, category_id=?, alcohol_content=?, volume=?
        WHERE id=?
        """, (
            request.form["name"],
            price,
            request.form["image"],
            stock,
            request.form["category"],
            alcohol,
            volume,
            id
        ))

        conn.commit()
        conn.close()
        return redirect("/")

    c.execute("SELECT * FROM liquors WHERE id=?", (id,))
    liquor = c.fetchone()

    c.execute("SELECT * FROM categories")
    categories = c.fetchall()

    conn.close()
    return render_template("form.html", liquor=liquor, categories=categories)

# ---------------------------
# DELETE
# ---------------------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DELETE FROM liquors WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)