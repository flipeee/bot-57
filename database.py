import aiosqlite

DB_PATH = "ideas.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                is_banned INTEGER DEFAULT 0,
                role TEXT DEFAULT 'user'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                msg_id INTEGER PRIMARY KEY,
                text TEXT,
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                user_id INTEGER,
                idea_msg_id INTEGER,
                vote_type TEXT,
                UNIQUE(user_id, idea_msg_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pending_admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT
            )
        """)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone()

async def create_user(user_id, username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        await db.commit()

async def set_role(user_id, role):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
        await db.commit()

async def save_idea(msg_id, text):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO ideas (msg_id, text) VALUES (?, ?)", (msg_id, text))
        await db.commit()

async def get_vote(user_id, idea_msg_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT vote_type FROM votes WHERE user_id=? AND idea_msg_id=?", (user_id, idea_msg_id)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None

async def add_vote(user_id, idea_msg_id, vote_type):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO votes (user_id, idea_msg_id, vote_type) VALUES (?,?,?)", (user_id, idea_msg_id, vote_type))
        col = "likes" if vote_type == "like" else "dislikes"
        await db.execute(f"UPDATE ideas SET {col} = {col} + 1 WHERE msg_id=?", (idea_msg_id,))
        await db.commit()

async def switch_vote(user_id, idea_msg_id, new_type):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT vote_type FROM votes WHERE user_id=? AND idea_msg_id=?", (user_id, idea_msg_id)) as cur:
            old = (await cur.fetchone())[0]
        old_col = "likes" if old == "like" else "dislikes"
        new_col = "likes" if new_type == "like" else "dislikes"
        await db.execute(f"UPDATE ideas SET {old_col} = {old_col} - 1, {new_col} = {new_col} + 1 WHERE msg_id=?", (idea_msg_id,))
        await db.execute("UPDATE votes SET vote_type=? WHERE user_id=? AND idea_msg_id=?", (new_type, user_id, idea_msg_id))
        await db.commit()

async def get_counts(msg_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT likes, dislikes FROM ideas WHERE msg_id=?", (msg_id,)) as cur:
            return await cur.fetchone()

async def add_pending(user_id, username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO pending_admins (user_id, username) VALUES (?,?)", (user_id, username))
        await db.commit()

async def remove_pending(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM pending_admins WHERE user_id=?", (user_id,))
        await db.commit()

async def get_all_admins():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id, username, role FROM users WHERE role LIKE 'admin%'") as cur:
            return await cur.fetchall()

async def ban_user_by_username(username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_banned = 1 WHERE username = ?", (username,))
        await db.commit()