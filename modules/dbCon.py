import aiosqlite

class Database:
    def __init__(self, db_file='db/data.db'):
        self.db_file = db_file
        self.connection = None

    async def connect(self):
        """Connect to the SQLite database."""
        self.connection = await aiosqlite.connect(self.db_file)
        await self.create_table()

    async def create_table(self):
        """Create the cases table if it doesn't exist."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                serial_number INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT NOT NULL,
                case_number TEXT NOT NULL,
                party_name TEXT NOT NULL,
                status TEXT
            );
        """)
        await self.connection.commit()

    async def add_case(self, district, case_number, party_name, status=None):
        """Add a new case to the database."""
        await self.connection.execute("""
            INSERT INTO cases (district, case_number, party_name, status)
            VALUES (?, ?, ?, ?);
        """, (district, case_number, party_name, status))
        await self.connection.commit()

    async def edit_district(self, serial_number, new_district):
        """Edit the district of a case."""
        await self.connection.execute("""
            UPDATE cases
            SET district = ?
            WHERE serial_number = ?;
        """, (new_district, serial_number))
        await self.connection.commit()

    async def edit_case_number(self, serial_number, new_case_number):
        """Edit the case number of a case."""
        await self.connection.execute("""
            UPDATE cases
            SET case_number = ?
            WHERE serial_number = ?;
        """, (new_case_number, serial_number))
        await self.connection.commit()

    async def edit_party_name(self, serial_number, new_party_name):
        """Edit the party name of a case."""
        await self.connection.execute("""
            UPDATE cases
            SET party_name = ?
            WHERE serial_number = ?;
        """, (new_party_name, serial_number))
        await self.connection.commit()

    async def edit_status(self, serial_number, new_status):
        """Edit the status of a case."""
        await self.connection.execute("""
            UPDATE cases
            SET status = ?
            WHERE serial_number = ?;
        """, (new_status, serial_number))
        await self.connection.commit()

    async def delete_case(self, serial_number):
        """Delete a case from the database."""
        await self.connection.execute("""
            DELETE FROM cases
            WHERE serial_number = ?;
        """, (serial_number,))
        await self.connection.commit()

    async def get_case(self, serial_number):
        """Retrieve a case by serial number."""
        cursor = await self.connection.execute("""
            SELECT * FROM cases
            WHERE serial_number = ?;
        """, (serial_number,))
        return await cursor.fetchone()

    async def search_cases(self, query):
        """Perform a fuzzy search on the party name."""
        cursor = await self.connection.execute("""
            SELECT * FROM cases
            WHERE party_name LIKE ?;
        """, (f"%{query}%",))
        return await cursor.fetchall()

    async def search_all_fields(self, query):
        """Perform a fuzzy search across all fields."""
        cursor = await self.connection.execute("""
            SELECT * FROM cases
            WHERE district LIKE ? 
            OR case_number LIKE ?
            OR party_name LIKE ?
            OR status LIKE ?
            ORDER BY serial_number DESC;
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        return await cursor.fetchall()

    async def get_all_cases(self):
        """Get all cases ordered by serial number."""
        cursor = await self.connection.execute("SELECT * FROM cases ORDER BY serial_number DESC")
        return await cursor.fetchall()

    async def close(self):
        """Close the database connection."""
        await self.connection.close()