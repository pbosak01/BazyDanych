import PySimpleGUI as sg
from dbmanager import DBManager


class GUI:
    def __init__(self) -> None:
        self.dbm = DBManager()
        self.clients = self.dbm.select_from_table('client')[1:]
        self.clients.sort(key = lambda x : x[0])
        self.login_text = "Użytkownik: Niezalogowano"

        self.cur_usr = None # will be (usr_id, name, city)
        sg.theme('DarkAmber')   # Add a touch of color
        # All the stuff inside your window.
        self.layout = [
                    [sg.Column([[sg.Text(self.login_text, key="-LOGIN_INFO-"),sg.Button("Wyloguj", key="-LOGOUT-", visible=False)]], justification='center')],
                    [sg.Column([[sg.Combo(values= self.clients, size=(20, 1), enable_events=True, key='-USER-'), sg.Button('Zaloguj', key='-LOGIN-')]], justification='center', key='-CLIENT_COLUMN-')],
                    [sg.Column([[sg.InputText('YYYY-MM-DD', key='-START_DATE-', size=(20, 1)), sg.InputText('YYYY-MM-DD', key='-END_DATE-', size=(20, 1)), sg.Button('Dodaj rezerwacje', key='-ADD_RESERVATION-')]], justification='center', key='-ADD_COLUMN-', visible=False)],
                    [sg.Column([[sg.Button('Szukaj dostępnych narzędzi', key='-FIND_AVAILABLE_ITEMS-', size=(37, 1))]],justification='center', key='-FIND_ITEMS_COLUMN-', visible=False)],
                    [sg.Column([[sg.Button('Pokaz moje rezerwacje', key='-SHOW_RESERVATION-')]], justification='center', key='-SHOW_RESERVATION_COLUMN-', visible=False)],
                    [sg.Column([[sg.Text("Numer rezerwacji:"), sg.InputText(size=(2, 1), key='-RESERVATION_ID-'), sg.Button('Anuluj rezerwacje', key='-CANCEL_RESERVATION-')]], justification='center', key='-CANCEL_RESERVATION_COLUMN-', visible=False)],
                    [sg.Column([[sg.Text("Numer rezerwacji:"), sg.InputText(size=(2, 1), key='-RESERVATION_ID_ADD-'), sg.Text("Numer przedmiotu:"), sg.InputText(size=(2, 1), key='-RESERVATION_ITEM_ID-'), sg.Text("Ilość przedmiotu:"), sg.InputText(size=(2, 1), key='-RESERVATION_ITEM_QUANTITY-'), sg.Button("Dodaj do rezerwacji", key="-ADD_TO_RESERVATION-")]], visible=False, key='-ADD_ITEM_RESERVATION_COLUMN-')],
                    
                    [sg.Column([[sg.Text('Podaj tabele którą chcesz wyświetlić:'), sg.Combo(['client', 'rent', 'renthist', 'rentitems', 'item'], enable_events=True, key='table_name'), sg.Button('Ok', key='-CHOOSE_TABLE-')]], justification='center', key='-SHOW_TABLES-')]
                    ]
        # Create the Window
        self.window = sg.Window('Window Title', self.layout, size=(600, 600))
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = self.window.read()
            print(event)
            if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
                self.dbm.end_connection()
                break
            elif event == '-CHOOSE_TABLE-':
                data = self.dbm.select_from_table(values['table_name'])
                data[1:].sort(key=lambda x : x[0])
                sg.popup_scrolled(*data, title=values['table_name'])

            elif event == '-LOGIN-':
                if not values["-USER-"]:
                    continue
                self.window["-LOGIN_INFO-"].update(f"Użytkownik: {values['-USER-'][1]}, usr_id: {values['-USER-'][0]}")
                self.cur_usr = values['-USER-']
                self.window["-CLIENT_COLUMN-"].update(visible=False)
                self.window["-LOGOUT-"].update(visible=True)
                self.window["-ADD_COLUMN-"].update(visible=True)
                self.window["-FIND_ITEMS_COLUMN-"].update(visible=True)
                self.window["-SHOW_RESERVATION_COLUMN-"].update(visible=True)
                self.window["-CANCEL_RESERVATION_COLUMN-"].update(visible=True)
                self.window["-FIND_ITEMS_COLUMN-"].update(visible=True)
                self.window["-ADD_ITEM_RESERVATION_COLUMN-"].update(visible=True)

            elif event == '-LOGOUT-':
                self.window["-LOGIN_INFO-"].update(self.login_text)
                self.cur_usr = None
                self.window["-CLIENT_COLUMN-"].update(visible=True)
                self.window["-LOGOUT-"].update(visible=False)
                self.window["-ADD_COLUMN-"].update(visible=False)
                self.window["-FIND_ITEMS_COLUMN-"].update(visible=False)
                self.window["-SHOW_RESERVATION_COLUMN-"].update(visible=False)
                self.window["-CANCEL_RESERVATION_COLUMN-"].update(visible=False)
                self.window["-FIND_ITEMS_COLUMN-"].update(visible=False)
                self.window["-ADD_ITEM_RESERVATION_COLUMN-"].update(visible=False)

            elif event == '-ADD_RESERVATION-':
                usr_id = values["-USER-"][0]
                begin_date = values["-START_DATE-"]
                end_date = values["-END_DATE-"]
                self.dbm.add_rent(usr_id, begin_date, end_date)

            elif event == '-FIND_AVAILABLE_ITEMS-':
                begin_date = values["-START_DATE-"]
                end_date = values["-END_DATE-"]
                data = self.dbm.get_available_items(begin_date, end_date)
                sg.popup_scrolled(*data, title="Dostępne przedmioty", non_blocking=True)
            elif event == '-SHOW_RESERVATION-':
                usr_id = values["-USER-"][0]
                data = self.dbm.show_my_reservations(usr_id)
                sg.popup_scrolled(*data, title="Moje rezerwacje", non_blocking=True)
            elif event == '-CANCEL_RESERVATION-':
                rent_id = values["-RESERVATION_ID-"]
                self.dbm.cancel_reservation(rent_id)
                print("theoritically cancelled")
            elif event == '-ADD_TO_RESERVATION-':
                rent_id = values["-RESERVATION_ID_ADD-"]
                item_id = values["-RESERVATION_ITEM_ID-"]
                item_quantity = values["-RESERVATION_ITEM_QUANTITY-"]
                self.dbm.add_item_to_reservation(rent_id, item_id, item_quantity)
        self.window.close()


if __name__ == "__main__":
    gui = GUI()