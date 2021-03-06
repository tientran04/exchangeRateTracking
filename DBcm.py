import psycopg2


class UseDatabase:

    def __init__(self, config) -> None:
        self.configuration = config

    def __enter__(self):
        if type(self.configuration) is str:
            try:
                self.conn = psycopg2.connect(self.configuration)
                self.cursor = self.conn.cursor()
                return self.cursor
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
        else:
            try:
                self.conn = psycopg2.connect(**self.configuration)
                self.cursor = self.conn.cursor()
                return self.cursor
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        
        if exc_type is not None:
            print(exc_type, exc_value, exc_trace)
            
    
