import tkinter as tk
from tkinter import messagebox


class Person:
    def __init__(self, source_floor, destination_floor):
        self.source_floor = source_floor
        self.destination_floor = destination_floor
        self.waiting_time = 0

    def direction(self):
        if self.destination_floor > self.source_floor:
            return "up"
        if self.destination_floor < self.source_floor:
            return "down"
        return "idle"


class Floor:
    def __init__(self, number):
        self.number = number
        self.waiting_people = []

    def add_person(self, person):
        self.waiting_people.append(person)

    def remove_person(self, person):
        if person in self.waiting_people:
            self.waiting_people.remove(person)


class Elevator:
    def __init__(self, capacity=15, current_floor=0):
        self.capacity = capacity
        self.current_floor = current_floor
        self.direction = "idle"
        self.passengers = []

    def passenger_count(self):
        return len(self.passengers)

    def is_full(self):
        return self.passenger_count() >= self.capacity

    def detect_direction(self, target_floor):
        if target_floor > self.current_floor:
            return "up"
        if target_floor < self.current_floor:
            return "down"
        return "idle"

    def move_one_floor_towards(self, target_floor):
        self.direction = self.detect_direction(target_floor)
        if self.direction == "up":
            self.current_floor += 1
        elif self.direction == "down":
            self.current_floor -= 1
        else:
            self.direction = "idle"
        return self.current_floor

    def board_person(self, person):
        if not self.is_full():
            self.passengers.append(person)
            return True
        return False

    def leave_passengers_at_current_floor(self):
        leaving = []
        for person in self.passengers:
            if person.destination_floor == self.current_floor:
                leaving.append(person)
        for person in leaving:
            self.passengers.remove(person)
        return len(leaving)


class Controller:
    def __init__(self, building, elevator, floor_travel_seconds=5):
        self.building = building
        self.elevator = elevator
        self.floor_travel_seconds = floor_travel_seconds
        self.requests = []
        self.current_request = None
        self.current_target = None
        self.moving = False
        self.elapsed_seconds = 0
        self.on_update = None

    def set_update_callback(self, callback):
        self.on_update = callback

    def add_request(self, source_floor, destination_floor):
        person = Person(source_floor, destination_floor)
        self.building.get_floor(source_floor).add_person(person)
        self.requests.append(person)
        self.calculate_waiting_time(person)
        self.update_gui()
        return person

    def calculate_waiting_time(self, person):
        position = self.elevator.current_floor
        pending_targets = []

        if self.current_target is not None:
            pending_targets.append(self.current_target)

        for request in self.requests:
            if request is person:
                break
            pending_targets.append(request.source_floor)
            pending_targets.append(request.destination_floor)

        simulated_seconds = 0
        for target in pending_targets:
            simulated_seconds += abs(target - position) * self.floor_travel_seconds
            position = target

        simulated_seconds += abs(person.source_floor - position) * self.floor_travel_seconds
        person.waiting_time = simulated_seconds
        return simulated_seconds

    def start(self):
        if not self.moving and self.requests:
            self.prepare_next_request()

    def prepare_next_request(self):
        if not self.requests:
            self.current_request = None
            self.current_target = None
            self.elevator.direction = "idle"
            self.moving = False
            self.update_gui()
            return

        self.current_request = self.requests[0]
        if self.current_request not in self.elevator.passengers:
            self.current_target = self.current_request.source_floor
        else:
            self.current_target = self.current_request.destination_floor
        self.moving = True
        self.update_gui()

    def step(self):
        if not self.moving:
            return

        if self.current_target is None:
            self.prepare_next_request()
            return

        if self.elevator.current_floor != self.current_target:
            self.elevator.move_one_floor_towards(self.current_target)
            self.elapsed_seconds += self.floor_travel_seconds
            self.update_waiting_times()
            self.update_gui()
            return

        self.handle_arrival()

    def handle_arrival(self):
        self.elevator.leave_passengers_at_current_floor()

        if self.current_request is None:
            self.prepare_next_request()
            return

        if self.elevator.current_floor == self.current_request.source_floor and self.current_request not in self.elevator.passengers:
            boarded = self.elevator.board_person(self.current_request)
            if boarded:
                self.building.get_floor(self.current_request.source_floor).remove_person(self.current_request)
                self.current_target = self.current_request.destination_floor
            else:
                messagebox.showwarning("ظرفیت آسانسور", "ظرفیت آسانسور تکمیل است.")
                self.current_target = self.current_request.source_floor
            self.update_gui()
            return

        if self.elevator.current_floor == self.current_request.destination_floor:
            if self.current_request in self.requests:
                self.requests.remove(self.current_request)
            self.current_request = None
            self.current_target = None
            self.prepare_next_request()
            return

        self.prepare_next_request()

    def update_waiting_times(self):
        for request in self.requests:
            if request not in self.elevator.passengers:
                request.waiting_time += self.floor_travel_seconds

    def update_gui(self):
        if self.on_update:
            self.on_update()


