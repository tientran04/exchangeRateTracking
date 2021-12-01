import psycopg2


class UseDatabase:

    def __init__(self, config: dict) -> None:
        self.configuration = config

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def __exit__(self) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        
            
    
