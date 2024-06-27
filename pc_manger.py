import os
import psutil
import platform
import tkinter as tk
from tkinter import ttk, messagebox
import random

class PCManager:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Manager")
        self.root.geometry("800x600")
        self.root.configure(bg="#1f1f23")  # Dark background color

        # Create style for frames
        self.style = ttk.Style()
        self.style.configure("Dark.TFrame", background="#1f1f23")  # Set background color for frames

        # Create tabs
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)

        # System Information Tab
        self.frame_system = ttk.Frame(self.tabs, style="Dark.TFrame")
        self.tabs.add(self.frame_system, text="System Information")

        self.system_label = ttk.Label(self.frame_system, text="System Information", font=("Segoe UI", 18), foreground="white", background="#1f1f23")
        self.system_label.pack(pady=10)

        self.system_info = ttk.Treeview(self.frame_system, columns=("Key", "Value"), show='headings', height=10)
        self.system_info.pack(fill="both", expand=True)
        self.system_info.heading("Key", text="Key")
        self.system_info.column("Key", width=200, anchor="center")
        self.system_info.heading("Value", text="Value")
        self.system_info.column("Value", width=400, anchor="center")

        self.get_system_info()

        # Process Manager Tab
        self.frame_processes = ttk.Frame(self.tabs, style="Dark.TFrame")
        self.tabs.add(self.frame_processes, text="Process Manager")

        self.processes_label = ttk.Label(self.frame_processes, text="Process Manager", font=("Segoe UI", 18), foreground="white", background="#1f1f23")
        self.processes_label.pack(pady=10)

        self.processes_list = ttk.Treeview(self.frame_processes, columns=("Process", "PID", "Memory"), show='headings', height=10)
        self.processes_list.pack(fill="both", expand=True)
        self.processes_list.heading("Process", text="Process")
        self.processes_list.column("Process", width=200, anchor="center")
        self.processes_list.heading("PID", text="PID")
        self.processes_list.column("PID", width=100, anchor="center")
        self.processes_list.heading("Memory", text="Memory")
        self.processes_list.column("Memory", width=200, anchor="center")

        self.get_processes()

        self.end_process_button = ttk.Button(self.frame_processes, text="End Process", command=self.end_process)
        self.end_process_button.pack(pady=10)

        # Resource Monitor Tab
        self.frame_resource_monitor = ttk.Frame(self.tabs, style="Dark.TFrame")
        self.tabs.add(self.frame_resource_monitor, text="Resource Monitor")

        self.resource_label = ttk.Label(self.frame_resource_monitor, text="Resource Monitor", font=("Segoe UI", 18), foreground="white", background="#1f1f23")
        self.resource_label.pack(pady=10)

        self.cpu_label = ttk.Label(self.frame_resource_monitor, text="CPU Usage: 0%", foreground="white", background="#1f1f23")
        self.cpu_label.pack(pady=10)

        self.memory_label = ttk.Label(self.frame_resource_monitor, text="Memory Usage: 0%", foreground="white", background="#1f1f23")
        self.memory_label.pack(pady=10)

        self.update_resource_monitor()

        # Optimization Button
        self.optimization_button = ttk.Button(self.root, text="Optimize System", command=self.optimize_system)
        self.optimization_button.pack(pady=10)
        self.optimization_button.configure(style="Optimize.TButton")

        # Style settings
        self.style.configure("Optimize.TButton", foreground="white", background="#4CAF50", font=("Segoe UI", 12, "bold"), width=15)

    def get_system_info(self):
        try:
            system_info = [
                ("Operating System", os.name),
                ("System Architecture", platform.machine()),  # Use platform.machine() instead of os.uname().machine
                ("Processor", os.cpu_count()),
                ("Physical Cores", psutil.cpu_count(logical=False)),
                ("Total Memory", f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB"),
                ("Available Memory", f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB"),
                ("Disk Usage", f"{psutil.disk_usage('/').percent}%")
            ]

            for item in system_info:
                self.system_info.insert("", "end", values=item)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get system information: {str(e)}")

    def get_processes(self):
        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                info = proc.info
                self.processes_list.insert("", "end", values=(info['name'], info['pid'], f"{info['memory_info'].rss / (1024 ** 2):.2f} MB"))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    def end_process(self):
        try:
            selected_item = self.processes_list.selection()[0]
            pid = int(self.processes_list.item(selected_item, 'values')[1])
            psutil.Process(pid).terminate()
            self.processes_list.delete(selected_item)
            messagebox.showinfo("Process Manager", f"Process {pid} terminated successfully.")
        except IndexError:
            messagebox.showwarning("Process Manager", "No process selected.")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("Process Manager", str(e))

    def update_resource_monitor(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent

            self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
            self.memory_label.config(text=f"Memory Usage: {memory_usage}%")

            self.root.after(1000, self.update_resource_monitor)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update resource monitor: {str(e)}")

    def optimize_system(self):
        try:
            memory_freed = 0
            for proc in sorted(psutil.process_iter(['pid', 'name', 'memory_info']), key=lambda p: p.info['memory_info'].rss, reverse=True):
                if memory_freed >= 200 * 1024 * 1024:
                    break
                if proc.info['name'] != "System" and proc.info['name'] != "python":
                    try:
                        proc.terminate()
                        memory_freed += proc.info['memory_info'].rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

            messagebox.showinfo("Optimization", f"System optimization completed. {memory_freed / (1024 ** 2):.2f} MB of memory freed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to optimize system: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PCManager(root)
    root.mainloop()
