import tkinter as tk
from tkinter import messagebox
import math
import random


class Pendulum:
    def __init__(self):
        self.length = 120
        self.angle = 0.12
        self.angular_speed = 0.0
        self.angular_acceleration = 0.0
        self.gravity = 9.8
        self.sensor_noise = 0.0

    def reset(self):
        self.angle = 0.12
        self.angular_speed = 0.0
        self.angular_acceleration = 0.0

    def read_angle(self):
        noise = random.uniform(-self.sensor_noise, self.sensor_noise)
        return self.angle + noise

    def update(self, cart_acceleration, dt):
        # مدل ساده شده پاندول معکوس روی گاری
        self.angular_acceleration = (
            (self.gravity * math.sin(self.angle)) -
            (cart_acceleration * math.cos(self.angle))
        ) / (self.length / 100)

        self.angular_speed += self.angular_acceleration * dt
        self.angle += self.angular_speed * dt

    def is_fallen(self):
        return abs(self.angle) > math.radians(45)


class Cart:
    def __init__(self):
        self.x = 350
        self.speed = 0.0
        self.acceleration = 0.0
        self.width = 80
        self.height = 30

    def reset(self):
        self.x = 350
        self.speed = 0.0
        self.acceleration = 0.0

    def apply_force(self, force):
        self.acceleration = force

    def update(self, dt):
        self.speed += self.acceleration * dt
        self.x += self.speed * dt

        if self.x < 80:
            self.x = 80
            self.speed = 0
        elif self.x > 620:
            self.x = 620
            self.speed = 0


class Controller:
    def __init__(self):
        self.auto_mode = True
        self.manual_force = 0.0
        self.k_angle = 55
        self.k_speed = 14
        self.k_cart = 0.35
        self.noise_enabled = False

    def control(self, pendulum, cart):
        if self.auto_mode:
            angle = pendulum.read_angle()
            force = (
                self.k_angle * angle +
                self.k_speed * pendulum.angular_speed +
                self.k_cart * (cart.x - 350)
            )
            return force
        return self.manual_force

    def set_manual_left(self):
        self.manual_force = -80

    def set_manual_right(self):
        self.manual_force = 80

    def stop_manual(self):
        self.manual_force = 0


