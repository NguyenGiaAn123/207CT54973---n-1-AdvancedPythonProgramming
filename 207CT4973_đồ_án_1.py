import tkinter as tk
from tkinter import messagebox

#Hàm kiểm tra đầu vào, chỉ cho phép nhập số
def validate_input(char):
    if char.isdigit() or char == ".":
        return True
    return False

#Hàm xử lý khi nhấn từ bàn phím
def on_enter_a(event=None):
    entry_b.focus_set()

def on_enter_b(event=None):
    operation_menu.focus_set()

def change_operation(event):
    current_op = operation_var.get()
    operations = ["+", "-", "*", "/"]
    current_index = operations.index(current_op)
    
    if event.keysym == "Up":
        # Chọn phép tính trước đó (vòng về cuối nếu đang là phép đầu)
        new_index = (current_index - 1) % len(operations)
    elif event.keysym == "Down":
        # Chọn phép tính tiếp theo (vòng về đầu nếu đang là phép cuối)
        new_index = (current_index + 1) % len(operations)
    
    # Cập nhật phép tính được chọn
    operation_var.set(operations[new_index])

def focus_on_input(event):
    if event.keysym == "a" and event.state & 0x1:  # Kiểm tra nếu Ctrl + A được nhấn
        entry_a.focus_set()    
    elif event.keysym == "b" and event.state & 0x1:  # Kiểm tra nếu Ctrl + B được nhấn
        entry_b.focus_set()           

# Hàm xử lý di chuyển focus giữa các ô nhập liệu a và b bằng phím mũi tên
def move_focus(event):
    if event.widget == entry_a and event.keysym == "Down":
        entry_b.focus_set()  # Di chuyển focus từ a xuống b
    elif event.widget == entry_b and event.keysym == "Up":
        entry_a.focus_set()  # Di chuyển focus từ b lên a

# Hàm thực hiện phép tính dựa vào chế độ mà người dùng chọn
def calculate(event=None):
    try:
        # Lấy giá trị a và b từ các ô nhập liệu
        a = float(entry_a.get())
        b = float(entry_b.get())

        # Kiểm tra phép tính được chọn
        operation = operation_var.get()

        if operation == "+":
            result = a + b
        elif operation == "-":
            result = a - b
        elif operation == "*":
            result = a * b
        elif operation == "/":
            # Kiểm tra chia cho 0
            if b == 0:
                messagebox.showerror("Lỗi", "Không thể chia cho 0!")
                return
            result = a / b
        else:
            result = "Chọn phép tính hợp lệ!"
        
        # Hiển thị kết quả
        messagebox.showinfo("Kết quả", f"Kết quả của phép tính là: {result}")

    except ValueError:
        # Hiển thị lỗi nếu người dùng nhập sai kiểu số
        messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")

# Tạo cửa sổ chính
win = tk.Tk()
win.title("Máy tính đơn giản")

#kiểm tra đầu vào của Entry
validate_command = win.register(validate_input)

win.resizable(True,True)
# Tạo các nhãn và ô nhập liệu cho a và b
label_a = tk.Label(win, text="Nhập a:")
label_a.grid(row=0, column=0)
entry_a = tk.Entry(win, validate="key", validatecommand=(validate_command, '%S'))
entry_a.grid(row=0, column=1)

label_b = tk.Label(win, text="Nhập b:")
label_b.grid(row=1, column=0)
entry_b = tk.Entry(win, validate="key", validatecommand=(validate_command, '%S'))
entry_b.grid(row=1, column=1)

# Tạo tùy chọn cho các phép tính
operation_var = tk.StringVar(value="+")
operation_label = tk.Label(win, text="Chọn phép tính:")
operation_label.grid(row=2, column=0)
operation_menu = tk.OptionMenu(win, operation_var, "+", "-", "*", "/")
operation_menu.grid(row=2, column=1)

# Tạo nút để thực hiện phép tính
calc_button = tk.Button(win, text="Tính", command=calculate)
calc_button.grid(row=3, column=0, columnspan=2)


# Gán sự kiện từ bàn phím
entry_a.bind('<Return>', on_enter_a)
entry_b.bind('<Return>', on_enter_b)
entry_a.bind('<Down>', move_focus)
entry_b.bind('<Up>', move_focus)
operation_menu.bind('<Return>', calculate)
operation_menu.bind('<Up>', change_operation)
operation_menu.bind('<Down>', change_operation)
win.bind('<Key>', focus_on_input)

# Bắt đầu vòng lặp giao diện
entry_a.focus_set()
win.mainloop()