from tkinter import *
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageColor  # Added ImageColor
import numpy as np

# Windows Setup
window = Tk()
window.iconbitmap("tiramisu_icon.ico")
window.resizable(False, False)
window.geometry('1350x700')
window.title("Tiramisu")

# Variables
pen_color = "black"
eraser_color = "white"
pixel_size = 10  # Size of each pixel
layers = []
layer_names = []
current_layer = None
canvas_width = 985  # Updated canvas width
canvas_height = 580  # Keep the height the same
lasso_points = []
lasso_active = False

# Modern dark theme colors
bg_color = "#2e2e2e"
button_bg = "#3e3e3e"
button_fg = "#ffffff"
highlight_bg = "#505050"
tool_frame_color = "#2a2a2a"

# Canvas management
def add_layer():
    global current_layer
    layer = Canvas(window, bg="white", bd=0, relief=FLAT, height=canvas_height, width=canvas_width, highlightthickness=0)
    layer.place(x=10, y=100)
    layer.image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))
    layer.draw = ImageDraw.Draw(layer.image)
    layer.bind("<B1-Motion>", Paint)
    layers.append(layer)
    layer_names.append(f"Layer {len(layer_names) + 1}")
    current_layer = layer
    update_layers_list()

def remove_layer():
    global current_layer
    if layers:
        index = layers.index(current_layer)
        layers.pop(index).destroy()
        layer_names.pop(index)
        current_layer = layers[-1] if layers else None
        update_layers_list()

def duplicate_layer():
    global current_layer
    if current_layer:
        new_layer = Canvas(window, bg="white", bd=0, relief=FLAT, height=canvas_height, width=canvas_width, highlightthickness=0)
        new_layer.place(x=10, y=100)
        new_layer.image = current_layer.image.copy()
        new_layer.draw = ImageDraw.Draw(new_layer.image)
        new_layer.bind("<B1-Motion>", Paint)
        layers.append(new_layer)
        layer_names.append(f"Layer {len(layer_names) + 1}")
        current_layer = new_layer
        update_layers_list()

def update_layers_list():
    layer_list.delete(0, END)
    for i, name in enumerate(layer_names):
        layer_list.insert(END, name)
    if current_layer:
        layer_list.selection_set(layers.index(current_layer))

def select_layer(event):
    global current_layer
    selected = layer_list.curselection()
    if selected:
        current_layer = layers[selected[0]]

def merge_layers():
    if len(layers) > 1:
        base_layer = layers[0]
        base_image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))
        for layer in layers:
            base_image.paste(layer.image, (0, 0), layer.image)
        base_layer.image = base_image
        base_layer.draw = ImageDraw.Draw(base_image)
        for layer in layers[1:]:
            layer.destroy()
        layers.clear()
        layer_names.clear()
        layers.append(base_layer)
        layer_names.append("Layer 1")
        current_layer = base_layer
        update_layers_list()

# Drawing on the current layer
def Paint(event):
    if current_layer and not lasso_active:
        x1 = (event.x // pixel_size) * pixel_size
        y1 = (event.y // pixel_size) * pixel_size
        x2 = x1 + pixel_size
        y2 = y1 + pixel_size
        current_layer.create_rectangle(x1, y1, x2, y2, fill=pen_color, outline=pen_color)
        current_layer.draw.rectangle([x1, y1, x2, y2], fill=pen_color, outline=pen_color)

def Erase():
    global pen_color
    pen_color = eraser_color

def Clear():
    if current_layer:
        current_layer.delete("all")
        current_layer.image.paste((255, 255, 255, 0), (0, 0, canvas_width, canvas_height))
        current_layer.draw = ImageDraw.Draw(current_layer.image)

def CanvasColor():
    global eraser_color
    color = colorchooser.askcolor()
    for layer in layers:
        layer.configure(bg=color[1])
    eraser_color = color[1]

def Save():
    if layers:
        base_image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))
        for layer in layers:
            base_image.paste(layer.image, (0, 0), layer.image)
        
        file_name = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_name:
            base_image.save(file_name, "PNG")
            messagebox.showinfo("Tiramisu", f"Image Saved as {file_name}")
    else:
        messagebox.showwarning("Tiramisu", "No layers to save")

def SelectColor(col):
    global pen_color
    pen_color = col

def choose_custom_color():
    global pen_color
    color = colorchooser.askcolor()[1]
    if color:
        pen_color = color
        custom_color_btn.config(bg=pen_color)

def rename_layer():
    if current_layer:
        try:
            selected_index = layers.index(current_layer)
            new_name = layer_name_entry.get()
            if new_name:
                layer_names[selected_index] = new_name
                update_layers_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename layer: {e}")

def lasso_select(event):
    global lasso_active, lasso_points
    lasso_active = True
    x, y = event.x, event.y
    lasso_points.append((x, y))
    if len(lasso_points) > 1:
        current_layer.create_line(lasso_points[-2], lasso_points[-1], fill="red")

def finalize_lasso(event):
    global lasso_active, lasso_points
    if lasso_points:
        lasso_active = False
        current_layer.create_polygon(lasso_points, outline="red", fill="")
        # Placeholder for cutting/copying the selected region
        lasso_points = []

# Bucket Paint Tool
def bucket_fill(event):
    if current_layer:
        x, y = event.x, event.y
        target_color = np.array(current_layer.image.getpixel((x, y)))
        fill_color = np.array(ImageColor.getrgb(pen_color))

        if np.array_equal(target_color, fill_color):
            return

        stack = [(x, y)]
        while stack:
            nx, ny = stack.pop()
            if 0 <= nx < canvas_width and 0 <= ny < canvas_height:
                current_color = np.array(current_layer.image.getpixel((nx, ny)))
                if np.array_equal(current_color, target_color):
                    current_layer.image.putpixel((nx, ny), tuple(fill_color))
                    stack.extend([(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)])

        # Update the canvas with the filled image
        img = ImageTk.PhotoImage(current_layer.image)
        current_layer.create_image(0, 0, image=img, anchor=NW)
        current_layer.image_tk = img  # Keep a reference to prevent garbage collection

