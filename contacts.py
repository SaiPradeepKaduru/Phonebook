import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

# ---------- Database Setup ----------
def init_db():
    db_exists = os.path.exists("contacts.db")
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    
    if not db_exists:
        cursor.execute('''
            CREATE TABLE contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        ''')
        conn.commit()
    else:
        # Ensure address column exists
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [col[1] for col in cursor.fetchall()]
        if "address" not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN address TEXT")
            conn.commit()

    conn.close()

# ---------- Contact Operations ----------
def add_contact():
    name = name_entry.get().strip()
    phone = phone_entry.get().strip()
    email = email_entry.get().strip()
    address = address_entry.get().strip()

    if not name:
        messagebox.showwarning("Input Error", "Name is required.")
        return

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                   (name, phone, email, address))
    conn.commit()
    conn.close()

    show_contacts()
    clear_entries()

def show_contacts():
    contact_list.delete(0, tk.END)
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    for row in cursor.fetchall():
        display = f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}"
        contact_list.insert(tk.END, display)
    conn.close()

def search_contact():
    query = search_entry.get().strip()
    contact_list.delete(0, tk.END)

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ?", 
                   ('%' + query + '%', '%' + query + '%'))
    for row in cursor.fetchall():
        display = f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}"
        contact_list.insert(tk.END, display)
    conn.close()

def delete_contact():
    selected = contact_list.curselection()
    if not selected:
        messagebox.showwarning("Select Contact", "Please select a contact to delete.")
        return
    contact_id = contact_list.get(selected[0]).split(" | ")[0]

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
    conn.commit()
    conn.close()

    show_contacts()
    clear_entries()

def load_contact():
    selected = contact_list.curselection()
    if not selected:
        messagebox.showwarning("Select Contact", "Please select a contact to edit.")
        return
    data = contact_list.get(selected[0]).split(" | ")
    contact_id_label.config(text=data[0])
    name_entry.delete(0, tk.END)
    name_entry.insert(0, data[1])
    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, data[2])
    email_entry.delete(0, tk.END)
    email_entry.insert(0, data[3])
    address_entry.delete(0, tk.END)
    address_entry.insert(0, data[4])

def update_contact():
    contact_id = contact_id_label.cget("text")
    if not contact_id:
        messagebox.showwarning("Update Error", "No contact loaded for editing.")
        return

    name = name_entry.get().strip()
    phone = phone_entry.get().strip()
    email = email_entry.get().strip()
    address = address_entry.get().strip()

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE contacts SET name=?, phone=?, email=?, address=?
        WHERE id=?
    """, (name, phone, email, address, contact_id))
    conn.commit()
    conn.close()

    clear_entries()
    show_contacts()
    contact_id_label.config(text="")

def clear_entries():
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    contact_id_label.config(text="")

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Contact Manager")
root.geometry("600x500")

# ID Label (for edit)
contact_id_label = tk.Label(root, text="", fg="grey")
contact_id_label.grid(row=0, column=1, sticky="w")

# Entry Fields
tk.Label(root, text="Name").grid(row=1, column=0, sticky="e", pady=2)
tk.Label(root, text="Phone").grid(row=2, column=0, sticky="e", pady=2)
tk.Label(root, text="Email").grid(row=3, column=0, sticky="e", pady=2)
tk.Label(root, text="Address").grid(row=4, column=0, sticky="e", pady=2)

name_entry = tk.Entry(root, width=40)
phone_entry = tk.Entry(root, width=40)
email_entry = tk.Entry(root, width=40)
address_entry = tk.Entry(root, width=40)

name_entry.grid(row=1, column=1, padx=10)
phone_entry.grid(row=2, column=1, padx=10)
email_entry.grid(row=3, column=1, padx=10)
address_entry.grid(row=4, column=1, padx=10)

# Buttons
tk.Button(root, text="Add Contact", width=15, command=add_contact).grid(row=5, column=0, pady=5)
tk.Button(root, text="Update Contact", width=15, command=update_contact).grid(row=5, column=1, pady=5, sticky="w")
tk.Button(root, text="Delete Contact", width=15, command=delete_contact).grid(row=6, column=0, pady=5)
tk.Button(root, text="Load for Edit", width=15, command=load_contact).grid(row=6, column=1, pady=5, sticky="w")

# Search Bar
tk.Label(root, text="Search").grid(row=7, column=0, sticky="e", pady=5)
search_entry = tk.Entry(root, width=30)
search_entry.grid(row=7, column=1, sticky="w")
tk.Button(root, text="Search", command=search_contact).grid(row=7, column=1, sticky="e", padx=10)

# Contact List
contact_list = tk.Listbox(root, width=85, height=12)
contact_list.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# Initialize Database and Load Contacts
init_db()
show_contacts()

# Start the GUI loop
root.mainloop()
