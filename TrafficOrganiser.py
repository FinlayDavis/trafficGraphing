import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from tkinter import Tk, ttk, Label, Entry, Button, StringVar, IntVar, BooleanVar, OptionMenu, Checkbutton, filedialog, messagebox, DISABLED, NORMAL

def filter_and_group_data(data, directions, hour, column):
    # Filter the data for the specified direction(s) and hour
    filtered_data = data[(data['direction_of_travel'].isin(directions)) & (data['hour'] == hour)]
    
    # Group by year and direction and sum the selected column for each year
    yearly_data = filtered_data.groupby(['year', 'direction_of_travel'])[column].sum().reset_index()
    return yearly_data

def calculate_percentage_data(data, directions, hour, column1, column2):
    yearly_data1 = filter_and_group_data(data, directions, hour, column1)
    yearly_data2 = filter_and_group_data(data, directions, hour, column2)
    
    percentage_data = []
    for year in yearly_data1['year'].unique():
        for direction in directions:
            dir_data1 = yearly_data1[(yearly_data1['year'] == year) & (yearly_data1['direction_of_travel'] == direction)]
            dir_data2 = yearly_data2[(yearly_data2['year'] == year) & (yearly_data2['direction_of_travel'] == direction)]
            if not dir_data1.empty and not dir_data2.empty:
                y1 = dir_data1[column1].values[0]
                y2 = dir_data2[column2].values[0]
                percentage = (y2 / y1) * 100 if y1 != 0 else 0
                percentage_data.append({'year': year, 'direction': direction, column1: y1, column2: y2, 'percentage': percentage})
    return pd.DataFrame(percentage_data)

