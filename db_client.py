import getpass
import pg8000

HOST = 'bartik.mines.edu'
DB = 'csci403'

class DB_Client:
    
    def __init__(self):
        
        self.user = input("Username: ")
        print("Password: ", end='')
        self.secret = getpass.getpass()
        self.db = pg8000.connect(user=self.user, password=self.secret,
                  host=HOST, database=DB)
        self.cursor = self.db.cursor()
        
    def refresh_tables(self):
        try:
            self.cursor.execute("drop table if exists artist cascade")
            self.cursor.execute("drop table if exists album cascade")
            self.cursor.execute("drop table if exists track cascade")
            query = """create table artist (
                       id TEXT PRIMARY KEY, 
                       name TEXT
                       )"""
            self.cursor.execute(query)
            
            query = """create table album (
                       id TEXT PRIMARY KEY, 
                       title TEXT NOT NULL,
                       artist_id TEXT REFERENCES artist (id),
                       score NUMERIC(2),
                       year NUMERIC(4)
                       )"""
            self.cursor.execute(query)
            
            query = """create table track (
                       id TEXT PRIMARY KEY, 
                       album_id TEXT REFERENCES album (id),
                       title TEXT NOT NULL,
                       danceability NUMERIC(4,3),
                       energy NUMERIC(4,3),
                       key INTEGER,
                       loudness NUMERIC(5,3),
                       mode INTEGER,
                       speechiness NUMERIC(4,3),
                       acousticness NUMERIC(4,3),
                       instrumentalness NUMERIC(4,3),
                       liveness NUMERIC(4,3),
                       valence NUMERIC(4,3),
                       tempo NUMERIC (5,2),
                       duration_ms INTEGER,
                       time_signature INTEGER
                       )"""
            self.cursor.execute(query)
            self.db.commit()
            
        except pg8000.Error as e:
            print("database error:", str(e))
        
    def insert_album(self, album):
        #step 1: add artist to db
        #step 2: add album to db
        #step 3: add songs to db
        try:
            values = album.artist_psql()
            query = """ INSERT INTO artist VALUES (%s,%s)
                        ON CONFLICT DO NOTHING"""
            
            self.cursor.execute(query,values)
            self.db.commit()
            
            values = album.to_psql()
            query = """ INSERT INTO album VALUES (
                        %s,%s,%s,%s,%s)
                        ON CONFLICT DO NOTHING"""

            self.cursor.execute(query,values)
            self.db.commit()

            for track in album.tracks:
                values = track.to_psql()
                query = """ INSERT INTO track VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING"""

                self.cursor.execute(query,values)

            self.db.commit()
            
        except pg8000.Error as e:
            print("database error:", str(e))