class Building:
    def __init__(self, min_floor=0, max_floor=107):
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.floors = []
        for number in range(self.min_floor, self.max_floor + 1):
            self.floors.append(Floor(number))

    def get_floor(self, floor_number):
        for floor in self.floors:
            if floor.number == floor_number:
                return floor
        raise ValueError("طبقه نامعتبر است.")

    def is_valid_floor(self, floor_number):
        return self.min_floor <= floor_number <= self.max_floor


class SmartElevatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Elevator")
        self.building = Building(0, 107)
        self.elevator = Elevator(capacity=15, current_floor=0)
        self.controller = Controller(self.building, self.elevator, floor_travel_seconds=5)
        self.controller.set_update_callback(self.refresh_gui)
        self.after_id = None

        self.create_widgets()
        self.refresh_gui()

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        list_frame = tk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.floor_list = tk.Listbox(list_frame, width=35, height=30, yscrollcommand=scrollbar.set)
        self.floor_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.floor_list.yview)

        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        tk.Label(control_frame, text="طبقه مبدا").pack(anchor="w")
        self.source_entry = tk.Entry(control_frame)
        self.source_entry.pack(fill=tk.X)

        tk.Label(control_frame, text="طبقه مقصد").pack(anchor="w", pady=(10, 0))
        self.destination_entry = tk.Entry(control_frame)
        self.destination_entry.pack(fill=tk.X)

        self.request_button = tk.Button(control_frame, text="ثبت درخواست", command=self.add_request)
        self.request_button.pack(fill=tk.X, pady=10)

        self.start_button = tk.Button(control_frame, text="شروع حرکت", command=self.start_elevator)
        self.start_button.pack(fill=tk.X)

        self.current_floor_label = tk.Label(control_frame, text="")
        self.current_floor_label.pack(anchor="w", pady=(20, 0))

        self.direction_label = tk.Label(control_frame, text="")
        self.direction_label.pack(anchor="w")

        self.passenger_label = tk.Label(control_frame, text="")
        self.passenger_label.pack(anchor="w")

        self.waiting_label = tk.Label(control_frame, text="")
        self.waiting_label.pack(anchor="w")

        self.requests_label = tk.Label(control_frame, text="", justify="left")
        self.requests_label.pack(anchor="w", pady=(15, 0))

    def add_request(self):
        try:
            source_floor = int(self.source_entry.get())
            destination_floor = int(self.destination_entry.get())
        except ValueError:
            messagebox.showerror("خطا", "طبقه مبدا و مقصد باید عدد باشند.")
            return

        if not self.building.is_valid_floor(source_floor) or not self.building.is_valid_floor(destination_floor):
            messagebox.showerror("خطا", "طبقه باید بین 0 تا 107 باشد.")
            return

        if source_floor == destination_floor:
            messagebox.showerror("خطا", "طبقه مبدا و مقصد نباید یکسان باشند.")
            return

        person = self.controller.add_request(source_floor, destination_floor)
        messagebox.showinfo("ثبت شد", f"درخواست ثبت شد. زمان انتظار محاسبه‌شده: {person.waiting_time} ثانیه")
        self.source_entry.delete(0, tk.END)
        self.destination_entry.delete(0, tk.END)
        self.start_elevator()

    def start_elevator(self):
        self.controller.start()
        if self.after_id is None:
            self.run_step()

    def run_step(self):
        if self.controller.moving:
            self.controller.step()
            self.after_id = self.root.after(1000, self.run_step)
        else:
            self.after_id = None

    def refresh_gui(self):
        self.floor_list.delete(0, tk.END)
        for floor_number in range(self.building.max_floor, self.building.min_floor - 1, -1):
            text = f"طبقه {floor_number}"
            if floor_number == self.elevator.current_floor:
                text += "  <-- آسانسور"
            floor = self.building.get_floor(floor_number)
            if floor.waiting_people:
                text += f" | منتظر: {len(floor.waiting_people)}"
            self.floor_list.insert(tk.END, text)

        elevator_index = self.building.max_floor - self.elevator.current_floor
        self.floor_list.selection_clear(0, tk.END)
        self.floor_list.selection_set(elevator_index)
        self.floor_list.see(elevator_index)

        self.current_floor_label.config(text=f"طبقه فعلی: {self.elevator.current_floor}")
        self.direction_label.config(text=f"جهت حرکت: {self.elevator.direction}")
        self.passenger_label.config(text=f"تعداد مسافران: {self.elevator.passenger_count()} از {self.elevator.capacity}")

        if self.controller.current_request:
            self.waiting_label.config(text=f"زمان انتظار درخواست جاری: {self.controller.current_request.waiting_time} ثانیه")
        else:
            self.waiting_label.config(text="زمان انتظار درخواست جاری: -")

        request_lines = ["درخواست‌ها:"]
        if not self.controller.requests:
            request_lines.append("درخواستی وجود ندارد.")
        else:
            for index, person in enumerate(self.controller.requests, start=1):
                request_lines.append(
                    f"{index}) مبدا: {person.source_floor}، مقصد: {person.destination_floor}، انتظار: {person.waiting_time} ثانیه"
                )
        self.requests_label.config(text="\n".join(request_lines))


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartElevatorApp(root)
    root.mainloop()