def plot_motor_vehicles(filename, directions, hour, column1, column2):
    # Read the CSV file
    data = pd.read_csv(filename, delimiter=',')
    
    # Get the road name from column J
    road_name = data['road_name'].iloc[0] if 'road_name' in data.columns else "Unknown Road"
    
    # Calculate the percentage data
    percentage_df = calculate_percentage_data(data, directions, hour, column1, column2)
    
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the data
    for direction in directions:
        dir_data1 = percentage_df[percentage_df['direction'] == direction]
        ax.plot(dir_data1['year'], dir_data1[column1], marker='o', linestyle='-', label=f'{direction} - {column1} - Hour {hour}')
        
        if enable_column2.get():
            ax.plot(dir_data1['year'], dir_data1[column2], marker='o', linestyle='-', label=f'{direction} - {column2} - Hour {hour}')
    ax.set_title(f'{road_name} - {column1.replace("_", " ").title()} in Hour {hour}')
  
    # Create a table for percentages with years as column headers and directions as row headers
    if enable_column2.get():
        table_data = []
        years = percentage_df['year'].unique()
        col_labels = [''] + [f"{year}" for year in years]
        
        for direction in directions:
            row = [f"{direction}"]
            for year in years:
                dir_data = percentage_df[(percentage_df['year'] == year) & (percentage_df['direction'] == direction)]
                if not dir_data.empty:
                    row.append(f"{dir_data['percentage'].values[0]:.1f}%")
                else:
                    row.append("N/A")
            table_data.append(row)
        
        table = ax.table(cellText=table_data, colLabels=col_labels, loc='bottom', cellLoc='center', bbox=[0.0, -0.6, 1.0, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        
        # Add heading for the table
        heading = f"Percentage of {column2.replace('_', ' ')} / {column1.replace('_', ' ')}"
        ax.text(0.5, -0.23, heading, ha='center', va='center', transform=ax.transAxes, fontsize=10)
        
        fig.subplots_adjust(bottom=0.35)
    
        ax.set_title(f'{road_name} - Comparison of {column1.replace("_", " ").title()} and {column2.replace("_", " ").title()} in Hour {hour}')
    ax.set_xlabel('Year')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel('Number of Vehicles')
    ax.grid(True)
    ax.legend()
    plt.show()

def save_filtered_data(filename, directions, hour, column1, column2, save_filename):
    # Read the CSV file
    data = pd.read_csv(filename, delimiter=',')

    # Save the combined data to a CSV file
    try:
        if enable_column2.get():
            # Calculate the percentage data
            percentage_df = calculate_percentage_data(data, directions, hour, column1, column2)
            percentage_df.to_csv(save_filename, index=False)
        else:
            yearly_data1 = filter_and_group_data(data, directions, hour, column1) 
            yearly_data1.to_csv(save_filename, index=False) 
        messagebox.showinfo("Save Successful", f"Filtered data saved to {save_filename}")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Failed to save file: {e}")

def browse_file():
    file_path = filedialog.askopenfilename()
    filename.set(file_path)
    update_columns(file_path)
    enable_menus()

def save_file():
    save_filename.set(filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[("CSV files", "*.csv")]))
    print(f"Save file path set to: {save_filename.get()}")  # Debugging output
    save_button.config(state=NORMAL)

def update_columns(file_path):
    try:
        data = pd.read_csv(file_path, delimiter=',')
        # Display columns starting from column T onwards (index 19 onwards)
        columns = data.columns.tolist()[19:]
        column_choice1.set(columns[-1])  # Default to the first column
        column_choice2.set(columns[-2])  # Default to the second column
        column_menu1['values'] = columns
        column_menu2['values'] = columns
        
        # Get unique directions from column B
        available_directions = data['direction_of_travel'].unique().tolist()
        
        # Enable/disable checkboxes based on available directions
        for direction in ["N", "S", "E", "W"]:
            if direction in available_directions:
                direction_vars[direction].set(1)
                direction_checkbuttons[direction].config(state=NORMAL)
            else:
                direction_vars[direction].set(0)
                direction_checkbuttons[direction].config(state=DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load columns: {e}")

def enable_menus():
    hour_entry.config(state=NORMAL)
    column_menu1.config(state=NORMAL)
    save_entry.config(state=NORMAL)
    save_as_button.config(state=NORMAL)
    plot_button.config(state=NORMAL)
    enable_c2_button.config(state=NORMAL)
    
def get_selected_directions():
    return [direction for direction, var in direction_vars.items() if var.get() == 1]

def toggle_column2():
    if enable_column2.get():
        column_menu2.config(state=NORMAL)
    else:
        column_menu2.config(state=DISABLED)

def create_gui():
    root = Tk()
    root.title("Traffic Data Plotter")
    
    global filename, save_filename, direction_vars, direction_checkbuttons, column_choice1, column_choice2, column_menu1, column_menu2, hour_entry, save_entry, save_button, save_as_button, plot_button, enable_column2, enable_c2_button
    filename = StringVar()
    save_filename = StringVar()

    direction_vars = {direction: IntVar() for direction in ["N", "S", "E", "W"]}
    hour = IntVar(value=8)

    column_choice1 = StringVar()
    column_choice2 = StringVar()
    enable_column2 = BooleanVar()
    
    Label(root, text="Filename:").grid(row=0, column=0, padx=10, pady=10)
    Entry(root, textvariable=filename, width=50).grid(row=0, column=1, columnspan=3, padx=10, pady=10)
    Button(root, text="Browse", command=browse_file).grid(row=0, column=4, padx=10, pady=10)
    
    Label(root, text="Direction:").grid(row=1, column=0, padx=10, pady=10) 
    direction_checkbuttons = {} 
    for i, direction in enumerate(["N", "S", "E", "W"]): 
        direction_checkbuttons[direction] = Checkbutton(root, text=direction, variable=direction_vars[direction], state=DISABLED) 
        direction_checkbuttons[direction].grid(row=1, column=i+1, padx=20, pady=10) # Adjust padx for spacing

    Label(root, text="Hour:").grid(row=2, column=0, padx=10, pady=10)
    hour_entry = Entry(root, textvariable=hour, state=DISABLED)
    hour_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=10)
    
    Label(root, text="Column 1 to Plot:").grid(row=3, column=0, padx=10, pady=10)
    column_menu1 = ttk.Combobox(root, textvariable=column_choice1, state='readonly')
    column_menu1.config(state=DISABLED)
    column_menu1.grid(row=3, column=1, columnspan=2, padx =10, pady=10)
    
    Label(root, text="Column 2 to Plot:").grid(row=4, column=0, padx=10, pady=10)
    column_menu2 = ttk.Combobox(root, textvariable=column_choice2, state='readonly')
    column_menu2.config(state=DISABLED)
    column_menu2.grid(row=4, column=1, columnspan=2, padx=10, pady=10)

    enable_c2_button = Checkbutton(root, text="Enable Column 2", variable=enable_column2, command=toggle_column2, state=DISABLED)
    enable_c2_button.grid(row=3, column=3, columnspan=2, padx=10, pady=10)

    Label(root, text="Save Filtered Data:").grid(row=5, column=0, padx=10, pady=10) 
    save_entry = Entry(root, textvariable=save_filename, width=50, state=DISABLED) 
    save_entry.grid(row=5, column=1, columnspan=3, padx=10, pady=10) 
    save_as_button = Button(root, text="Save As", command=save_file, state=DISABLED) 
    save_as_button.grid(row=5, column=4, padx=10, pady=10)
    
    plot_button = Button(root, text="      Plot      ", command=lambda: plot_motor_vehicles(filename.get(), get_selected_directions(), hour.get(), column_choice1.get(), column_choice2.get()), state=DISABLED) 
    plot_button.grid(row=4, column=3, padx=10, pady=10) 
    save_button = Button(root, text="Save", command=lambda: save_filtered_data(filename.get(), get_selected_directions(), hour.get(), column_choice1.get(), column_choice2.get(), save_filename.get()), state=DISABLED) 
    save_button.grid(row=6, column=4, padx=10, pady=10)

    root.mainloop()

# Run the GUI
create_gui()
