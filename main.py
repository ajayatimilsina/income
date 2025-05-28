import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import pandas as pd
from tkinter import filedialog
import matplotlib.pyplot as plt

DB_NAME = 'finance.db'

# Database setup
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    category TEXT,
    date TEXT,
    amount REAL,
    remarks TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    category TEXT,
    date TEXT,
    amount REAL,
    remarks TEXT
)''')
conn.commit()
conn.close()

class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Income & Expenses Manager')
        self.geometry('900x600')
        self.configure(bg='#f4f6fb')
        self.create_widgets()

    def create_widgets(self):
        tab_control = ttk.Notebook(self)
        self.dashboard_tab = ttk.Frame(tab_control)
        self.income_tab = ttk.Frame(tab_control)
        self.expenses_tab = ttk.Frame(tab_control)
        tab_control.add(self.dashboard_tab, text='Dashboard')
        tab_control.add(self.income_tab, text='Income')
        tab_control.add(self.expenses_tab, text='Expenses')
        tab_control.pack(expand=1, fill='both')
        self.create_dashboard()
        self.create_income_tab()
        self.create_expenses_tab()

    def create_dashboard(self):
        self.total_income_var = tk.StringVar()
        self.total_expenses_var = tk.StringVar()
        self.balance_var = tk.StringVar()
        tk.Label(self.dashboard_tab, text='Dashboard', font=('Arial', 22, 'bold'), bg='#f4f6fb').pack(pady=20)
        frame = tk.Frame(self.dashboard_tab, bg='#f4f6fb')
        frame.pack(pady=10)
        tk.Label(frame, text='Total Income:', font=('Arial', 16), bg='#f4f6fb').grid(row=0, column=0, padx=20, pady=10)
        tk.Label(frame, textvariable=self.total_income_var, font=('Arial', 16, 'bold'), fg='green', bg='#f4f6fb').grid(row=0, column=1)
        tk.Label(frame, text='Total Expenses:', font=('Arial', 16), bg='#f4f6fb').grid(row=1, column=0, padx=20, pady=10)
        tk.Label(frame, textvariable=self.total_expenses_var, font=('Arial', 16, 'bold'), fg='red', bg='#f4f6fb').grid(row=1, column=1)
        tk.Label(frame, text='Balance:', font=('Arial', 16), bg='#f4f6fb').grid(row=2, column=0, padx=20, pady=10)
        tk.Label(frame, textvariable=self.balance_var, font=('Arial', 16, 'bold'), fg='blue', bg='#f4f6fb').grid(row=2, column=1)
        tk.Button(self.dashboard_tab, text='Show Chart', command=self.show_chart, bg='#673ab7', fg='white', font=('Arial', 12), width=15).pack(pady=20)
        self.update_dashboard()

    def update_dashboard(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM income')
        total_income = c.fetchone()[0] or 0
        c.execute('SELECT SUM(amount) FROM expenses')
        total_expenses = c.fetchone()[0] or 0
        conn.close()
        self.total_income_var.set(f'{total_income:.2f}')
        self.total_expenses_var.set(f'{total_expenses:.2f}')
        self.balance_var.set(f'{total_income - total_expenses:.2f}')

    def create_income_tab(self):
        self.income_entries = {}
        self.create_entry_tab(self.income_tab, 'income', self.income_entries)

    def create_expenses_tab(self):
        self.expenses_entries = {}
        self.create_entry_tab(self.expenses_tab, 'expenses', self.expenses_entries)

    def create_entry_tab(self, tab, table, entries_dict):
        form_frame = tk.Frame(tab, bg='#f4f6fb')
        form_frame.pack(pady=10)
        labels = ['Title', 'Category', 'Date (YYYY-MM-DD)', 'Amount', 'Remarks']
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, font=('Arial', 12), bg='#f4f6fb').grid(row=i, column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(form_frame, font=('Arial', 12), width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries_dict[label] = entry
        btn_frame = tk.Frame(form_frame, bg='#f4f6fb')
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text='Add', command=lambda: self.add_entry(table, entries_dict), bg='#4caf50', fg='white', font=('Arial', 11), width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Update', command=lambda: self.update_entry(table, entries_dict), bg='#2196f3', fg='white', font=('Arial', 11), width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Delete', command=lambda: self.delete_entry(table), bg='#f44336', fg='white', font=('Arial', 11), width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Clear', command=lambda: self.clear_form(entries_dict), bg='#9e9e9e', fg='white', font=('Arial', 11), width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Export Excel', command=lambda: self.export_to_excel(table), bg='#ff9800', fg='white', font=('Arial', 11), width=12).pack(side='left', padx=5)
        search_frame = tk.Frame(tab, bg='#f4f6fb')
        search_frame.pack(pady=5)
        tk.Label(search_frame, text='Search:', font=('Arial', 12), bg='#f4f6fb').pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 12), width=30)
        search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text='Search', command=lambda: self.search_entries(table), bg='#607d8b', fg='white', font=('Arial', 11), width=10).pack(side='left', padx=5)
        columns = ('id', 'title', 'category', 'date', 'amount', 'remarks')
        self.tree = ttk.Treeview(tab, columns=columns, show='headings', height=12)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=120)
        self.tree.pack(pady=10, fill='x')
        self.tree.bind('<<TreeviewSelect>>', lambda event: self.on_tree_select(event, entries_dict))
        self.load_entries(table)

    def add_entry(self, table, entries_dict):
        data = [entries_dict[label].get() for label in ['Title', 'Category', 'Date (YYYY-MM-DD)', 'Amount', 'Remarks']]
        if not all(data[:4]):
            messagebox.showerror('Error', 'Please fill all required fields.')
            return
        try:
            datetime.strptime(data[2], '%Y-%m-%d')
            amount = float(data[3])
        except ValueError:
            messagebox.showerror('Error', 'Invalid date or amount.')
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f'INSERT INTO {table} (title, category, date, amount, remarks) VALUES (?, ?, ?, ?, ?)', data)
        conn.commit()
        conn.close()
        self.load_entries(table)
        self.update_dashboard()
        self.clear_form(entries_dict)
        messagebox.showinfo('Success', 'Entry added successfully!')

    def load_entries(self, table):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f'SELECT * FROM {table}')
        for row in c.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

    def on_tree_select(self, event, entries_dict):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            labels = ['Title', 'Category', 'Date (YYYY-MM-DD)', 'Amount', 'Remarks']
            for i, label in enumerate(labels):
                entries_dict[label].delete(0, tk.END)
                entries_dict[label].insert(0, values[i+1])
            self.selected_id = values[0]
        else:
            self.selected_id = None

    def update_entry(self, table, entries_dict):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            messagebox.showerror('Error', 'No entry selected.')
            return
        data = [entries_dict[label].get() for label in ['Title', 'Category', 'Date (YYYY-MM-DD)', 'Amount', 'Remarks']]
        if not all(data[:4]):
            messagebox.showerror('Error', 'Please fill all required fields.')
            return
        try:
            datetime.strptime(data[2], '%Y-%m-%d')
            amount = float(data[3])
        except ValueError:
            messagebox.showerror('Error', 'Invalid date or amount.')
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f'UPDATE {table} SET title=?, category=?, date=?, amount=?, remarks=? WHERE id=?', (*data, self.selected_id))
        conn.commit()
        conn.close()
        self.load_entries(table)
        self.update_dashboard()
        self.clear_form(entries_dict)
        messagebox.showinfo('Success', 'Entry updated successfully!')

    def delete_entry(self, table):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            messagebox.showerror('Error', 'No entry selected.')
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f'DELETE FROM {table} WHERE id=?', (self.selected_id,))
        conn.commit()
        conn.close()
        self.load_entries(table)
        self.update_dashboard()
        self.clear_form()
        messagebox.showinfo('Success', 'Entry deleted successfully!')

    def clear_form(self, entries_dict):
        for entry in entries_dict.values():
            entry.delete(0, tk.END)
        self.selected_id = None

    def search_entries(self, table):
        query = self.search_var.get()
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table} WHERE title LIKE ? OR category LIKE ? OR remarks LIKE ?", (f'%{query}%', f'%{query}%', f'%{query}%'))
        for row in c.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

    def export_to_excel(self, table):
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
        conn.close()
        file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel Files', '*.xlsx')])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo('Export', f'{table.capitalize()} exported to Excel successfully!')

    def show_chart(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM income')
        total_income = c.fetchone()[0] or 0
        c.execute('SELECT SUM(amount) FROM expenses')
        total_expenses = c.fetchone()[0] or 0
        conn.close()
        labels = ['Income', 'Expenses']
        values = [total_income, total_expenses]
        colors = ['#4caf50', '#f44336']
        plt.figure(figsize=(6,4))
        plt.bar(labels, values, color=colors)
        plt.title('Income vs Expenses')
        plt.ylabel('Amount')
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    app = FinanceApp()
    app.mainloop()