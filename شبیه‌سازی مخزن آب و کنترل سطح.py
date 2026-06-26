import tkinter as tk
from tkinter import messagebox


class Tank:
    def __init__(self, max_height=507.0, start_height=80.0, out_flow=2.0):
        self.max_height = max_height
        self.height = start_height
        self.out_flow = out_flow

    def update(self, input_flow, dt):
        self.height += (input_flow - self.out_flow) * dt

        if self.height < 0:
            self.height = 0
        if self.height > self.max_height:
            self.height = self.max_height

        return self.height

    def reset(self):
        self.height = 80.0


class Pump:
    def __init__(self, max_flow=12.0):
        self.max_flow = max_flow
        self.flow = 0.0

    def set_flow(self, value):
        if value < 0:
            value = 0
        if value > self.max_flow:
            value = self.max_flow

        self.flow = value
        return self.flow


class Sensor:
    def __init__(self, tank):
        self.tank = tank

    def read_height(self):
        return self.tank.height


class Controller:
    def __init__(self, mode="On-Off", set_point=250.0):
        self.mode = mode
        self.set_point = set_point

        self.kp = 0.12
        self.ki = 0.015
        self.kd = 0.04

        self.sum_error = 0.0
        self.old_error = 0.0

    def reset(self):
        self.sum_error = 0.0
        self.old_error = 0.0

    def on_off(self, height, max_flow):
        low_limit = self.set_point - 15
        high_limit = self.set_point + 15

        if height < low_limit:
            return max_flow

        if height > high_limit:
            return 0.0

        if height < self.set_point:
            return max_flow * 0.6

        return 0.0

    def pid(self, height, max_flow, dt):
        error = self.set_point - height

        self.sum_error += error * dt
        diff_error = (error - self.old_error) / dt

        output = self.kp * error + self.ki * self.sum_error + self.kd * diff_error
        self.old_error = error

        if output < 0:
            output = 0
        if output > max_flow:
            output = max_flow

        return output

    def calculate(self, height, max_flow, dt):
        if self.mode == "PID":
            return self.pid(height, max_flow, dt)

        return self.on_off(height, max_flow)


class Simulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Tank 507 Simulation")

        self.tank = Tank()
        self.pump = Pump()
        self.sensor = Sensor(self.tank)
        self.controller = Controller()

        self.dt = 1
        self.time = 0
        self.running = False
        self.levels = []

        self.make_window()
        self.draw_tank()
        self.draw_graph()

    def make_window(self):
        base = tk.Frame(self.root)
        base.pack(padx=10, pady=10)

        left = tk.Frame(base)
        left.grid(row=0, column=0, padx=10)

        right = tk.Frame(base)
        right.grid(row=0, column=1, padx=10)

        tk.Label(left, text="مخزن آب 507", font=("Arial", 12, "bold")).pack()

        self.tank_canvas = tk.Canvas(left, width=260, height=420, bg="white")
        self.tank_canvas.pack(pady=5)

        self.graph_canvas = tk.Canvas(right, width=620, height=320, bg="white")
        self.graph_canvas.pack()

        form = tk.Frame(right)
        form.pack(pady=8)

        tk.Label(form, text="دبی ورودی:").grid(row=0, column=0)
        self.flow_entry = tk.Entry(form, width=10)
        self.flow_entry.insert(0, "8")
        self.flow_entry.grid(row=0, column=1, padx=4)

        tk.Label(form, text="ارتفاع مطلوب:").grid(row=0, column=2)
        self.set_entry = tk.Entry(form, width=10)
        self.set_entry.insert(0, "250")
        self.set_entry.grid(row=0, column=3, padx=4)

        tk.Label(form, text="نوع کنترل:").grid(row=0, column=4)
        self.mode_value = tk.StringVar(value="On-Off")
        tk.OptionMenu(form, self.mode_value, "Manual", "On-Off", "PID").grid(row=0, column=5, padx=4)

        buttons = tk.Frame(right)
        buttons.pack(pady=5)

        tk.Button(buttons, text="شروع", width=12, command=self.start).grid(row=0, column=0, padx=4)
        tk.Button(buttons, text="توقف", width=12, command=self.stop).grid(row=0, column=1, padx=4)
        tk.Button(buttons, text="ریست", width=12, command=self.reset).grid(row=0, column=2, padx=4)
        tk.Button(buttons, text="مقایسه کنترلرها", width=16, command=self.compare).grid(row=0, column=3, padx=4)

        self.info = tk.Label(right, text="آماده اجرا", font=("Arial", 10))
        self.info.pack(pady=5)

        self.compare_info = tk.Label(right, text="", justify="right", font=("Arial", 10))
        self.compare_info.pack(pady=5)

    def get_set_point(self):
        try:
            sp = float(self.set_entry.get())
        except ValueError:
            sp = 250.0

        if sp < 0:
            sp = 0
        if sp > self.tank.max_height:
            sp = self.tank.max_height

        return sp

    def get_manual_flow(self):
        try:
            return float(self.flow_entry.get())
        except ValueError:
            messagebox.showerror("خطا", "دبی ورودی باید عدد باشد")
            return 0.0

    def draw_tank(self):
        self.tank_canvas.delete("all")

        x1 = 85
        y1 = 40
        x2 = 175
        y2 = 360

        self.tank_canvas.create_rectangle(x1, y1, x2, y2, width=3)
        self.tank_canvas.create_text(130, 20, text="Tank 507")

        ratio = self.tank.height / self.tank.max_height
        water_y = y2 - (y2 - y1) * ratio

        self.tank_canvas.create_rectangle(x1 + 3, water_y, x2 - 3, y2 - 3,
                                          fill="lightblue", outline="lightblue")

        sp = self.get_set_point()
        sp_y = y2 - (y2 - y1) * (sp / self.tank.max_height)

        self.tank_canvas.create_line(x1 - 20, sp_y, x2 + 20, sp_y, fill="red", dash=(4, 3))
        self.tank_canvas.create_text(x2 + 42, sp_y, text="هدف")
        self.tank_canvas.create_text(130, 385, text="ارتفاع: %.1f" % self.tank.height)

    def draw_graph(self):
        self.graph_canvas.delete("all")

        self.graph_canvas.create_line(40, 280, 600, 280)
        self.graph_canvas.create_line(40, 20, 40, 280)
        self.graph_canvas.create_text(310, 300, text="زمان")
        self.graph_canvas.create_text(20, 150, text="ارتفاع", angle=90)
        self.graph_canvas.create_text(310, 12, text="نمودار سطح آب")

        for i in range(6):
            y = 280 - i * 52
            value = int(i * self.tank.max_height / 5)
            self.graph_canvas.create_line(36, y, 44, y)
            self.graph_canvas.create_text(20, y, text=str(value))

        sp_y = 280 - (self.get_set_point() / self.tank.max_height) * 260
        self.graph_canvas.create_line(40, sp_y, 600, sp_y, fill="red", dash=(4, 3))

        if len(self.levels) < 2:
            return

        show = self.levels[-100:]
        points = []

        for i, h in enumerate(show):
            x = 40 + i * (560 / 100)
            y = 280 - (h / self.tank.max_height) * 260
            points.append((x, y))

        for i in range(len(points) - 1):
            self.graph_canvas.create_line(points[i][0], points[i][1],
                                          points[i + 1][0], points[i + 1][1],
                                          fill="blue", width=2)

    def start(self):
        self.running = True
        self.controller.reset()
        self.run()

    def stop(self):
        self.running = False

    def reset(self):
        self.running = False
        self.time = 0
        self.levels = []
        self.tank.reset()
        self.pump.set_flow(0)
        self.controller.reset()
        self.compare_info.config(text="")
        self.info.config(text="برنامه ریست شد")
        self.draw_tank()
        self.draw_graph()

    def run(self):
        if not self.running:
            return

        self.controller.mode = self.mode_value.get()
        self.controller.set_point = self.get_set_point()

        height = self.sensor.read_height()

        if self.mode_value.get() == "Manual":
            flow = self.get_manual_flow()
        else:
            flow = self.controller.calculate(height, self.pump.max_flow, self.dt)

        flow = self.pump.set_flow(flow)
        new_height = self.tank.update(flow, self.dt)

        self.time += self.dt
        self.levels.append(new_height)

        self.info.config(
            text="زمان: %d ثانیه   دبی ورودی: %.2f   ارتفاع آب: %.2f   کنترل: %s"
            % (self.time, flow, new_height, self.mode_value.get())
        )

        self.draw_tank()
        self.draw_graph()

        self.root.after(200, self.run)

    def run_test(self, mode):
        tank = Tank()
        pump = Pump()
        sensor = Sensor(tank)
        controller = Controller(mode=mode, set_point=self.get_set_point())

        data = []
        for i in range(160):
            height = sensor.read_height()
            flow = controller.calculate(height, pump.max_flow, 1)
            flow = pump.set_flow(flow)
            data.append(tank.update(flow, 1))

        return data

    def compare(self):
        onoff_data = self.run_test("On-Off")
        pid_data = self.run_test("PID")

        sp = self.get_set_point()

        onoff_error = sum(abs(sp - x) for x in onoff_data) / len(onoff_data)
        pid_error = sum(abs(sp - x) for x in pid_data) / len(pid_data)

        txt = "مقایسه کنترلرها:\n"
        txt += "میانگین خطای On-Off: %.2f\n" % onoff_error
        txt += "میانگین خطای PID: %.2f\n" % pid_error

        if pid_error < onoff_error:
            txt += "PID در این اجرا نتیجه بهتری دارد."
        else:
            txt += "On-Off در این اجرا بهتر یا نزدیک‌تر است."

        self.compare_info.config(text=txt)
        self.draw_compare_graph(onoff_data, pid_data)

    def draw_compare_graph(self, onoff_data, pid_data):
        self.graph_canvas.delete("all")

        self.graph_canvas.create_line(40, 280, 600, 280)
        self.graph_canvas.create_line(40, 20, 40, 280)
        self.graph_canvas.create_text(310, 12, text="مقایسه On-Off و PID")
        self.graph_canvas.create_text(500, 35, text="آبی: On-Off")
        self.graph_canvas.create_text(500, 55, text="سبز: PID")

        count = len(onoff_data)

        for i in range(count - 1):
            x1 = 40 + i * (560 / count)
            x2 = 40 + (i + 1) * (560 / count)

            y1 = 280 - (onoff_data[i] / self.tank.max_height) * 260
            y2 = 280 - (onoff_data[i + 1] / self.tank.max_height) * 260
            self.graph_canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

            y3 = 280 - (pid_data[i] / self.tank.max_height) * 260
            y4 = 280 - (pid_data[i + 1] / self.tank.max_height) * 260
            self.graph_canvas.create_line(x1, y3, x2, y4, fill="green", width=2)

        sp_y = 280 - (self.get_set_point() / self.tank.max_height) * 260
        self.graph_canvas.create_line(40, sp_y, 600, sp_y, fill="red", dash=(4, 3))


if __name__ == "__main__":
    root = tk.Tk()
    app = Simulation(root)
    root.mainloop()
