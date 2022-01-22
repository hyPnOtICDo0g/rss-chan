import psycopg2
from psycopg2 import sql
from bot import LOGGER, DATABASE_URL

rss_dict = {}

# Database Operations
class PostgreSQL():
    def connect(self):
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.cur = self.conn.cursor()
        except psycopg2.DatabaseError as error:
            LOGGER.error(error)

    def disconnect(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def init(self):
        try:
            self.connect()
            self.cur.execute("CREATE TABLE rss (name text, link text, last text, title text, template text)")
            self.disconnect()
            LOGGER.info("Database Created.")
        except psycopg2.errors.DuplicateTable:
            LOGGER.info("Database already exists.")
            self.rss_load()
        except AttributeError:
            LOGGER.error("Database not found, exiting now.")
            exit(1)

    def load_all(self):
        self.connect()
        self.cur.execute("SELECT * FROM rss")
        rows = self.cur.fetchall()
        self.disconnect()
        return rows

    def write(self, name, link, last, title, template):
        self.connect()
        q = [(name), (link), (last), (title), (template)]
        self.cur.execute("INSERT INTO rss (name, link, last, title, template) VALUES(%s, %s, %s, %s, %s)", q)
        self.disconnect()
        self.rss_load()

    def update_items(self, link, last, name, title):
        self.connect()
        q = [(last), (title), (link), (name)]
        self.cur.execute("UPDATE rss SET last=%s, title=%s, link=%s WHERE name=%s", q)
        self.disconnect()

    def update_one(self, field, q):
        self.connect()
        self.cur.execute(sql.SQL("UPDATE rss SET {F}=%s WHERE name=%s").format(F=sql.Identifier(field)), q)
        self.disconnect()
        self.rss_load()

    def find_one(self, field, q):
        self.connect()
        self.cur.execute(sql.SQL("SELECT {F} FROM rss WHERE name = %s").format(F=sql.Identifier(field)), q)
        result = self.cur.fetchone()
        self.disconnect()
        return result

    def find_all(self, field):
        self.connect()
        self.cur.execute(sql.SQL("SELECT {F} FROM rss").format(F=sql.Identifier(field)))
        results = [x[0] for x in self.cur.fetchall()]
        self.disconnect()
        return results

    def delete(self, q):
        try:
            self.connect()
            self.cur.execute("DELETE FROM rss WHERE name = %s", q)
            self.disconnect()
        except psycopg2.errors.UndefinedTable:
            pass
        self.rss_load()

    def deleteall(self):
        self.connect()
        # clear database & dictionary
        self.cur.execute("TRUNCATE TABLE rss")
        self.disconnect()
        rss_dict.clear()
        LOGGER.info('Database reset.')

    def rss_load(self):
        # if the dict is not empty, empty it
        if bool(rss_dict):
            rss_dict.clear()

        for row in self.load_all():
            rss_dict[row[0]] = (row[1], row[2], row[3], row[4])

postgres = PostgreSQL()
