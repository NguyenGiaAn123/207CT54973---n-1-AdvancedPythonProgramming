import tkinter as tk
from tkinter import messagebox
import psycopg2
from psycopg2 import sql

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý Sinh Viên")

       # Database connection fields
        self.db_name = tk.StringVar(value='test')
        self.user = tk.StringVar(value='postgres')
        self.password = tk.StringVar(value='123456')
        self.host = tk.StringVar(value='localhost')
        self.port = tk.StringVar(value='5432')
        self.table_name = tk.StringVar(value='students')

        self.conn = None
        self.cur = None

        # Create frames for different sections
        self.connection_frame = tk.Frame(self.root)
        self.student_frame = tk.Frame(self.root)

        # Setup both frames
        self.setup_connection_frame()
        self.setup_student_frame()

        # Show the connection frame initially
        self.connection_frame.grid(row=0, column=0)

    def setup_connection_frame(self):
        tk.Label(self.connection_frame, text="DB Name:").grid(row=0, column=0)
        self.db_name_entry = tk.Entry(self.connection_frame, textvariable=self.db_name)
        self.db_name_entry.grid(row=0, column=1)

        tk.Label(self.connection_frame, text="User:").grid(row=1, column=0)
        self.user_entry = tk.Entry(self.connection_frame, textvariable=self.user)
        self.user_entry.grid(row=1, column=1)

        tk.Label(self.connection_frame, text="Password:").grid(row=2, column=0)
        self.password_entry = tk.Entry(self.connection_frame, show="*", textvariable=self.password)
        self.password_entry.grid(row=2, column=1)

        tk.Label(self.connection_frame, text="Host:").grid(row=3, column=0)
        self.host_entry = tk.Entry(self.connection_frame, textvariable=self.host)
        self.host_entry.grid(row=3, column=1)

        tk.Label(self.connection_frame, text="Port:").grid(row=4, column=0)
        self.port_entry = tk.Entry(self.connection_frame, textvariable=self.port)
        self.port_entry.grid(row=4, column=1)

        # Connect button
        tk.Button(self.connection_frame, text="Kết nối Database", command=self.connect_db).grid(row=5, column=0, columnspan=2)

    def setup_student_frame(self):
        # Input fields for student information
        tk.Label(self.student_frame, text="Tên:").grid(row=0, column=0)
        self.student_name = tk.Entry(self.student_frame)
        self.student_name.grid(row=0, column=1)

        tk.Label(self.student_frame, text="Tuổi:").grid(row=0, column=2)
        self.student_age = tk.Entry(self.student_frame)
        self.student_age.grid(row=0, column=3)

        tk.Label(self.student_frame, text="Giới tính:").grid(row=1, column=0)
        self.student_gender = tk.Entry(self.student_frame)
        self.student_gender.grid(row=1, column=1)

        tk.Label(self.student_frame, text="Ngành học:").grid(row=1, column=2)
        self.student_major = tk.Entry(self.student_frame)
        self.student_major.grid(row=1, column=3)

        # Buttons for CRUD operations
        tk.Button(self.student_frame, text="Thêm sinh viên", command=self.add_student).grid(row=2, column=0)
        tk.Button(self.student_frame, text="Cập nhật thông tin", command=self.update_student).grid(row=2, column=1)
        tk.Button(self.student_frame, text="Xóa sinh viên", command=self.delete_student).grid(row=2, column=2)
        tk.Button(self.student_frame, text="Tải lại danh sách", command=self.load_students).grid(row=2, column=3)

        # Student list
        self.student_listbox = tk.Listbox(self.student_frame, width=80)
        self.student_listbox.grid(row=3, column=0, columnspan=4)

        # Logout button to go back to connection page
        tk.Button(self.student_frame, text="Đăng xuất", command=self.logout).grid(row=4, column=0, columnspan=4)

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.db_name.get(),
                user=self.user.get(),
                password=self.password.get(),
                host=self.host.get(),
                port=self.port.get()
            )
            self.cur = self.conn.cursor()
            messagebox.showinfo("Thông báo", "Kết nối database thành công!")
            self.show_student_frame()  # Show the student frame upon successful connection
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối database: {e}")

    def add_student(self):
        if self.conn is None:
            messagebox.showerror("Lỗi", "Chưa kết nối database")
            return

        # Fetch data from form
        name = self.student_name.get()
        age = self.student_age.get()
        gender = self.student_gender.get()
        major = self.student_major.get()

        # Ensure that all fields are filled
        if not (name and age and gender and major):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
            return

        try:
            cur = self.conn.cursor()

            # Insert query
            insert_query = sql.SQL(
                "INSERT INTO {table} (name, age, gender, major) VALUES (%s, %s, %s, %s)"
            ).format(table=sql.Identifier(self.table_name.get()))

            # Execute the insert statement
            cur.execute(insert_query, (name, age, gender, major))
            self.conn.commit()
            cur.close()

            messagebox.showinfo("Thông báo", "Thêm sinh viên thành công")
            self.load_students()  # Reload the list of students after insertion

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm sinh viên: {e}")

    def update_student(self):
        """Update the selected student record in the database."""
        try:
            selected_student = self.student_listbox.get(tk.ACTIVE)
            student_id = selected_student.split('|')[0].strip()  # Extract student ID

            name = self.student_name.get()
            age = self.student_age.get()
            gender = self.student_gender.get()
            major = self.student_major.get()

            if not (name and age and gender and major):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
                return

            update_query = sql.SQL("UPDATE {table} SET name = %s, age = %s, gender = %s, major = %s WHERE id = %s"
            ).format(table=sql.Identifier(self.table_name.get()))

            self.cur.execute(update_query, (name, age, gender, major, student_id))
            self.conn.commit()
            messagebox.showinfo("Thông báo", "Cập nhật thành công")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật: {e}")

    def delete_student(self):
        """Delete the selected student from the database."""
        try:
            selected_student = self.student_listbox.get(tk.ACTIVE)
            student_id = selected_student.split('|')[0].strip()  # Extract student ID

            delete_query = sql.SQL("DELETE FROM {table} WHERE id = %s"
            ).format(table=sql.Identifier(self.table_name.get()))

            self.cur.execute(delete_query, (student_id,))
            self.conn.commit()
            messagebox.showinfo("Thông báo", "Xóa sinh viên thành công")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa sinh viên: {e}")

    def load_students(self):
        """Load all students from the database and display them in the listbox."""
        try:
            self.student_listbox.delete(0, tk.END)  # Clear current listbox entries

            select_query = sql.SQL("SELECT * FROM {table}").format(
                table=sql.Identifier(self.table_name.get())
            )
            self.cur.execute(select_query)
            rows = self.cur.fetchall()

            for row in rows:
                self.student_listbox.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sinh viên: {e}")

    def show_student_frame(self):
        """Hide the connection frame and show the student frame."""
        self.connection_frame.grid_forget()  # Hide connection frame
        self.student_frame.grid(row=0, column=0)  # Show student frame

    def logout(self):
        """Log out and go back to the connection page."""
        if self.conn:
            self.conn.close()
        self.student_frame.grid_forget()  # Hide student frame
        self.connection_frame.grid(row=0, column=0)  # Show connection frame

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()
