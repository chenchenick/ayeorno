import sqlite3

class DBHandler:
    def __init__(self, db_name='votes.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                congress TEXT,
                question TEXT,
                bill_description TEXT,
                vote_type TEXT,
                status TEXT,
                roll_call TEXT,
                bill_number TEXT,
                session TEXT,
                yea_count INTEGER,
                nay_count INTEGER,
                present_count INTEGER,
                not_voting_count INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS individual_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vote_id INTEGER,
                member_link TEXT,
                representative_name TEXT,
                vote TEXT,
                party TEXT,
                state TEXT,
                FOREIGN KEY(vote_id) REFERENCES votes(id)
            )
        ''')
        self.conn.commit()

    def insert_vote(self, date, congress, question, bill_description, vote_type, status, roll_call, bill_number, session, yea_count, nay_count, present_count, not_voting_count):
        self.cursor.execute('''
            INSERT INTO votes (date, congress, question, bill_description, vote_type, status, roll_call, bill_number, session, yea_count, nay_count, present_count, not_voting_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, congress, question, bill_description, vote_type, status, roll_call, bill_number, session, yea_count, nay_count, present_count, not_voting_count))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_individual_vote(self, vote_id, member_link, representative_name, vote, party, state):
        self.cursor.execute('''
            INSERT INTO individual_votes (vote_id, member_link, representative_name, vote, party, state)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (vote_id, member_link, representative_name, vote, party, state))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def insert_year_summary(self, year, total_votes, processed_votes, failed_votes):
        query = """
        INSERT INTO year_summary (year, total_votes, processed_votes, failed_votes)
        VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (year, total_votes, processed_votes, failed_votes))
        self.conn.commit()

    def insert_overall_summary(self, total_votes, processed_votes, failed_votes):
        query = """
        INSERT INTO overall_summary (total_votes, processed_votes, failed_votes)
        VALUES (?, ?, ?)
        """
        self.cursor.execute(query, (total_votes, processed_votes, failed_votes))
        self.conn.commit()

    def create_summary_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS year_summary (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            total_votes INTEGER,
            processed_votes INTEGER,
            failed_votes INTEGER
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS overall_summary (
            id INTEGER PRIMARY KEY,
            total_votes INTEGER,
            processed_votes INTEGER,
            failed_votes INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()