import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

STATUSES = ["Выдана", "На проверке", "Возвращена", "Требует ремонта"]
records = []
next_id = 1
selected_id = None


def find_record(rec_id):
    for rec in records:
        if rec["id"] == rec_id:
            return rec
    return None


def validate_inputs():
    game = game_entry.get().strip()
    table = table_entry.get().strip()
    guest = guest_entry.get().strip()
    issue_time = time_entry.get().strip()
    condition = condition_entry.get().strip()

    if not game or not table or not guest:
        messagebox.showwarning(
            "Неполные данные",
            "Заполните обязательные поля:\n— Название игры\n— Номер стола\n— Имя гостя",
        )
        return None

    if not issue_time:
        issue_time = datetime.now().strftime("%H:%M")
    if not condition:
        condition = "Полный комплект"

    return game, table, guest, issue_time, condition


def add_record():
    global next_id
    data = validate_inputs()
    if not data:
        return

    game, table, guest, issue_time, condition = data
    records.append({
        "id": next_id,
        "game": game,
        "table": table,
        "guest": guest,
        "time": issue_time,
        "condition": condition,
        "status": "Выдана",
    })
    next_id += 1
    refresh_table()
    clear_form()


def on_row_select(event=None):
    global selected_id
    selected = tree.selection()
    if not selected:
        return

    first_item, *_ = selected
    values = tree.item(first_item, "values")
    if not values:
        return

    rec_id_str, *_ = values
    rec_id = int(rec_id_str)
    rec = find_record(rec_id)
    if not rec:
        return

    selected_id = rec_id
    game_entry.delete(0, tk.END)
    game_entry.insert(0, rec["game"])
    table_entry.delete(0, tk.END)
    table_entry.insert(0, rec["table"])
    guest_entry.delete(0, tk.END)
    guest_entry.insert(0, rec["guest"])
    time_entry.delete(0, tk.END)
    time_entry.insert(0, rec["time"])
    condition_entry.delete(0, tk.END)
    condition_entry.insert(0, rec["condition"])
    status_label.config(text=f"Запись №{rec['id']} — {rec['status']}")


def update_record():
    if selected_id is None:
        messagebox.showwarning("Запись не выбрана", "Выберите строку в таблице для редактирования.")
        return

    data = validate_inputs()
    if not data:
        return

    rec = find_record(selected_id)
    if not rec:
        return

    rec["game"], rec["table"], rec["guest"], rec["time"], rec["condition"] = data
    refresh_table()
    clear_form()


def change_status(target_status):
    if selected_id is None:
        messagebox.showwarning("Запись не выбрана", "Выберите запись в таблице, чтобы изменить статус.")
        return

    rec = find_record(selected_id)
    if not rec:
        return

    current = rec["status"]
    allowed = (current == "Выдана" and target_status == "На проверке") or (
        current == "На проверке" and target_status in ("Возвращена", "Требует ремонта")
    )

    if not allowed:
        messagebox.showwarning(
            "Недопустимый переход",
            f"Нельзя перевести из «{current}» в «{target_status}».\n"
            "Правило: Выдана → На проверке → Возвращена / Требует ремонта.",
        )
        return

    rec["status"] = target_status
    status_label.config(text=f"Запись №{rec['id']} — {rec['status']}")
    refresh_table()


def refresh_table():
    query = search_var.get().strip().lower()
    status_filter = filter_status_var.get()

    for item in tree.get_children():
        tree.delete(item)

    for rec in records:
        if status_filter != "Все" and rec["status"] != status_filter:
            continue
        if query and query not in rec["game"].lower() and query not in rec["guest"].lower():
            continue
        tree.insert(
            "",
            "end",
            values=(rec["id"], rec["game"], rec["table"], rec["guest"], rec["time"], rec["condition"], rec["status"]),
        )


def reset_filters():
    search_var.set("")
    filter_status_var.set("Все")
    refresh_table()

def delete_record():
    if selected_id is None:
        messagebox.showwarning("Запись не выбрана", "Выберите строку в таблице для удаления.")
        return

    rec = find_record(selected_id)
    if not rec:
        return

    confirm = messagebox.askyesno(
        "Подтверждение удаления",
        f"Удалить запись №{rec['id']} (игра «{rec['game']}», стол {rec['table']})?",
    )
    if not confirm:
        return

    records.remove(rec)
    refresh_table()
    clear_form()




def clear_form():
    global selected_id
    selected_id = None
    game_entry.delete(0, tk.END)
    table_entry.delete(0, tk.END)
    guest_entry.delete(0, tk.END)
    time_entry.delete(0, tk.END)
    condition_entry.delete(0, tk.END)
    condition_entry.insert(0, "Полный комплект")
    status_label.config(text="Новая запись (будет: Выдана)")
    for item in tree.selection():
        tree.selection_remove(item)


