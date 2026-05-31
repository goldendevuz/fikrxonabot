import sqlite3
from config import DB_NAME


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Kategoriyalar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Kitoblar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category_id INTEGER,
            description TEXT,
            file_id TEXT,
            cover_id TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            downloads INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Yuklab olish tarixi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)

    conn.commit()
    conn.close()


# ─── Kategoriya funksiyalari ───────────────────────────────────────────────

def add_category(name: str):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_all_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    return rows


def delete_category(cat_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()


# ─── Kitob funksiyalari ────────────────────────────────────────────────────

def add_book(title, author, category_id, description, file_id, cover_id=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO books (title, author, category_id, description, file_id, cover_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, author, category_id, description, file_id, cover_id))
    conn.commit()
    conn.close()


def search_books(query: str):
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, c.name as category_name
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE LOWER(b.title) LIKE ? OR LOWER(b.author) LIKE ?
        ORDER BY b.downloads DESC
        LIMIT 10
    """, (f"%{query.lower()}%", f"%{query.lower()}%")).fetchall()
    conn.close()
    return rows


def get_books_by_category(category_id: int):
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, c.name as category_name
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.category_id = ?
        ORDER BY b.downloads DESC
    """, (category_id,)).fetchall()
    conn.close()
    return rows


def get_book_by_id(book_id: int):
    conn = get_connection()
    row = conn.execute("""
        SELECT b.*, c.name as category_name
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE b.id = ?
    """, (book_id,)).fetchone()
    conn.close()
    return row


def get_top_books(limit=5):
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, c.name as category_name
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        ORDER BY b.downloads DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def increment_downloads(book_id: int):
    conn = get_connection()
    conn.execute("UPDATE books SET downloads = downloads + 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def delete_book(book_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def get_all_books():
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, c.name as category_name
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        ORDER BY b.added_at DESC
    """).fetchall()
    conn.close()
    return rows


# ─── Foydalanuvchi funksiyalari ────────────────────────────────────────────

def register_user(user_id: int, username: str, full_name: str):
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO users (id, username, full_name)
        VALUES (?, ?, ?)
    """, (user_id, username, full_name))
    conn.commit()
    conn.close()


def log_download(user_id: int, book_id: int):
    conn = get_connection()
    conn.execute("""
        INSERT INTO downloads (user_id, book_id) VALUES (?, ?)
    """, (user_id, book_id))
    conn.commit()
    conn.close()


def get_user_downloads(user_id: int):
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, d.downloaded_at
        FROM downloads d
        JOIN books b ON d.book_id = b.id
        WHERE d.user_id = ?
        ORDER BY d.downloaded_at DESC
        LIMIT 10
    """, (user_id,)).fetchall()
    conn.close()
    return rows


def get_stats():
    conn = get_connection()
    books_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    downloads_count = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
    conn.close()
    return books_count, users_count, downloads_count
