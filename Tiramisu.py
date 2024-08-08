from tkinter import *
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw
import PIL.ImageGrab as ImageGrab

# Windows Setup
window = Tk()
window.geometry('1350x700')
window.title("Tiramisu")

# Variables
pen_color = "black"
eraser_color = "white"
pixel_size = 10  # Size of each pixel
layers = []
current_layer = None

# Modern dark theme colors
bg_color = "#2e2e2e"
button_bg = "#3e3e3e"
button_fg = "#ffffff"
highlight_bg = "#505050"
tool_frame_color = "#2a2a2a"

# Canvas management
def add_layer():
    global current_layer
    # Create a new canvas layer
    layer = Canvas(window, bg="white", bd=0, relief=FLAT, height=580, width=985, highlightthickness=0)
    layer.place(x=10, y=100)
    
    # Create an image for the new layer to store the drawing
    layer.image = Image.new("RGBA", (1325, 580), (255, 255, 255, 0))
    layer.draw = ImageDraw.Draw(layer.image)
    
    # Bind the Paint function to the new layer
    layer.bind("<B1-Motion>", Paint)
    
    layers.append(layer)
    current_layer = layer
    update_layers_list()

def remove_layer():
    global current_layer
    if layers:
        layer = layers.pop()
        layer.destroy()
        current_layer = layers[-1] if layers else None
        update_layers_list()

def duplicate_layer():
    global current_layer
    if current_layer:
        new_layer = Canvas(window, bg="white", bd=0, relief=FLAT, height=580, width=1325, highlightthickness=0)
        new_layer.place(x=10, y=100)
        
        # Copy image from current layer
        new_layer.image = current_layer.image.copy()
        new_layer.draw = ImageDraw.Draw(new_layer.image)
        
        # Bind the Paint function to the new layer
        new_layer.bind("<B1-Motion>", Paint)
        
        layers.append(new_layer)
        current_layer = new_layer
        update_layers_list()

def update_layers_list():
    layer_list.delete(0, END)
    for i, layer in enumerate(layers):
        layer_list.insert(END, f"Layer {i + 1}")
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
        base_image = Image.new("RGBA", (1325, 580), (255, 255, 255, 0))
        for layer in layers:
            base_image.paste(layer.image, (0, 0), layer.image)
        base_layer.image = base_image
        base_layer.draw = ImageDraw.Draw(base_image)
        for layer in layers[1:]:
            layer.destroy()
        layers.clear()
        layers.append(base_layer)
        current_layer = base_layer
        update_layers_list()

# Drawing on the current layer
def Paint(event):
    if current_layer:
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
        current_layer.image.paste((255, 255, 255, 0), (0, 0, 1325, 580))
        current_layer.draw = ImageDraw.Draw(current_layer.image)

# Canvas Configuration
def CanvasColor():
    global eraser_color
    color = colorchooser.askcolor()
    for layer in layers:
        layer.configure(bg=color[1])
    eraser_color = color[1]

def Save():
    file_name = filedialog.asksaveasfile(defaultextension=".jpg")
    if file_name:
        x = window.winfo_rootx() + layers[0].winfo_rootx()
        y = window.winfo_rooty() + layers[0].winfo_rooty()
        x1 = x + layers[0].winfo_width()
        y1 = y + layers[0].winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save(file_name)
        messagebox.showinfo("Tiramisu", "Image Saved as " + str(file_name))

def SelectColor(col):
    global pen_color
    pen_color = col

def choose_custom_color():
    global pen_color
    color = colorchooser.askcolor()[1]
    if color:
        pen_color = color
        custom_color_btn.config(bg=pen_color)

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

# Add colors
colors = ["#000000", "#0019ff", "#ff0000", "#edff00", "#00ff19", "#ffffff"]

# Add color buttons
i = j = 0
for color in colors:
    Button(color_frame, bd=0, relief=FLAT, width=3, bg=color, command=lambda col=color: SelectColor(col)).grid(row=j, column=i, padx=5)
    i += 1

# Custom Color Button
custom_color_btn = Button(color_frame, text="Custom", relief=FLAT, bg=pen_color, fg=button_fg, command=choose_custom_color)
custom_color_btn.grid(row=1, column=0, columnspan=6, pady=5, sticky="ew")

# Tool Buttons
canvas_color_b1 = Button(tool_frame, text="Canvas", relief=FLAT, bg=button_bg, fg=button_fg, command=CanvasColor)
canvas_color_b1.grid(row=0, column=0, padx=5)

save_b2 = Button(tool_frame, text="Save", relief=FLAT, bg=button_bg, fg=button_fg, command=Save)
save_b2.grid(row=0, column=1, padx=5)

eraser_b3 = Button(tool_frame, text="Erase", relief=FLAT, bg=button_bg, fg=button_fg, command=Erase)
eraser_b3.grid(row=0, column=2, padx=5)

clear_b4 = Button(tool_frame, text="Clear", relief=FLAT, bg=button_bg, fg=button_fg, command=Clear)
clear_b4.grid(row=0, column=3, padx=5)

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

window.mainloop()
