import tkinter as tk
import random
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Objective Function
def Objective_Function(initial_fare, initial_cost, initial_takeoff_time, initial_duration, initial_fki_cost, pop, dim_cost, trp):
    objective_pop = [[0, 0] for _ in range(pop)]    
    for i in range(pop):
        total_cost = 0
        for j in range(dim_cost):
            total_cost += initial_fki_cost[i][j] * initial_cost[i][j]
        objective_pop[i][0] = total_cost

        # Adjustment factor f for fare
        if abs(initial_fare[i][0] - initial_fare[i][1]) > 2 * initial_fare[i][1]:
            f = 0
        elif abs(initial_fare[i][0] - initial_fare[i][1]) < 0.5 * initial_fare[i][1]:
            f = 1
        else:
            f = 0.5

        # Adjustment factor tot for takeoff time
        if abs(initial_takeoff_time[i][0] - initial_takeoff_time[i][1]) > 2 * initial_takeoff_time[i][1]:
            tot = 0
        elif abs(initial_takeoff_time[i][0] - initial_takeoff_time[i][1]) < 0.5 * initial_takeoff_time[i][1]:
            tot = 1
        else:
            tot = 0.5

        # Adjustment factor td for total duration
        if abs(initial_duration[i][0] - initial_duration[i][1]) > 2 * initial_duration[i][1]:
            td = 0
        elif abs(initial_duration[i][0] - initial_duration[i][1]) < 0.5 * initial_duration[i][1]:
            td = 1
        else:
            td = 0.5

        brp = (f + tot + td) / 3
        total_fare = abs(initial_fare[i][0] - brp * initial_fare[i][1]) * trp
        objective_pop[i][1] = total_fare
    
    return objective_pop

# Improving Phase
def improving_phase(experimental_pop, pop, dim, gbest_row):
    modified_pop = np.copy(experimental_pop)
    for i in range(pop):
        for j in range(dim):
            rdm = random.random()
            modified_pop[i, j] = 0.5 * experimental_pop[i, j] + rdm * (experimental_pop[gbest_row, j] - experimental_pop[i, j])
    return modified_pop

# Acquiring Phase
def acquring_phase(modified_pop, pop, dim, gbest_list_ip, gbest_row_ip):
    modified_popp = np.copy(modified_pop)
    for i in range(pop):
        other_Xr = [index for index in range(pop) if index != i]
        Xr_row = random.choice(other_Xr)
        Xr = random.choice(modified_pop[Xr_row])
        fXr = gbest_list_ip[Xr_row]
        fXi = gbest_list_ip[i]

        for j in range(dim):
            rdm1 = random.random()
            rdm2 = random.random()
            if fXi < fXr:
                modified_popp[i, j] = modified_pop[i, j] + rdm1 * (modified_pop[i, j] - modified_pop[Xr_row, j]) + rdm2 * (modified_pop[gbest_row_ip, j] - modified_pop[i, j])
            else:                        
                modified_popp[i, j] = modified_pop[i, j] + rdm1 * (modified_pop[Xr_row, j] - modified_pop[i, j]) + rdm2 * (modified_pop[gbest_row_ip, j] - modified_pop[i, j])
    return modified_popp

# Find gbest
def find_gbest(objective_pop, pop):
    gbest_list = [sum(x for x in objective_pop[i]) for i in range(pop)]
    if not gbest_list:
        return None, None, None
    gbest = min(gbest_list)
    gbest_row = gbest_list.index(gbest)
    return gbest_list, gbest, gbest_row

plot_canvas = None

