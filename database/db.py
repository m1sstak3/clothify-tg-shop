import aiosqlite
from typing import List, Tuple, Optional

DB_NAME = "shop.sqlite3"

async def init_db(seed_data: bool = False):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        await db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            sizes TEXT NOT NULL,
            photo_id TEXT
        )
        ''')
        
        await db.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            product_id INTEGER,
            size TEXT,
            address TEXT,
            status TEXT DEFAULT 'Новый',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        await db.commit()
        
        if seed_data:
            # Заполнение случайными товарами, если каталог пуст
            async with db.execute('SELECT COUNT(*) FROM products') as cursor:
                row = await cursor.fetchone()
                if row and row[0] == 0:
                    mock_products = [
                        ("Худи Yellow", "Фирменное ярко-желтое худи оверсайз с вышитым логотипом.", 4500.0, "S, M, L, XL", "assets/hoodie.png"),
                        ("Футболка Basic", "Черная футболка из премиального хлопка с ярким принтом на спине.", 2200.0, "XS, S, M, L", "assets/tshirt.png"),
                        ("Джоггеры Tech", "Спортивные штаны-джоггеры графитового цвета для активной жизни.", 3800.0, "M, L, XL", "assets/joggers.png"),
                        ("Свитшот Relax", "Удлиненный свитшот молочного цвета с минималистичной надписью.", 4200.0, "S, M, L", "assets/sweatshirt.png"),
                        ("Панама Summer", "Стильная желтая панама для защиты от солнца и ярких образов.", 1500.0, "One Size", "assets/panama.png")
                    ]
                    await db.executemany(
                        'INSERT INTO products (name, description, price, sizes, photo_id) VALUES (?, ?, ?, ?, ?)',
                        mock_products
                    )
                    await db.commit()

async def ensure_user_exists(user_id: int, username: Optional[str]):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)', (user_id, username))
        await db.commit()

async def add_product(name: str, description: str, price: float, sizes: str, photo_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO products (name, description, price, sizes, photo_id) VALUES (?, ?, ?, ?, ?)',
                         (name, description, price, sizes, photo_id))
        await db.commit()

async def get_products() -> List[Tuple]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM products') as cursor:
            return await cursor.fetchall()
            
async def get_product(product_id: int) -> Optional[Tuple]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM products WHERE id = ?', (product_id,)) as cursor:
            return await cursor.fetchone()

async def create_order(user_id: int, username: str, product_id: int, size: str, address: str) -> int:
    await ensure_user_exists(user_id, username)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('INSERT INTO orders (user_id, username, product_id, size, address) VALUES (?, ?, ?, ?, ?)',
                                  (user_id, username, product_id, size, address))
        await db.commit()
        return cursor.lastrowid

async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        await db.commit()

async def get_stats() -> dict:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT COUNT(*), SUM(p.price) FROM orders o JOIN products p ON o.product_id = p.id') as cursor:
            row = await cursor.fetchone()
            return {
                "total_orders": row[0] or 0,
                "total_sales": row[1] or 0.0
            }

async def get_orders(limit: int = 10) -> List[Tuple]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT ?', (limit,)) as cursor:
            return await cursor.fetchall()
