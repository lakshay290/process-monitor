import os
import time
import psutil
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class EcoKernelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EcoKernel Process Monitor")
        self.root.geometry("800x600")

        # Create a frame for system info
        self.system_frame = ttk.LabelFrame(self.root, text="System Information")
        self.system_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Labels for system info
        self.cpu_label = ttk.Label(self.system_frame, text="CPU Usage: 0%")
        self.cpu_label.pack(pady=5)
       #labels for cpu , memory disk
        self.memory_label = ttk.Label(self.system_frame, text="Memory Usage: 0%")
        self.memory_label.pack(pady=5)

        self.disk_label = ttk.Label(self.system_frame, text="Disk Usage: 0%")
        self.disk_label.pack(pady=5)

        # Create a frame for process info
        self.process_frame = ttk.LabelFrame(self.root, text="Top Processes")
        self.process_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview for processes
        self.process_tree = ttk.Treeview(self.process_frame, columns=("PID", "Name", "User ", "CPU %", "Memory %"), show="headings")
        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Name", text="Name")
        self.process_tree.heading("User ", text="User ")
        self.process_tree.heading("CPU %", text="CPU %")
        self.process_tree.heading("Memory %", text="Memory %")
        self.process_tree.pack(fill=tk.BOTH, expand=True)

        # Create a frame for graphs
        self.graph_frame = ttk.LabelFrame(self.root, text="Usage Graphs")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a figure for the plot
        self.fig, self.ax = plt.subplots(2, 1, figsize=(8, 4))
        self.cpu_line, = self.ax[0].plot([], [], 'r-', label='CPU Usage')
        self.memory_line, = self.ax[1].plot([], [], 'b-', label='Memory Usage')
        self.ax[0].set_ylim(0, 100)
        self.ax[1].set_ylim(0, 100)
        self.ax[0].set_title('CPU Usage Over Time')
        self.ax[1].set_title('Memory Usage Over Time')
        self.ax[0].set_ylabel('Percent %')
        self.ax[1].set_ylabel('Percent %')
        self.ax[1].set_xlabel('Time (last 30 readings)')
        self.ax[0].legend()
        self.ax[1].legend()

        # Embed the figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize data
        self.cpu_history = []
        self.memory_history = []

        # Start the update loop
        self.update_data()

    def update_data(self):
        """Update all data from the system"""
        try:
            # Get system info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Update labels
            self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
            self.memory_label.config(text=f"Memory Usage: {memory.percent:.1f}%")
            self.disk_label.config(text=f"Disk Usage: {disk.percent:.1f}%")

            # Update history for graphs
            self.cpu_history.append(cpu_percent)
            self.memory_history.append(memory.percent)

            # Keep only the last 30 readings
            if len(self.cpu_history) > 30:
                self.cpu_history.pop(0)
            if len(self.memory_history) > 30:
                self.memory_history.pop(0)

            # Update graphs
            self.cpu_line.set_xdata(range(len(self.cpu_history)))
            self.cpu_line.set_ydata(self.cpu_history)
            self.memory_line.set_xdata(range(len(self.memory_history)))
            self.memory_line.set_ydata(self.memory_history)
            self.ax[0].set_xlim(0, 30)
            self.ax[1].set_xlim(0, 30)
            self.canvas.draw()

            # Update process list
            self.update_process_list()

            # Schedule the next update
            self.root.after(2000, self.update_data)  # Update every 2 seconds

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update system data: {str(e)}")

    def update_process_list(self):
        """Update the process list in the GUI"""
        # Clear the current list
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        # Get process data
        processes = self.get_process_info()

        # Sort processes by CPU usage
        sorted_processes = sorted(processes.values(), key=lambda x: x.get('cpu_percent', 0), reverse=True)

        # Add the top processes to the list
        for proc in sorted_processes[:10]:  # Limit to top 10 processes
            self.process_tree.insert("", "end", values=(
                proc['pid'],
                proc['name'],
                proc.get('username', 'Unknown'),
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}"
            ))

    def get_process_info(self):
        """Get information about all running processes"""
        processes = {}
        for proc in psutil.process_iter():
            try:
                # Get process info
                process_info = proc.as_dict(attrs=['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent'])
                processes[proc.pid] = process_info
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

def main():
    """Main function to run the EcoKernel GUI"""
    root = tk.Tk()
    app = EcoKernelGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()