# Run Optimization
def run_optimization():
    global plot_canvas 
    pop = int(pop_entry.get())
    dim_cost = int(dim_cost_entry.get())
    trp = int(trp_entry.get())
    itr = int(itr_entry.get())
    constant = 0.5


    # Initialize random population
    initial_fare = np.random.randint(2500, 1000000, size=(pop, 2)).astype(float)
    experimetal_fare = np.copy(initial_fare)
    initial_cost = np.random.randint(400000, 35000000, size=(pop, dim_cost)).astype(float)
    experimetal_cost = np.copy(initial_cost)
    initial_fki_cost = np.random.randint(0, 2, size=(pop, dim_cost))
    initial_takeoff_time = (np.sort(np.random.rand(pop, 2) * 24, axis=1)).astype(float)
    experimetal_takeoff_time = np.copy(initial_takeoff_time)
    initial_duration = (np.random.rand(pop, 2) * 22 + 2).astype(float)
    experimetal_duration = np.copy(initial_duration)

    # Objective Function
    objective_pop = Objective_Function(initial_fare, initial_cost, initial_takeoff_time, initial_duration, initial_fki_cost, pop, dim_cost, trp)
    gbest_list0, gbest0, gbest_row = find_gbest(objective_pop, pop)

    if gbest_list0 is None:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Error: Unable to find gbest.")
        return

    gbest_values = [gbest0]
    print(f"gbest at 0th Iteration (Initialization) : {gbest0}")
    print(f"Corresponding Flight Type : {gbest_row + 1}")

    # Iterative Optimization
    for count in range(itr):
        print(f"ITERATION : {count + 1}")
        z = 0
        c = 0
        while z == 0:
            c += 1
            modified_cost_pop = improving_phase(experimetal_cost, pop, dim_cost, gbest_row)
            modified_fare_pop = improving_phase(experimetal_fare, pop, dim=2, gbest_row=gbest_row)
            modified_takeoff_pop = improving_phase(experimetal_takeoff_time, pop, dim=2, gbest_row=gbest_row)
            modified_duration_pop = improving_phase(experimetal_duration, pop, dim=2, gbest_row=gbest_row)
            modified_objective_pop = Objective_Function(modified_fare_pop, modified_cost_pop, modified_takeoff_pop, modified_duration_pop, initial_fki_cost, pop, dim_cost, trp)
            gbest_list_ip, gbest_ip, gbest_row_ip = find_gbest(modified_objective_pop, pop)
            if gbest_list_ip is None:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "Error: Unable to find gbest.")
                return
            if gbest_ip < gbest0 and gbest_ip > 0:
                print(f"Improving Phase Accepted after {c} Attempt and gbest at This Stage : {gbest_ip}")
                z = 1
            else:
                z = 0

        z = 0
        c = 0
        while z == 0:
            c += 1
            modified_cost_popp = acquring_phase(modified_cost_pop, pop, dim_cost, gbest_list_ip, gbest_row_ip)
            modified_fare_popp = acquring_phase(modified_fare_pop, pop, dim=2, gbest_list_ip=gbest_list_ip, gbest_row_ip=gbest_row_ip)
            modified_takeoff_popp = acquring_phase(modified_takeoff_pop, pop, dim=2, gbest_list_ip=gbest_list_ip, gbest_row_ip=gbest_row_ip)
            modified_duration_popp = acquring_phase(modified_duration_pop, pop, dim=2, gbest_list_ip=gbest_list_ip, gbest_row_ip=gbest_row_ip)
            modified_objective_popp = Objective_Function(modified_fare_popp, modified_cost_popp, modified_takeoff_popp, modified_duration_popp, initial_fki_cost, pop, dim_cost, trp)
            gbest_list_ap, gbest_ap, gbest_row_ap = find_gbest(modified_objective_popp, pop)
            if gbest_list_ap is None:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "Error: Unable to find gbest.")
                return
            if gbest_ap < gbest_ip and gbest_ap > 0:
                print(f"Acquiring Phase Accepted after {c} Attempt and gbest at This Stage : {gbest_ap}")
                z = 1
            else:
                z = 0

        print(f"gbest at Iteration {count + 1} : {gbest_ap}")
        gbest_values.append(gbest_ap)
        print(f"Corresponding Flight Type : {gbest_row_ap + 1}")

        experimetal_cost = modified_cost_popp
        experimetal_fare = modified_fare_popp
        experimetal_takeoff_time = modified_takeoff_popp
        experimetal_duration = modified_duration_popp

        gbest_row = gbest_row_ap

    # Display Results
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"RESCHEDULED FLIGHT DETAILS:\n\n")
    result_text.insert(tk.END, f"FLIGHT TYPE : {gbest_row + 1}\n")
    result_text.insert(tk.END, f"TRAVEL FARE : {initial_fare[gbest_row][1]}\n")
    hrs = int(initial_duration[gbest_row][1])
    min = (initial_duration[gbest_row][1] - hrs) * 60
    sec = (min - int(min)) * 60
    result_text.insert(tk.END, f"TOTAL DURATION : {hrs} hours {int(min)} minutes {round(sec)} seconds\n")
    hour = int(initial_takeoff_time[gbest_row][1])
    minute = (initial_takeoff_time[gbest_row][1] - hour) * 60
    second = (minute - int(minute)) * 60
    period = " AM" if hour < 12 else " PM"
    hour = hour if hour <= 12 else (hour - 12)
    minute = int(minute)
    second = round(second)
    result_text.insert(tk.END, f"TAKEOFF TIME : {hour} : {minute:02d} : {second:02d}{period}\n")
    gb_row = initial_fki_cost[gbest_row]
    flight_legs = [col_index + 1 for col_index, value in enumerate(gb_row) if value == 1]
    result_text.insert(tk.END, f"INVOLVED FLIGHT LEGS : {flight_legs}\n")
    capacity = [0] * len(flight_legs)
    for i in range(len(flight_legs)):
        capacity[i] = np.random.randint(15, 30)
    for i in range(len(flight_legs)):
        result_text.insert(tk.END, f"NUMBER OF ACCOMODATED PASSENGERS IN FLIGHT LEG {flight_legs[i]} : {capacity[i]}\n")
    left = trp
    for i in range(len(flight_legs)):
        left -= capacity[i]
    if left < 0:
        left = 0
    result_text.insert(tk.END, f"PASSENGERS WE FAILED TO ACCOMODATE : {left}\n")
    result_text.insert(tk.END, f"INVOLVED FLIGHT LEGS : {flight_legs}\n")
    result_text.insert(tk.END, f"TOTAL OPERATIONAL COST : {initial_cost[gbest_row][1]}")
    print(initial_takeoff_time)
    
    # Plotting
    smoothed_iterations = list(range(len(gbest_values)))
    smoothed_SGO = gbest_values

    plot_figure = plt.Figure(figsize=(5, 0.9))
    ax = plot_figure.add_subplot(111)

    # Clear previous canvas if it exists
    if plot_canvas:
        plot_canvas.get_tk_widget().pack_forget()
        plot_canvas.get_tk_widget().destroy()
        plot_canvas = None

    # Plotting on the specific Tkinter figure
    ax.plot(smoothed_iterations, smoothed_SGO, label='Flight Rescheduling by SGO')
    ax.set_title('Iteration vs Fitness Value')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Fitness Value')
    ax.legend()
    ax.grid(True)

    # Display the updated plot in the GUI
    plot_canvas = FigureCanvasTkAgg(plot_figure, master=result_frame)
    plot_canvas.draw()
    plot_canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


