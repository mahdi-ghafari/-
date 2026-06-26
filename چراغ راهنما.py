import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque


class Car:
    counter = 1

    def __init__(self, lane_name):
        self.id = Car.counter
        Car.counter += 1
        self.lane_name = lane_name

    def __str__(self):
        return f"Car {self.id}"


class TrafficLight:
    def __init__(self, lane_name):
        self.lane_name = lane_name
        self.state = "RED"
        self.remaining_time = 0

    def set_green(self, seconds):
        self.state = "GREEN"
        self.remaining_time = seconds

    def set_red(self):
        self.state = "RED"
        self.remaining_time = 0

    def tick(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1


class Lane:
    def __init__(self, name):
        self.name = name
        self.cars = deque()
        self.light = TrafficLight(name)

    def add_car(self):
        car = Car(self.name)
        self.cars.append(car)
        return car

    def pass_car(self):
        if self.cars:
            return self.cars.popleft()
        return None

    def car_count(self):
        return len(self.cars)


class Intersection:
    def __init__(self):
        self.lanes = {
            "North": Lane("North"),
            "East": Lane("East"),
            "South": Lane("South"),
            "West": Lane("West"),
        }

    def get_lane(self, lane_name):
        return self.lanes.get(lane_name)

    def all_lanes(self):
        return list(self.lanes.values())

    def reset_lights(self):
        for lane in self.all_lanes():
            lane.light.set_red()


class Controller:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Traffic Light Simulator")
        self.root.geometry("760x560")
        self.root.resizable(False, False)

        self.intersection = Intersection()
        self.running = False
        self.active_lane = None
        self.base_green_time = 5
        self.max_green_time = 15
        self.car_pass_interval = 2
        self.pass_timer = 0

        self.lane_order = ["North", "East", "South", "West"]
        self.last_lane_index = -1

        self.queue_labels = {}
        self.light_labels = {}
        self.canvas_cars = {}

        self.build_gui()
        self.refresh_screen()

    def build_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        control_frame = ttk.LabelFrame(main_frame, text="Vehicle Entry", padding=10)
        control_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(control_frame, text="Lane:").pack(anchor="w")
        self.lane_var = tk.StringVar(value="North")
        lane_box = ttk.Combobox(
            control_frame,
            textvariable=self.lane_var,
            values=self.lane_order,
            state="readonly",
            width=18,
        )
        lane_box.pack(anchor="w", pady=(4, 10))

        ttk.Button(control_frame, text="Add Car", command=self.add_car).pack(fill="x", pady=4)
        ttk.Button(control_frame, text="Start", command=self.start).pack(fill="x", pady=4)
        ttk.Button(control_frame, text="Stop", command=self.stop).pack(fill="x", pady=4)

        ttk.Separator(control_frame, orient="horizontal").pack(fill="x", pady=12)

        ttk.Label(control_frame, text="Queues").pack(anchor="w", pady=(0, 6))
        for lane_name in self.lane_order:
            label = ttk.Label(control_frame, text=f"{lane_name}: 0 cars")
            label.pack(anchor="w", pady=2)
            self.queue_labels[lane_name] = label

        ttk.Separator(control_frame, orient="horizontal").pack(fill="x", pady=12)
        self.status_label = ttk.Label(control_frame, text="Status: Stopped")
        self.status_label.pack(anchor="w")

        display_frame = ttk.LabelFrame(main_frame, text="Intersection", padding=10)
        display_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(display_frame, width=520, height=500, bg="white")
        self.canvas.pack()
        self.draw_intersection()

    def draw_intersection(self):
        self.canvas.delete("all")

        self.canvas.create_rectangle(215, 0, 305, 500, fill="#dddddd", outline="")
        self.canvas.create_rectangle(0, 205, 520, 295, fill="#dddddd", outline="")
        self.canvas.create_rectangle(215, 205, 305, 295, fill="#bbbbbb", outline="")

        self.canvas.create_text(260, 25, text="North", font=("Arial", 12, "bold"))
        self.canvas.create_text(485, 250, text="East", font=("Arial", 12, "bold"))
        self.canvas.create_text(260, 475, text="South", font=("Arial", 12, "bold"))
        self.canvas.create_text(35, 250, text="West", font=("Arial", 12, "bold"))

        positions = {
            "North": (330, 150),
            "East": (365, 315),
            "South": (170, 350),
            "West": (155, 170),
        }

        for lane_name, (x, y) in positions.items():
            circle = self.canvas.create_oval(x, y, x + 30, y + 30, fill="red", outline="black")
            text = self.canvas.create_text(x + 15, y + 45, text="RED", font=("Arial", 9))
            self.light_labels[lane_name] = (circle, text)

    def add_car(self):
        lane_name = self.lane_var.get()
        lane = self.intersection.get_lane(lane_name)
        if lane:
            lane.add_car()
            self.refresh_screen()

    def start(self):
        if not self.running:
            self.running = True
            self.status_label.config(text="Status: Running")
            self.choose_next_lane()
            self.run_cycle()

    def stop(self):
        self.running = False
        self.status_label.config(text="Status: Stopped")

    def calculate_green_time(self, lane):
        queue_size = lane.car_count()
        if queue_size == 0:
            return self.base_green_time
        green_time = self.base_green_time + queue_size
        return min(green_time, self.max_green_time)

    def choose_next_lane(self):
        self.intersection.reset_lights()

        best_lane = None
        biggest_queue = -1

        for step in range(1, len(self.lane_order) + 1):
            index = (self.last_lane_index + step) % len(self.lane_order)
            lane = self.intersection.get_lane(self.lane_order[index])
            if lane.car_count() > biggest_queue:
                biggest_queue = lane.car_count()
                best_lane = lane
                self.last_lane_index = index

        if best_lane is None:
            best_lane = self.intersection.get_lane(self.lane_order[0])
            self.last_lane_index = 0

        self.active_lane = best_lane
        green_time = self.calculate_green_time(best_lane)
        best_lane.light.set_green(green_time)
        self.pass_timer = 0
        self.refresh_screen()

    def run_cycle(self):
        if not self.running:
            return

        if self.active_lane is None:
            self.choose_next_lane()

        active_light = self.active_lane.light

        if active_light.remaining_time <= 0:
            self.choose_next_lane()
        else:
            active_light.tick()
            self.pass_timer += 1
            if self.pass_timer >= self.car_pass_interval:
                self.active_lane.pass_car()
                self.pass_timer = 0
            self.refresh_screen()

        self.root.after(1000, self.run_cycle)

    def refresh_screen(self):
        for lane in self.intersection.all_lanes():
            self.queue_labels[lane.name].config(text=f"{lane.name}: {lane.car_count()} cars")

            circle, text = self.light_labels[lane.name]
            if lane.light.state == "GREEN":
                self.canvas.itemconfig(circle, fill="green")
                self.canvas.itemconfig(text, text=f"GREEN {lane.light.remaining_time}")
            else:
                self.canvas.itemconfig(circle, fill="red")
                self.canvas.itemconfig(text, text="RED")

        self.draw_cars()

    def draw_cars(self):
        self.canvas.delete("car")
        start_points = {
            "North": (245, 55, 0, 32),
            "East": (430, 240, -32, 0),
            "South": (275, 415, 0, -32),
            "West": (55, 260, 32, 0),
        }

        for lane in self.intersection.all_lanes():
            x, y, dx, dy = start_points[lane.name]
            for index, car in enumerate(list(lane.cars)[:10]):
                car_x = x + dx * index
                car_y = y + dy * index
                self.canvas.create_rectangle(
                    car_x,
                    car_y,
                    car_x + 24,
                    car_y + 16,
                    fill="#4477aa",
                    outline="black",
                    tags="car",
                )
                self.canvas.create_text(
                    car_x + 12,
                    car_y + 8,
                    text=str(car.id),
                    fill="white",
                    font=("Arial", 8),
                    tags="car",
                )


def main():
    root = tk.Tk()
    Controller(root)
    root.mainloop()


if __name__ == "__main__":
    main()
