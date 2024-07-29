import tkinter as tk
import pyautogui
import pytesseract
from PIL import Image
import time
import queue
import webbrowser

log_queue = queue.Queue()

# Set the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

monitoring_window = None
control_window = None
region = (0, 0, 100, 100)
typing = False

def log_action(action):
    current_time = time.strftime("%H:%M:%S")
    log_message = f"{action} at {current_time}\n"
    log_queue.put(log_message)
    print(log_message)

def update_log():
    while not log_queue.empty():
        log_message = log_queue.get()
        control_window_log.insert(tk.END, log_message)
        control_window_log.yview(tk.END)
    control_window.after(100, update_log)

def make_transparent(window):
    window.wm_attributes("-transparentcolor", "gray")
    window.wm_attributes("-topmost", 1)

def on_drag(event):
    if monitoring_window:
        monitoring_window.geometry(f"+{event.x_root}+{event.y_root}")

def on_resize(event):
    update_region()

def update_region():
    global region
    if monitoring_window:
        left = monitoring_window.winfo_x() + 10
        top = monitoring_window.winfo_y() + 10
        width = monitoring_window.winfo_width() - 20
        height = monitoring_window.winfo_height() - 20
        region = (left, top, left + width, top + height)
        if control_window_status_label:
            control_window_status_label.config(text=f"Region updated to: {region}")

def get_region_colors(region):
    left, top, right, bottom = region
    if right <= left or bottom <= top:
        return []
    screenshot = pyautogui.screenshot(region=(left, top, right-left, bottom-top))
    return [screenshot.getpixel((x, y))
            for x in range(right-left)
            for y in range(bottom-top)]

def stop_typing(event=None):
    global typing
    if typing:
        typing = False
        control_window_status_label.config(text="Stopped due to background detection.")

def monitor_region():
    global typing
    initial_colors = get_region_colors(region)
    while typing:
        current_colors = get_region_colors(region)
        if is_significant_change(initial_colors, current_colors):
            log_action("Stopping, significant change detected")
            stop_typing()
            break

def is_significant_change(initial_colors, current_colors, threshold=0.05):
    """Check if there is a significant change in colors."""
    if len(initial_colors) != len(current_colors):
        return True

    changed_pixels = sum(1 for i in range(len(initial_colors))
                         if initial_colors[i] != current_colors[i])
    change_ratio = changed_pixels / len(initial_colors)
    return change_ratio > threshold

def start_typing():
    global typing, last_fish_time, last_buy_time, last_charms_time, last_quests_time, last_pet_time, last_play_time
    typing = True
    last_fish_time = time.time()
    last_buy_time = time.time()
    last_charms_time = time.time()
    last_quests_time = time.time()
    last_pet_time = time.time()
    last_play_time = time.time()

    def typing_task():
        global typing, last_fish_time, last_buy_time, last_charms_time, last_quests_time, last_pet_time, last_play_time
        if not typing:
            return

        monitor_region()  # Check for region changes

        current_time = time.time()

        if fish_var.get() and (current_time - last_fish_time >= float(fish_entry.get()) * 1):  # Converted to seconds
            if not typing:
                return
            pyautogui.typewrite("/fish ")
            pyautogui.press('enter')
            log_action("/fish sent")
            last_fish_time = current_time

        if buy_var.get() and (current_time - last_buy_time >= float(buy_entry.get()) * 60):
            if not typing:
                return
            pyautogui.typewrite("/buy ")
            pyautogui.press('enter')
            time.sleep(0.2)
            pyautogui.typewrite("Fish5m")
            pyautogui.press('enter')
            log_action("/buy Fish5m sent")

            time.sleep(0.2)
            pyautogui.typewrite("/buy ")
            pyautogui.press('enter')
            time.sleep(0.2)
            pyautogui.typewrite("Treasure5m")
            pyautogui.press('enter')
            log_action("/buy Treasure5m sent")

            last_buy_time = current_time

        if charms_var.get() and (current_time - last_charms_time >= float(charms_entry.get()) * 60):
            if not typing:
                return
            pyautogui.typewrite("/charms ")
            pyautogui.press('enter')
            log_action("/charms sent")
            last_charms_time = current_time

        if quests_var.get() and (current_time - last_quests_time >= float(quests_entry.get()) * 60):
            if not typing:
                return
            pyautogui.typewrite("/quests ")
            pyautogui.press('enter')
            log_action("/quests sent")
            last_quests_time = current_time

        if pet_var.get() and (current_time - last_pet_time >= float(pet_entry.get()) * 60):
            if not typing:
                return
            pyautogui.typewrite("/pet ")
            pyautogui.press('enter')
            log_action("/pet sent")
            last_pet_time = current_time

        if play_var.get() and (current_time - last_play_time >= float(play_entry.get()) * 60):
            if not typing:
                return
            pyautogui.typewrite("/play ")
            pyautogui.press('enter')
            log_action("/play sent")
            last_play_time = current_time

        control_window.after(1000, typing_task)

    typing_task()