# Create the GUI
root = tk.Tk()
root.title("Flight Delay SGO")

# Input fields
input_frame = tk.Frame(root)
input_frame.pack(pady=20)

pop_label = tk.Label(input_frame, text="Enter the Number of Different Types of Flights Available:")
pop_label.grid(row=0, column=0, padx=10, pady=5)
pop_entry = tk.Entry(input_frame)
pop_entry.grid(row=0, column=1, padx=10, pady=5)

dim_cost_label = tk.Label(input_frame, text="Enter the Total Number of Flight Legs Available:")
dim_cost_label.grid(row=1, column=0, padx=10, pady=5)
dim_cost_entry = tk.Entry(input_frame)
dim_cost_entry.grid(row=1, column=1, padx=10, pady=5)

trp_label = tk.Label(input_frame, text="Enter the Number of Redirected Passengers:")
trp_label.grid(row=2, column=0, padx=10, pady=5)
trp_entry = tk.Entry(input_frame)
trp_entry.grid(row=2, column=1, padx=10, pady=5)

itr_label = tk.Label(input_frame, text="Enter the Number of Iteration:")
itr_label.grid(row=3, column=0, padx=10, pady=5)
itr_entry = tk.Entry(input_frame)
itr_entry.grid(row=3, column=1, padx=10, pady=5)

run_button = tk.Button(root, text="Run Optimization", command=run_optimization)
run_button.pack(pady=10)

# Result text box and plot
result_frame = tk.Frame(root)
result_frame.pack(pady=20)

result_label = tk.Label(result_frame, text="")
result_label.pack(side=tk.TOP, anchor=tk.W)

result_text = tk.Text(result_frame, width=100, height=25)
result_text.pack(side=tk.LEFT)

scrollbar = tk.Scrollbar(result_frame, command=result_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
result_text.config(yscrollcommand=scrollbar.set)

root.mainloop()