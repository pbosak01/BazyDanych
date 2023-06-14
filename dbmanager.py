import cx_Oracle
from datetime import datetime
# jak wywoływać procedury (funkcje tak samo)
# cursor.execute("begin \
#                 addclient('Bzymon', 'Jasło');\
#                 end;")

# r - rezerwacja
# p - wypozyczony
# c - anulowany
# d - zakończone

class DBManager:
    def __init__(self) -> None:
        with open('password.txt', 'r') as f:
            self.password = f.read()
        try:
            cx_Oracle.init_oracle_client(lib_dir="C:\\instantclient_19_9")
        except cx_Oracle.DatabaseError:
            pass
        self._dsn = cx_Oracle.makedsn("dbmanage.lab.ii.agh.edu.pl", "1521", sid="DBMANAGE")
        self._connection = cx_Oracle.connect(user="BD_406248", password=self.password, dsn=self._dsn)
        self._cursor = self._connection.cursor()
    
    def select_from_table(self, table_name: str):
        try:
            self._cursor.execute(f"select * from {table_name}")
            data = self._cursor.fetchall()
            new_data = [[] for _ in range(len(data))]

            col_names = [row[0] for row in self._cursor.description]

            if table_name in ['rent', 'renthist']:
                for i in range(len(data)):
                    for thing in data[i]:
                        if type(thing) == datetime:
                            new_data[i].append(thing.strftime("%Y-%m-%d"))
                            continue
                        new_data[i].append(thing)
            else:
                new_data = data
            new_data.sort(key=lambda x : x[0])
            new_data.insert(0, col_names)
            return new_data
        except cx_Oracle.DatabaseError:
            return []
    
    def add_rent(self, client_id, date_from, date_to, status = "R"):
        self._cursor.execute(f"begin\
                               addrent({client_id}, '{date_from}', '{date_to}', '{status}');\
                               end;")
    
    def get_available_items(self, date_from, date_to):
        result = self._cursor.execute(f"select * from AVAILABLEITEMS('{date_from}', '{date_to}')")
        data = result.fetchall()
        data.sort(key = lambda x : x[0])
        col_names = [row[0] for row in self._cursor.description]
        data.insert(0, col_names)
        return data
    
    def show_my_reservations(self, client_id):
        result = self._cursor.execute(f"select * from clientrents('{client_id}')")
        data = result.fetchall()
        col_names = [row[0] for row in self._cursor.description]

        new_data = [[] for _ in range(len(data))]

        for i in range(len(data)):
            for thing in data[i]:
                if type(thing) == datetime:
                    new_data[i].append(thing.strftime("%Y-%m-%d"))
                    continue
                new_data[i].append(thing)

        new_data.sort(key = lambda x : x[0])
        new_data.insert(0, col_names)
        return new_data
    
    def show_my_reserved_items(self, client_id):
        result = self._cursor.execute(f"select * from myreservations('{client_id}')")
        data = result.fetchall()
        col_names = [row[0] for row in self._cursor.description]

        new_data = [[] for _ in range(len(data))]

        for i in range(len(data)):
            for thing in data[i]:
                if type(thing) == datetime:
                    new_data[i].append(thing.strftime("%Y-%m-%d"))
                    continue
                new_data[i].append(thing)

        new_data.sort(key = lambda x : x[0])
        new_data.insert(0, col_names)
        return new_data
    
    def cancel_reservation(self, rent_id, status = "C"):
        self._cursor.execute(f"begin\
                               modifystatus({rent_id}, '{status}');\
                               end;")

    def add_item_to_reservation(self, rent_id, item_id, item_quantity):
        try:
            price = self._cursor.execute(f"select priceperday from item where ID = '{item_id}'")
            add_price = price.fetchone()[0]
            self._cursor.execute(f"begin\
                                additemtorent('{rent_id}', '{item_id}', '{item_quantity}', '{add_price}');\
                                end;")
            return False
        except cx_Oracle.DatabaseError as e:
            return True
        except TypeError:
            return True

    def move_to_history(self, rent_id, return_date):
        self._cursor.execute(f"begin\
                               movetohist('{rent_id}','{return_date}');\
                               end;")

    def end_connection(self):
        self._cursor.close()
        self._connection.close()