# Frames
color_frame = LabelFrame(window, text="Color", relief=FLAT, bg=tool_frame_color, fg=button_fg, font=("Arial", 12))
color_frame.place(x=10, y=10, width=424, height=70)

tool_frame = LabelFrame(window, text="Tools", relief=FLAT, bg=tool_frame_color, fg=button_fg, font=("Arial", 12))
tool_frame.place(x=450, y=10, width=300, height=60)

size_frame = LabelFrame(window, text="Pixel Size", relief=FLAT, bg=tool_frame_color, fg=button_fg, font=("Arial", 12))
size_frame.place(x=770, y=10, width=224, height=60)

layer_frame = LabelFrame(window, text="Layers", relief=FLAT, bg=tool_frame_color, fg=button_fg, font=("Arial", 12))
layer_frame.place(x=1000, y=10, width=300, height=580)

# Layer listbox and buttons
layer_frame_content = Frame(layer_frame, bg=tool_frame_color)
layer_frame_content.pack(fill=BOTH, expand=True)

layer_list = Listbox(layer_frame_content, bg=tool_frame_color, fg=button_fg, selectbackground=highlight_bg, font=("Arial", 10))
layer_list.pack(side=LEFT, fill=BOTH, expand=True)

button_frame = Frame(layer_frame_content, bg=tool_frame_color)
button_frame.pack(side=RIGHT, fill=Y)

add_layer_btn = Button(button_frame, text="Add Layer", relief=FLAT, bg=button_bg, fg=button_fg, command=add_layer)
add_layer_btn.pack(fill=X, pady=5)

remove_layer_btn = Button(button_frame, text="Remove Layer", relief=FLAT, bg=button_bg, fg=button_fg, command=remove_layer)
remove_layer_btn.pack(fill=X, pady=5)

duplicate_layer_btn = Button(button_frame, text="Duplicate Layer", relief=FLAT, bg=button_bg, fg=button_fg, command=duplicate_layer)
duplicate_layer_btn.pack(fill=X, pady=5)

merge_layers_btn = Button(button_frame, text="Merge Layers", relief=FLAT, bg=button_bg, fg=button_fg, command=merge_layers)
merge_layers_btn.pack(fill=X, pady=5)

rename_layer_btn = Button(button_frame, text="Rename Layer", relief=FLAT, bg=button_bg, fg=button_fg, command=rename_layer)
rename_layer_btn.pack(fill=X, pady=5)

layer_name_entry = Entry(button_frame, bg=tool_frame_color, fg=button_fg, font=("Arial", 10))
layer_name_entry.pack(fill=X, pady=5)

# Add colors
colors = ["#000000", "#0019ff", "#ff0000", "#edff00", "#00ff19", "#ffffff"]

# Add color buttons
i = j = 0
for color in colors:
    Button(color_frame, bd=0, relief=FLAT, width=3, bg=color, command=lambda col=color: SelectColor(col)).grid(row=j, column=i, padx=5)
    i += 1

# Custom Color Button
custom_color_btn = Button(color_frame, text="Custom", relief=FLAT, bg=pen_color, fg=button_fg, command=choose_custom_color)
custom_color_btn.grid(row=1, column=0, columnspan=5, pady=5, sticky="ew")

# Tool Buttons
canvas_color_b1 = Button(tool_frame, text="Canvas", relief=FLAT, bg=button_bg, fg=button_fg, command=CanvasColor)
canvas_color_b1.grid(row=0, column=0, padx=5)

save_b2 = Button(tool_frame, text="Save", relief=FLAT, bg=button_bg, fg=button_fg, command=Save)
save_b2.grid(row=0, column=1, padx=5)

eraser_b3 = Button(tool_frame, text="Erase", relief=FLAT, bg=button_bg, fg=button_fg, command=Erase)
eraser_b3.grid(row=0, column=2, padx=5)

clear_b4 = Button(tool_frame, text="Clear", relief=FLAT, bg=button_bg, fg=button_fg, command=Clear)
clear_b4.grid(row=0, column=3, padx=5)

lasso_b5 = Button(tool_frame, text="Lasso", relief=FLAT, bg=button_bg, fg=button_fg, command=lambda: current_layer.bind("<Button-1>", lasso_select))
lasso_b5.grid(row=0, column=4, padx=5)

bucket_b6 = Button(tool_frame, text="Bucket", relief=FLAT, bg=button_bg, fg=button_fg, command=lambda: current_layer.bind("<Button-1>", bucket_fill))
bucket_b6.grid(row=0, column=5, padx=5)

# Pixel Size Control
pixel_size_scale = Scale(size_frame, orient=HORIZONTAL, from_=5, to=50, length=170, bg=tool_frame_color, fg=button_fg, troughcolor=highlight_bg, highlightbackground=bg_color)
pixel_size_scale.set(pixel_size)
pixel_size_scale.grid(row=0, column=0)

def update_pixel_size(event):
    global pixel_size
    pixel_size = pixel_size_scale.get()

pixel_size_scale.bind("<Motion>", update_pixel_size)

# Set the background color of the window
window.configure(bg=bg_color)

# Initialize with one layer
add_layer()

# Bind lasso finalize function
window.bind("<ButtonRelease-1>", finalize_lasso)

window.mainloop()