class Simulation:
    def __init__(self, root):
        self.root = root
        self.root.title("بازی تعادلی پاندول معکوس")
        self.root.geometry("760x560")
        self.root.resizable(False, False)

        self.cart = Cart()
        self.pendulum = Pendulum()
        self.controller = Controller()

        self.running = False
        self.dt = 0.03

        self.make_gui()
        self.draw_scene()

    def make_gui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=8)

        self.start_button = tk.Button(top_frame, text="شروع", width=10, command=self.start)
        self.start_button.grid(row=0, column=0, padx=4)

        self.stop_button = tk.Button(top_frame, text="توقف", width=10, command=self.stop)
        self.stop_button.grid(row=0, column=1, padx=4)

        self.reset_button = tk.Button(top_frame, text="شروع دوباره", width=12, command=self.reset)
        self.reset_button.grid(row=0, column=2, padx=4)

        self.mode_button = tk.Button(top_frame, text="حالت: کنترلر", width=14, command=self.change_mode)
        self.mode_button.grid(row=0, column=3, padx=4)

        self.noise_button = tk.Button(top_frame, text="نویز سنسور: خاموش", width=17, command=self.change_noise)
        self.noise_button.grid(row=0, column=4, padx=4)

        self.canvas = tk.Canvas(self.root, width=700, height=380, bg="white")
        self.canvas.pack(pady=10)

        info_frame = tk.Frame(self.root)
        info_frame.pack()

        self.info_label = tk.Label(info_frame, text="زاویه: 0   موقعیت گاری: 0", font=("Tahoma", 10))
        self.info_label.pack()

        help_text = "در حالت دستی از کلیدهای چپ و راست استفاده کنید. هدف این است پاندول سقوط نکند."
        self.help_label = tk.Label(self.root, text=help_text, font=("Tahoma", 9))
        self.help_label.pack(pady=5)

        self.root.bind("<Left>", self.left_key)
        self.root.bind("<Right>", self.right_key)
        self.root.bind("<KeyRelease>", self.key_release)

    def start(self):
        if not self.running:
            self.running = True
            self.run()

    def stop(self):
        self.running = False

    def reset(self):
        self.stop()
        self.cart.reset()
        self.pendulum.reset()
        self.draw_scene()

    def change_mode(self):
        self.controller.auto_mode = not self.controller.auto_mode
        if self.controller.auto_mode:
            self.mode_button.config(text="حالت: کنترلر")
        else:
            self.mode_button.config(text="حالت: دستی")

    def change_noise(self):
        self.controller.noise_enabled = not self.controller.noise_enabled
        if self.controller.noise_enabled:
            self.pendulum.sensor_noise = 0.035
            self.noise_button.config(text="نویز سنسور: روشن")
        else:
            self.pendulum.sensor_noise = 0.0
            self.noise_button.config(text="نویز سنسور: خاموش")

    def left_key(self, event):
        if not self.controller.auto_mode:
            self.controller.set_manual_left()

    def right_key(self, event):
        if not self.controller.auto_mode:
            self.controller.set_manual_right()

    def key_release(self, event):
        if not self.controller.auto_mode:
            self.controller.stop_manual()

    def run(self):
        if not self.running:
            return

        force = self.controller.control(self.pendulum, self.cart)
        self.cart.apply_force(force)
        self.cart.update(self.dt)
        self.pendulum.update(self.cart.acceleration, self.dt)

        self.draw_scene()

        if self.pendulum.is_fallen():
            self.running = False
            messagebox.showinfo("پایان بازی", "پاندول سقوط کرد!")
            return

        self.root.after(int(self.dt * 1000), self.run)

    def draw_scene(self):
        self.canvas.delete("all")

        ground_y = 300
        self.canvas.create_line(40, ground_y + 20, 660, ground_y + 20, width=2)

        cart_left = self.cart.x - self.cart.width / 2
        cart_right = self.cart.x + self.cart.width / 2
        cart_top = ground_y - self.cart.height / 2
        cart_bottom = ground_y + self.cart.height / 2

        self.canvas.create_rectangle(cart_left, cart_top, cart_right, cart_bottom, fill="lightgray")
        self.canvas.create_oval(cart_left + 8, cart_bottom - 2, cart_left + 28, cart_bottom + 18, fill="gray")
        self.canvas.create_oval(cart_right - 28, cart_bottom - 2, cart_right - 8, cart_bottom + 18, fill="gray")

        pivot_x = self.cart.x
        pivot_y = cart_top

        end_x = pivot_x + self.pendulum.length * math.sin(self.pendulum.angle)
        end_y = pivot_y - self.pendulum.length * math.cos(self.pendulum.angle)

        self.canvas.create_line(pivot_x, pivot_y, end_x, end_y, width=5)
        self.canvas.create_oval(end_x - 12, end_y - 12, end_x + 12, end_y + 12, fill="black")
        self.canvas.create_oval(pivot_x - 5, pivot_y - 5, pivot_x + 5, pivot_y + 5, fill="red")

        mode = "کنترلر" if self.controller.auto_mode else "دستی"
        noise = "روشن" if self.controller.noise_enabled else "خاموش"
        angle_degree = math.degrees(self.pendulum.angle)
        self.info_label.config(
            text=f"زاویه: {angle_degree:.2f} درجه   موقعیت گاری: {self.cart.x:.1f}   حالت: {mode}   نویز: {noise}"
        )


if __name__ == "__main__":
    main_window = tk.Tk()
    app = Simulation(main_window)
    main_window.mainloop()