root = tk.Tk()
root.title("Учёт выдачи настольных игр «MyКубик»")
root.geometry("920x620")
root.minsize(840, 540)

form_frame = ttk.LabelFrame(root, text="Карточка выдачи игры", padding=10)
form_frame.pack(fill="x", padx=12, pady=(10, 6))

ttk.Label(form_frame, text="Название игры *:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
game_entry = ttk.Entry(form_frame, width=28)
game_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=4)

ttk.Label(form_frame, text="Номер стола *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
table_entry = ttk.Entry(form_frame, width=14)
table_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=4)

ttk.Label(form_frame, text="Имя гостя *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
guest_entry = ttk.Entry(form_frame, width=28)
guest_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

ttk.Label(form_frame, text="Время выдачи:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
time_entry = ttk.Entry(form_frame, width=14)
time_entry.grid(row=1, column=3, sticky="ew", padx=5, pady=4)

ttk.Label(form_frame, text="Состояние комплекта:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
condition_entry = ttk.Entry(form_frame, width=28)
condition_entry.insert(0, "Полный комплект")
condition_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=4)

ttk.Label(form_frame, text="Текущий статус:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
status_label = ttk.Label(form_frame, text="Новая запись (будет: Выдана)", font=("Segoe UI", 9, "bold"))
status_label.grid(row=2, column=3, sticky="w", padx=5, pady=4)

form_frame.columnconfigure(1, weight=1)
form_frame.columnconfigure(3, weight=1)

btn_frame = ttk.Frame(form_frame)
btn_frame.grid(row=3, column=0, columnspan=4, sticky="w", padx=5, pady=(8, 2))
ttk.Button(btn_frame, text="Добавить выдачу", command=add_record).pack(side="left", padx=(0, 6))
ttk.Button(btn_frame, text="Сохранить изменения", command=update_record).pack(side="left", padx=(0, 6))
ttk.Button(btn_frame, text="Удалить запись", command=delete_record).pack(side="left", padx=(0, 6))
ttk.Button(btn_frame, text="Очистить форму", command=clear_form).pack(side="left")


status_frame = ttk.LabelFrame(root, text="Управление статусом выбранной записи", padding=8)
status_frame.pack(fill="x", padx=12, pady=6)
ttk.Button(status_frame, text="Отправить на проверку", command=lambda: change_status("На проверке")).pack(side="left", padx=(0, 8))
ttk.Button(status_frame, text="Принять (Возвращена)", command=lambda: change_status("Возвращена")).pack(side="left", padx=(0, 8))
ttk.Button(status_frame, text="В ремонт (Требует ремонта)", command=lambda: change_status("Требует ремонта")).pack(side="left", padx=(0, 8))
ttk.Label(status_frame, text="Выдана → На проверке → Возвращена / Требует ремонта", foreground="gray").pack(side="right", padx=5)

filter_frame = ttk.LabelFrame(root, text="Поиск и фильтрация", padding=8)
filter_frame.pack(fill="x", padx=12, pady=6)
ttk.Label(filter_frame, text="Поиск (игра или гость):").pack(side="left", padx=(0, 6))
search_var = tk.StringVar()
search_var.trace_add("write", lambda *args: refresh_table())
ttk.Entry(filter_frame, textvariable=search_var, width=28).pack(side="left", padx=(0, 14))

ttk.Label(filter_frame, text="Статус:").pack(side="left", padx=(0, 6))
filter_status_var = tk.StringVar(value="Все")
filter_combo = ttk.Combobox(filter_frame, textvariable=filter_status_var, values=["Все"] + STATUSES, state="readonly", width=18)
filter_combo.pack(side="left", padx=(0, 10))
filter_combo.bind("<<ComboboxSelected>>", lambda e: refresh_table())
ttk.Button(filter_frame, text="Сбросить фильтры", command=reset_filters).pack(side="left")

list_frame = ttk.LabelFrame(root, text="Список выданных игр (нажмите на строку для выбора)", padding=10)
list_frame.pack(fill="both", expand=True, padx=12, pady=(6, 12))

columns = ("id", "game", "table", "guest", "time", "condition", "status")
tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
for col, title, width, anchor in [
    ("id", "№", 45, "center"),
    ("game", "Название игры", 185, "w"),
    ("table", "Стол", 70, "center"),
    ("guest", "Гость", 135, "w"),
    ("time", "Время", 80, "center"),
    ("condition", "Состояние", 185, "w"),
    ("status", "Статус", 135, "center"),
]:
    tree.heading(col, text=title)
    tree.column(col, width=width, anchor=anchor)

scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
tree.bind("<<TreeviewSelect>>", on_row_select)

root.mainloop()
  