import tkinter as tk
from tkinter import messagebox


class Passenger:
    def __init__(self, name="مسافر"):
        self.name = name
        self.inside_station = False

    def enter_station(self):
        self.inside_station = True

    def exit_station(self):
        self.inside_station = False


class Card:
    def __init__(self, balance=20000):
        self.balance = balance
        self.ticket_price = 5000

    def charge(self, amount):
        if amount > 0:
            self.balance += amount

    def can_pay(self):
        return self.balance >= self.ticket_price

    def pay(self):
        if self.can_pay():
            self.balance -= self.ticket_price
            return True
        return False


class Sensor:
    def __init__(self, name):
        self.name = name
        self.active = False

    def detect(self):
        self.active = True

    def clear(self):
        self.active = False


class Motor:
    def __init__(self):
        self.state = "closed"

    def open_gate(self):
        self.state = "open"

    def close_gate(self):
        self.state = "closed"


class Gate:
    def __init__(self):
        self.entry_sensor = Sensor("سنسور ورود")
        self.exit_sensor = Sensor("سنسور خروج")
        self.motor = Motor()
        self.last_message = "گیت بسته است"

    def check_card_and_open(self, card):
        self.entry_sensor.detect()

        if card.pay():
            self.motor.open_gate()
            self.last_message = "کارت تایید شد، گیت باز شد"
            return True

        self.motor.close_gate()
        self.last_message = "موجودی کارت کافی نیست"
        return False

    def passenger_passed(self):
        self.exit_sensor.detect()
        self.motor.close_gate()
        self.entry_sensor.clear()
        self.exit_sensor.clear()
        self.last_message = "مسافر عبور کرد، گیت بسته شد"


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("شبیه ساز گیت مترو")

        self.passenger = Passenger()
        self.card = Card()
        self.gate = Gate()

        self.make_gui()
        self.draw_gate()
        self.update_info()

    def make_gui(self):
        main = tk.Frame(self.root)
        main.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(main, width=520, height=310, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=2, pady=8)

        form = tk.Frame(main)
        form.grid(row=1, column=0, columnspan=2, pady=5)

        tk.Label(form, text="نام مسافر:").grid(row=0, column=0, padx=4)
        self.name_entry = tk.Entry(form, width=15)
        self.name_entry.insert(0, "Ali")
        self.name_entry.grid(row=0, column=1, padx=4)

        tk.Label(form, text="شارژ کارت:").grid(row=0, column=2, padx=4)
        self.charge_entry = tk.Entry(form, width=10)
        self.charge_entry.insert(0, "10000")
        self.charge_entry.grid(row=0, column=3, padx=4)

        buttons = tk.Frame(main)
        buttons.grid(row=2, column=0, columnspan=2, pady=6)

        tk.Button(buttons, text="شارژ کارت", width=14, command=self.charge_card).grid(row=0, column=0, padx=4)
        tk.Button(buttons, text="ورود مسافر", width=14, command=self.enter_passenger).grid(row=0, column=1, padx=4)
        tk.Button(buttons, text="خروج مسافر", width=14, command=self.exit_passenger).grid(row=0, column=2, padx=4)
        tk.Button(buttons, text="ریست", width=14, command=self.reset).grid(row=0, column=3, padx=4)

        self.info_label = tk.Label(main, text="", justify="right", font=("Arial", 10))
        self.info_label.grid(row=3, column=0, columnspan=2, pady=6)

    def draw_gate(self):
        self.canvas.delete("all")

        self.canvas.create_text(260, 20, text="Metro Gate Simulator", font=("Arial", 14, "bold"))

        self.canvas.create_rectangle(70, 90, 160, 240, fill="#dddddd")
        self.canvas.create_rectangle(360, 90, 450, 240, fill="#dddddd")

        self.canvas.create_text(115, 80, text="پایه گیت")
        self.canvas.create_text(405, 80, text="پایه گیت")

        if self.gate.motor.state == "open":
            self.canvas.create_line(160, 160, 235, 115, width=8, fill="green")
            self.canvas.create_line(360, 160, 285, 115, width=8, fill="green")
            self.canvas.create_text(260, 270, text="گیت باز است", fill="green", font=("Arial", 12, "bold"))
        else:
            self.canvas.create_line(160, 160, 250, 160, width=8, fill="red")
            self.canvas.create_line(360, 160, 270, 160, width=8, fill="red")
            self.canvas.create_text(260, 270, text="گیت بسته است", fill="red", font=("Arial", 12, "bold"))

        if self.gate.entry_sensor.active:
            self.canvas.create_oval(95, 105, 135, 145, fill="orange")
        else:
            self.canvas.create_oval(95, 105, 135, 145, fill="gray")

        if self.gate.exit_sensor.active:
            self.canvas.create_oval(385, 105, 425, 145, fill="orange")
        else:
            self.canvas.create_oval(385, 105, 425, 145, fill="gray")

        self.canvas.create_text(115, 155, text="Sensor In")
        self.canvas.create_text(405, 155, text="Sensor Out")

        if self.passenger.inside_station:
            self.canvas.create_oval(240, 175, 280, 215, fill="lightblue")
            self.canvas.create_text(260, 225, text=self.passenger.name)
        else:
            self.canvas.create_oval(35, 175, 75, 215, fill="lightblue")
            self.canvas.create_text(55, 225, text=self.passenger.name)

    def update_info(self):
        status = "داخل ایستگاه" if self.passenger.inside_station else "بیرون ایستگاه"
        text = "نام مسافر: %s\n" % self.passenger.name
        text += "موجودی کارت: %d تومان\n" % self.card.balance
        text += "وضعیت مسافر: %s\n" % status
        text += "وضعیت موتور: %s\n" % ("باز" if self.gate.motor.state == "open" else "بسته")
        text += "پیام: %s" % self.gate.last_message

        self.info_label.config(text=text)

    def charge_card(self):
        try:
            amount = int(self.charge_entry.get())
        except ValueError:
            messagebox.showerror("خطا", "مقدار شارژ باید عدد باشد")
            return

        self.card.charge(amount)
        self.gate.last_message = "کارت شارژ شد"
        self.update_info()
        self.draw_gate()

    def enter_passenger(self):
        name = self.name_entry.get().strip()
        if name:
            self.passenger.name = name

        if self.passenger.inside_station:
            self.gate.last_message = "مسافر قبلا وارد شده است"
            self.update_info()
            return

        allowed = self.gate.check_card_and_open(self.card)

        if allowed:
            self.draw_gate()
            self.update_info()
            self.root.after(800, self.finish_enter)
        else:
            self.draw_gate()
            self.update_info()

    def finish_enter(self):
        self.passenger.enter_station()
        self.gate.passenger_passed()
        self.draw_gate()
        self.update_info()

    def exit_passenger(self):
        if not self.passenger.inside_station:
            self.gate.last_message = "مسافر داخل ایستگاه نیست"
            self.update_info()
            return

        self.gate.entry_sensor.detect()
        self.gate.motor.open_gate()
        self.gate.last_message = "گیت برای خروج باز شد"
        self.draw_gate()
        self.update_info()
        self.root.after(800, self.finish_exit)

    def finish_exit(self):
        self.passenger.exit_station()
        self.gate.passenger_passed()
        self.draw_gate()
        self.update_info()

    def reset(self):
        self.passenger = Passenger()
        self.card = Card()
        self.gate = Gate()
        self.draw_gate()
        self.update_info()


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
