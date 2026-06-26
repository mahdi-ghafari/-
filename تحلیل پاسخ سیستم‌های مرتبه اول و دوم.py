import tkinter as tk
from tkinter import messagebox
import math

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except Exception:
    matplotlib = None


class TransferFunction:
    def __init__(self, k=1.0, zeta=0.5, wn=2.0, system_order=2):
        self.k = k
        self.zeta = zeta
        self.wn = wn
        self.system_order = system_order

    def value_at(self, t):
        if self.system_order == 1:
            if self.wn <= 0:
                return 0
            return self.k * (1 - math.exp(-self.wn * t))

        if self.wn <= 0:
            return 0

        z = self.zeta
        wn = self.wn

        if z < 1:
            wd = wn * math.sqrt(1 - z * z)
            angle_part = math.cos(wd * t)
            sin_part = (z / math.sqrt(1 - z * z)) * math.sin(wd * t)
            return self.k * (1 - math.exp(-z * wn * t) * (angle_part + sin_part))

        if z == 1:
            return self.k * (1 - math.exp(-wn * t) * (1 + wn * t))

        s1 = -wn * (z - math.sqrt(z * z - 1))
        s2 = -wn * (z + math.sqrt(z * z - 1))
        a = s2 / (s2 - s1)
        b = s1 / (s1 - s2)
        return self.k * (1 + a * math.exp(s1 * t) + b * math.exp(s2 * t))


class StepResponse:
    def __init__(self, transfer_function):
        self.transfer_function = transfer_function
        self.times = []
        self.values = []

    def make_response(self):
        self.times.clear()
        self.values.clear()

        wn = self.transfer_function.wn
        if wn <= 0:
            end_time = 10
        else:
            end_time = max(10, 8 / wn)

        points = 600
        for i in range(points + 1):
            t = end_time * i / points
            y = self.transfer_function.value_at(t)
            self.times.append(t)
            self.values.append(y)

        return self.times, self.values


class Analyzer:
    def __init__(self, transfer_function, response):
        self.transfer_function = transfer_function
        self.response = response

    def settling_time(self):
        final_value = self.transfer_function.k
        if final_value == 0:
            return 0

        band = abs(final_value) * 0.02
        times = self.response.times
        values = self.response.values

        for i in range(len(values)):
            ok = True
            for j in range(i, len(values)):
                if abs(values[j] - final_value) > band:
                    ok = False
                    break
            if ok:
                return times[i]
        return None

    def overshoot(self):
        final_value = self.transfer_function.k
        if final_value == 0 or not self.response.values:
            return 0
        maximum_value = max(self.response.values)
        extra = maximum_value - final_value
        if extra <= 0:
            return 0
        return (extra / abs(final_value)) * 100

    def rise_time(self):
        final_value = self.transfer_function.k
        if final_value == 0:
            return 0

        low = 0.1 * final_value
        high = 0.9 * final_value
        t_low = None
        t_high = None

        for t, y in zip(self.response.times, self.response.values):
            if t_low is None and y >= low:
                t_low = t
            if t_high is None and y >= high:
                t_high = t
                break

        if t_low is None or t_high is None:
            return None
        return t_high - t_low

    def get_all(self):
        return {
            "settling": self.settling_time(),
            "overshoot": self.overshoot(),
            "rise": self.rise_time()
        }


class Plotter:
    def __init__(self, master):
        self.master = master
        self.canvas = None

    def draw(self, times, values):
        if matplotlib is None:
            messagebox.showerror("خطا", "کتابخانه matplotlib نصب نیست.")
            return

        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        fig = Figure(figsize=(6.5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(times, values)
        ax.set_title("Step Response")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Output")
        ax.grid(True)

        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


class MainProgram:
    def __init__(self, root):
        self.root = root
        self.root.title("تحلیل پاسخ سیستم")
        self.root.geometry("900x600")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(self.main_frame, width=240)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.plotter = Plotter(self.right_frame)
        self.make_inputs()

    def make_inputs(self):
        tk.Label(self.left_frame, text="پارامترهای سیستم", font=("Tahoma", 12, "bold")).pack(pady=8)

        tk.Label(self.left_frame, text="K").pack(anchor="w")
        self.k_entry = tk.Entry(self.left_frame)
        self.k_entry.insert(0, "1")
        self.k_entry.pack(fill=tk.X, pady=3)

        tk.Label(self.left_frame, text="ζ").pack(anchor="w")
        self.zeta_entry = tk.Entry(self.left_frame)
        self.zeta_entry.insert(0, "0.5")
        self.zeta_entry.pack(fill=tk.X, pady=3)

        tk.Label(self.left_frame, text="ωn").pack(anchor="w")
        self.wn_entry = tk.Entry(self.left_frame)
        self.wn_entry.insert(0, "2")
        self.wn_entry.pack(fill=tk.X, pady=3)

        tk.Label(self.left_frame, text="نوع سیستم").pack(anchor="w", pady=(10, 0))
        self.order_var = tk.IntVar(value=2)
        tk.Radiobutton(self.left_frame, text="مرتبه اول", variable=self.order_var, value=1).pack(anchor="w")
        tk.Radiobutton(self.left_frame, text="مرتبه دوم", variable=self.order_var, value=2).pack(anchor="w")

        tk.Button(self.left_frame, text="رسم و تحلیل", command=self.run_program).pack(fill=tk.X, pady=12)

        self.result_label = tk.Label(self.left_frame, text="نتایج هنوز محاسبه نشده است", justify=tk.LEFT)
        self.result_label.pack(anchor="w", pady=10)

        info = "برای سیستم مرتبه اول، مقدار ζ استفاده نمی‌شود."
        tk.Label(self.left_frame, text=info, wraplength=220, fg="gray").pack(anchor="w", pady=10)

    def run_program(self):
        try:
            k = float(self.k_entry.get())
            zeta = float(self.zeta_entry.get())
            wn = float(self.wn_entry.get())
            order = int(self.order_var.get())
        except ValueError:
            messagebox.showerror("خطا", "لطفاً مقدارهای عددی وارد کنید.")
            return

        if wn <= 0:
            messagebox.showerror("خطا", "ωn باید بزرگ‌تر از صفر باشد.")
            return

        if order == 2 and zeta < 0:
            messagebox.showerror("خطا", "ζ نباید منفی باشد.")
            return

        tf = TransferFunction(k, zeta, wn, order)
        response = StepResponse(tf)
        times, values = response.make_response()

        analyzer = Analyzer(tf, response)
        data = analyzer.get_all()

        settling = self.format_number(data["settling"])
        overshoot = self.format_number(data["overshoot"])
        rise = self.format_number(data["rise"])

        result_text = (
            "نتایج تحلیل:\n"
            f"زمان نشست: {settling} ثانیه\n"
            f"فراجهش: {overshoot} درصد\n"
            f"زمان صعود: {rise} ثانیه"
        )
        self.result_label.config(text=result_text)

        self.plotter.draw(times, values)

    def format_number(self, value):
        if value is None:
            return "محاسبه نشد"
        return f"{value:.3f}"


if __name__ == "__main__":
    root = tk.Tk()
    app = MainProgram(root)
    root.mainloop()