def start_monitoring():
    monitor_region()
    if control_window_status_label:
        control_window_status_label.config(text="Status: Monitoring...")

def stop_monitoring():
    global typing
    typing = False
    if control_window_status_label:
        control_window_status_label.config(text="Status: Idle")

def on_closing_control_window():
    global typing
    typing = False
    control_window.destroy()

def on_closing_monitor_window():
    monitoring_window.destroy()

def create_monitoring_window():
    global monitoring_window
    monitoring_window = tk.Toplevel(control_window)
    monitoring_window.title("Monitoring Window")
    monitoring_window.geometry("300x300")
    monitoring_window.configure(bg="gray")
    make_transparent(monitoring_window)

    inner_frame = tk.Frame(monitoring_window, bg="gray")
    inner_frame.place(x=10, y=10, relwidth=1.0, relheight=1.0)

    monitoring_window.bind("<B1-Motion>", on_drag)
    monitoring_window.bind("<Configure>", on_resize)

    monitoring_window.protocol("WM_DELETE_WINDOW", on_closing_monitor_window)

def create_control_window():
    global control_window, control_window_status_label, control_window_log
    global fish_entry, buy_entry, charms_entry, quests_entry, pet_entry, play_entry
    global fish_var, buy_var, charms_var, quests_var, pet_var, play_var

    control_window = tk.Tk()
    control_window.title("AutoFish from LegoLovesYou<3")
    control_window.geometry("500x535")
    control_window.configure(bg="#003366")


    start_button = tk.Button(control_window, text="Start", command=start_typing, bg="#003845", font=("Arial", 14), width=10)
    start_button.grid(row=0, column=0, columnspan=1, pady=10)

    stop_button = tk.Button(control_window, text="Stop", command=stop_monitoring, bg="#003845", font=("Arial", 14), width=10)
    stop_button.grid(row=0, column=2, columnspan=1, pady=10)


    control_window_status_label = tk.Label(control_window, text="Status: Idle", bg="#003845", fg="lightgray")
    control_window_status_label.grid(row=1, column=0, columnspan=4, pady=10)


    control_window_log = tk.Text(control_window, height=10, width=60, bg="#003845", fg="lightgray")
    control_window_log.grid(row=2, column=0, columnspan=4, pady=10)
    control_window_log.insert(tk.END, "Log started...\n")


    # Create time entry labels and fields
    tk.Label(control_window, text="Fish Interval (seconds):", bg="#003845", fg="lightgray").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
    fish_var = tk.BooleanVar(value=True)
    tk.Checkbutton(control_window, text="Enable Fish", variable=fish_var, command=update_visibility, bg="#003845", fg="lightgray").grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
    fish_entry = tk.Entry(control_window, bg="#003845", fg="lightgray")
    fish_entry.insert(tk.END, "3")
    fish_entry.grid(row=3, column=2, padx=10, pady=5)

    tk.Label(control_window, text="Buy Interval (minutes):", bg="#003845", fg="lightgray").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
    buy_var = tk.BooleanVar(value=True)
    tk.Checkbutton(control_window, text="Enable Boosters", variable=buy_var, command=update_visibility, bg="#003845", fg="lightgray").grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
    buy_entry = tk.Entry(control_window, bg="#003845", fg="lightgray")
    buy_entry.insert(tk.END, "5")
    buy_entry.grid(row=4, column=2, padx=10, pady=5)

    tk.Label(control_window, text="Charms Interval (minutes):", bg="#003845", fg="lightgray").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
    charms_var = tk.BooleanVar(value=True)
    tk.Checkbutton(control_window, text="Enable Charms", variable=charms_var, command=update_visibility, bg="#003845", fg="lightgray").grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
    charms_entry = tk.Entry(control_window, bg="#003845", fg="lightgray")
    charms_entry.insert(tk.END, "10")
    charms_entry.grid(row=5, column=2, padx=10, pady=5)

    tk.Label(control_window, text="Quests Interval (minutes):", bg="#003845", fg="lightgray").grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)
    quests_var = tk.BooleanVar(value=True)
    tk.Checkbutton(control_window, text="Enable Quests", variable=quests_var, command=update_visibility, bg="#003845", fg="lightgray").grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)
    quests_entry = tk.Entry(control_window, bg="#003845", fg="lightgray")
    quests_entry.insert(tk.END, "15")
    quests_entry.grid(row=6, column=2, padx=10, pady=5)

    tk.Label(control_window, text="Pet Interval (minutes):", bg="#003845", fg="lightgray").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
    pet_var = tk.BooleanVar(value=True)
    tk.Checkbutton(control_window, text="Enable Pet", variable=pet_var, command=update_visibility, bg="#003845", fg="lightgray").grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)
    pet_entry = tk.Entry(control_window, bg="#003845", fg="lightgray")
    pet_entry.insert(tk.END, "20")
    pet_entry.grid(row=7, column=2, padx=10, pady=5)

    tk.Label(control_window, text="Play Interval (minutes):", bg="#003845", fg="lightgray").grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)
    play_var = tk.BooleanVar(value=True)
    tk.Checkbutton(control_window, text="Enable Play", variable=play_var, command=update_visibility, bg="#003845", fg="lightgray").grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)
    play_entry = tk.Entry(control_window, bg="#003845", fg="lightgray")
    play_entry.insert(tk.END, "25")
    play_entry.grid(row=8, column=2, padx=10, pady=5)

    tk.Button(control_window, text="Create Monitoring Window", command=create_monitoring_window, bg="#003845", fg="lightgray").grid(row=9, column=0, columnspan=5, pady=10)
    tk.Button(control_window, text="Join my Discord!", command=lambda: webbrowser.open("https://discord.gg/Ps7e7zR7tQ"), bg="#003845", fg="lightgray").grid(row=9, column=2, padx=10, pady=10)


    control_window.protocol("WM_DELETE_WINDOW", on_closing_control_window)
    update_log()
    control_window.mainloop()

def update_visibility():
    fish_entry.grid_forget() if not fish_var.get() else fish_entry.grid(row=3, column=2, padx=10, pady=5)
    buy_entry.grid_forget() if not buy_var.get() else buy_entry.grid(row=4, column=2, padx=10, pady=5)
    charms_entry.grid_forget() if not charms_var.get() else charms_entry.grid(row=5, column=2, padx=10, pady=5)
    quests_entry.grid_forget() if not quests_var.get() else quests_entry.grid(row=6, column=2, padx=10, pady=5)
    pet_entry.grid_forget() if not pet_var.get() else pet_entry.grid(row=7, column=2, padx=10, pady=5)
    play_entry.grid_forget() if not play_var.get() else play_entry.grid(row=8, column=2, padx=10, pady=5)

def run_guis():
    create_control_window()
    create_monitoring_window()
    start_monitoring()
    control_window.after(100, update_log)
    control_window.mainloop()

if __name__ == "__main__":
    try:
        run_guis()
    except Exception as e:
        print(f"An error occurred: {e}")
