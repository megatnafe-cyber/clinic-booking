import datetime
import requests
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

SUPABASE_URL = "https://dfgokopfpzoveubjxfes.supabase.co/rest/v1/appointments"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRmZ29rb3BmcHpvdmV1Ymp4ZmVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTU2MjA1MTQsImV4cCI6MjExMTE5NjUxNH0.VJqZ0dmDI9xauYGEbLZHLzm_8ec_CRRIRnXCImMqsPc"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + SUPABASE_KEY,
    "Content-Type": "application/json",
}

DOCTORS = [
    "Dr. Sufyan Suleiman (Internal Medicine)",
    "Dr. Hiba Al-Shafie (General Surgery)",
    "Dr. Imad Rashad (Psychiatry)",
    "Dr. Khalid Al-Talib (Cardiology & Catheterization)",
    "Dr. Mohammed Idris (General Practice)",
    "Dr. Ibtisam Shabo (Obstetrics & Gynecology)",
]

SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00",
    "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
]

BLUE = (0.25, 0.45, 0.65, 1)
LIGHT_GREY = (0.85, 0.86, 0.88, 1)


def make_button(text, callback, color=BLUE, height=50):
    btn = Button(text=text, size_hint_y=None, height=height, background_color=color)
    btn.bind(on_release=callback)
    return btn


def show_message(title, text):
    popup = Popup(title=title, content=Label(text=text), size_hint=(0.8, 0.3))
    popup.open()


def get_booked_times(doctor, date):
    params = {"doctor": "eq." + doctor, "appt_date": "eq." + date, "select": "appt_time"}
    r = requests.get(SUPABASE_URL, headers=HEADERS, params=params, timeout=10)
    r.raise_for_status()
    return [row["appt_time"] for row in r.json()]


def book_slot(doctor, date, time, name):
    data = {"doctor": doctor, "appt_date": date, "appt_time": time, "patient_name": name}
    r = requests.post(SUPABASE_URL, headers=HEADERS, json=data, timeout=10)
    return r.status_code


def get_patient_bookings(name):
    params = {"patient_name": "eq." + name, "order": "appt_date.asc,appt_time.asc"}
    r = requests.get(SUPABASE_URL, headers=HEADERS, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def cancel_booking(booking_id, name):
    params = {"id": "eq." + str(booking_id), "patient_name": "eq." + name}
    r = requests.delete(SUPABASE_URL, headers=HEADERS, params=params, timeout=10)
    r.raise_for_status()


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation="vertical", padding=40, spacing=20)
        box.add_widget(Label(text="Clinic Booking", font_size=32, color=BLUE))
        box.add_widget(make_button("Book an appointment", lambda *a: self.go("book"), height=70))
        box.add_widget(make_button("My bookings", lambda *a: self.go("bookings"), height=70))
        self.add_widget(box)

    def go(self, screen_name):
        self.manager.current = screen_name


class BookScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.doctor_spinner = Spinner(text=DOCTORS[0], values=DOCTORS, size_hint_y=None, height=50)
        self.date_input = TextInput(
            text=datetime.date.today().isoformat(), multiline=False,
            size_hint_y=None, height=50
        )
        layout.add_widget(self.doctor_spinner)
        layout.add_widget(self.date_input)
        layout.add_widget(make_button("Show times", self.show_slots))
        layout.add_widget(Label(text="Grey times are already booked", size_hint_y=None, height=30))

        self.grid = GridLayout(cols=3, spacing=8, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)

        layout.add_widget(make_button("Back", self.go_back, LIGHT_GREY))
        self.add_widget(layout)

    def go_back(self, *args):
        self.manager.current = "menu"

    def show_slots(self, *args):
        doctor = self.doctor_spinner.text
        date = self.date_input.text.strip()

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            show_message("Wrong date", "Please write the date like 2026-12-01")
            return

        if date < datetime.date.today().isoformat():
            show_message("Wrong date", "This date has already passed")
            return

        try:
            booked = get_booked_times(doctor, date)
        except requests.RequestException:
            show_message("No internet", "Please check your connection and try again")
            return

        self.grid.clear_widgets()
        for slot in SLOTS:
            if slot in booked:
                btn = Button(text=slot, size_hint_y=None, height=50, background_color=LIGHT_GREY)
                btn.disabled = True
            else:
                btn = make_button(slot, lambda *a, t=slot: self.ask_name(doctor, date, t))
            self.grid.add_widget(btn)

    def ask_name(self, doctor, date, time):
        name_input = TextInput(hint_text="Patient name", multiline=False, size_hint_y=None, height=50)
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        box.add_widget(name_input)
        box.add_widget(make_button(
            "Confirm",
            lambda *a: self.confirm(popup, name_input, doctor, date, time)
        ))
        popup = Popup(title="Book at " + time, content=box, size_hint=(0.9, 0.4))
        popup.open()

    def confirm(self, popup, name_input, doctor, date, time):
        name = name_input.text.strip()
        if not name:
            show_message("Missing name", "Please write the patient name")
            return

        try:
            status = book_slot(doctor, date, time, name)
        except requests.RequestException:
            show_message("No internet", "Please check your connection and try again")
            return

        popup.dismiss()
        if status == 201:
            show_message("Done", "Your appointment is booked")
        elif status == 409:
            show_message("Sorry", "This time was just booked by someone else")
        else:
            show_message("Error", "Something went wrong, please try again")
        self.show_slots()


class BookingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.name_input = TextInput(hint_text="Your name", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.name_input)
        layout.add_widget(make_button("Find my bookings", self.search))

        self.results = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.results.bind(minimum_height=self.results.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.results)
        layout.add_widget(scroll)

        layout.add_widget(make_button("Back", self.go_back, LIGHT_GREY))
        self.add_widget(layout)

    def go_back(self, *args):
        self.manager.current = "menu"

    def search(self, *args):
        name = self.name_input.text.strip()
        if not name:
            return

        try:
            bookings = get_patient_bookings(name)
        except requests.RequestException:
            show_message("No internet", "Please check your connection and try again")
            return

        self.results.clear_widgets()
        if not bookings:
            self.results.add_widget(Label(text="No bookings found", size_hint_y=None, height=40))
            return

        for b in bookings:
            doctor_short = b["doctor"].split(" (")[0]
            text = "Cancel: {} {} {}".format(b["appt_date"], b["appt_time"], doctor_short)
            self.results.add_widget(
                make_button(text, lambda *a, bid=b["id"]: self.cancel(bid, name), height=60)
            )

    def cancel(self, booking_id, name):
        try:
            cancel_booking(booking_id, name)
        except requests.RequestException:
            show_message("No internet", "Please check your connection and try again")
            return
        show_message("Cancelled", "Your appointment was cancelled")
        self.search()


class ClinicBookingApp(App):
    def build(self):
        Window.clearcolor = (0.96, 0.97, 0.98, 1)
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(BookScreen(name="book"))
        sm.add_widget(BookingsScreen(name="bookings"))
        return sm


if __name__ == "__main__":
    ClinicBookingApp().run()
