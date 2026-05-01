# 📦 Inventory Manager

A desktop-based Inventory Management System built with Python. Features a modern dark-themed GUI, real-time search and filtering, analytics with a bar chart, stock alerts, and CSV-based persistence — all without any database setup.

---

## 🖥️ Tech Stack

| Layer | Technology |
|-------|-----------|
| GUI | `tkinter` + `ttk` |
| Data Handling | `pandas` |
| Stats & Computation | `numpy` |
| Storage | CSV file (`inventory.csv`) |
| Language | Python 3 |

---

## ✨ Features

- **📋 Inventory Tab** — Sortable, searchable table with live search by name, ID, or supplier. Filter by category. Rows are color-coded for out-of-stock (red) and low stock (orange).
- **📊 Analytics Tab** — KPI cards for total SKUs, inventory value, average and highest unit price. Category breakdown table and a canvas-drawn bar chart for stock distribution.
- **⚠️ Alerts Tab** — Automatically flags items at or below 10 units as Low Stock or Out of Stock.
- **🗂️ Sidebar** — Add, Edit, Delete, Export CSV, and Refresh actions with live stat cards that update after every operation.
- **💾 Auto-seed** — Generates a sample inventory on first run so the app is usable immediately.

---

## 📁 Project Structure

```
inventory-manager/
│
├── ims.py   # Main application
├── inventory.csv          # Auto-generated on first run
├── setup.bat              # Dependency installer for Windows
├── setup.sh               # Dependency installer for Linux/macOS
└── README.md              # You are here
```

---

## ⚙️ Installing Dependencies

All required packages can be installed using the provided setup scripts. Choose the one for your operating system.

---

### 🪟 Windows — `setup.bat`

1. Make sure **Python 3** is installed from [python.org](https://www.python.org/downloads/)
2. During Python installation, **check the box that says "Add Python to PATH"** — this is important
3. Double-click `setup.bat`
4. A CMD window will open and install everything automatically
5. Once you see `Setup complete!`, you are ready to run the app

> If tkinter is missing, re-run the Python installer → choose **Modify** → make sure **tcl/tk and IDLE** is checked → finish installation → run `setup.bat` again.

---

### 🐧 Linux / macOS — `setup.sh`

The `.sh` file is a shell script and needs to be made executable before running. Follow these steps:

**Step 1 — Open a terminal** in the project folder.

**Step 2 — Give the script execute permission:**

```bash
chmod +x setup.sh
```

> `chmod +x` tells the system that this file is allowed to be executed as a program. You only need to do this once.

**Step 3 — Run the script:**

```bash
./setup.sh
```

The script will automatically detect your OS and package manager (`apt`, `dnf`, `pacman`, or `brew`) and install everything including `python3-tk`, `pandas`, and `numpy`.

**Step 4 — Once you see `Setup complete!`, run the app:**

```bash
python3 inventory_manager.py
```

> On some systems you may need `sudo` for the tkinter system package install. The script handles this automatically.

---

## ▶️ Running the App

**Windows:**
```
python inventory_manager.py
```

**Linux / macOS:**
```bash
python3 inventory_manager.py
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `tkinter` | GUI framework (bundled with Python) |
| `pandas` | DataFrame operations, CSV read/write |
| `numpy` | Stats computation (value, averages, stock counts) |

---

## 📋 CRUD Operations

| Operation | Details |
|-----------|---------|
| **Add** | Auto-generates sequential ID (`ITM001`, `ITM002`, …), validates all fields |
| **Edit** | Opens pre-filled dialog, updates only the selected record |
| **Delete** | Asks for confirmation before removing the item |
| **Export** | Saves current data to a user-chosen CSV with a timestamped filename |

---

## 🚨 Stock Alert Threshold

Items with quantity **≤ 10** are flagged automatically:

- 🟡 **Low Stock** — quantity between 1 and 10
- 🔴 **Out of Stock** — quantity is 0

This threshold is defined as `LOW_STOCK_THRESHOLD = 10` in `inventory_manager.py` and can be changed to any value you prefer.

---

## 📸 Color Reference

| Color | Meaning |
|-------|---------|
| 🔴 Dark Red row | Out of stock |
| 🟠 Dark Orange row | Low stock |
| 🟣 Indigo highlight | Selected row |
| ⚪ Alternating grey rows | Normal stock |

---

## 🛠️ Customization

- **Add categories** — Edit the `CATEGORIES` list in `inventory_manager.py`
- **Change stock threshold** — Update `LOW_STOCK_THRESHOLD`
- **Change data file path** — Update `DATA_FILE`
- **Reseed sample data** — Delete `inventory.csv` and restart the app

---

## 📄 License

This project is open for personal and educational use.
