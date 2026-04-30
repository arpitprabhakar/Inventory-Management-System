import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import os
import csv
from datetime import datetime

DATA_FILE = "inventory.csv"
LOW_STOCK_THRESHOLD = 10

COLUMNS = ["ID", "Name", "Category", "Quantity", "Price (₹)", "Supplier", "Last Updated"]

CATEGORIES = [
    "Electronics", "Clothing", "Food & Beverage",
    "Furniture", "Stationery", "Tools", "Medicine", "Other"
]

BG          = "#0f172a"
SURFACE     = "#1e293b"
SURFACE2    = "#334155"
ACCENT      = "#6366f1"
ACCENT_DARK = "#4f46e5"
GREEN       = "#22c55e"
RED         = "#ef4444"
YELLOW      = "#f59e0b"
TEXT        = "#f8fafc"
TEXT_DIM    = "#94a3b8"
BORDER      = "#334155"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)


class InventoryData:
    def __init__(self):
        self.df = self._load()

    def _load(self) -> pd.DataFrame:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            for c in COLUMNS:
                if c not in df.columns:
                    df[c] = ""
            return df
        return self._seed()

    def _seed(self) -> pd.DataFrame:
        data = {
            "ID":           [f"ITM{str(i).zfill(3)}" for i in range(1, 11)],
            "Name":         ["Laptop", "T-Shirt", "Rice (5kg)", "Office Chair",
                             "Notebook", "Drill Machine", "Paracetamol",
                             "Headphones", "Jeans", "Pen Set"],
            "Category":     ["Electronics", "Clothing", "Food & Beverage",
                             "Furniture", "Stationery", "Tools", "Medicine",
                             "Electronics", "Clothing", "Stationery"],
            "Quantity":     [15, 50, 8, 3, 200, 12, 5, 30, 25, 100],
            "Price (₹)":    [65000, 499, 350, 8500, 120, 3200, 25, 2999, 1299, 150],
            "Supplier":     ["TechCorp", "FashionHub", "GrainMart", "FurniPlus",
                             "Stationery World", "ToolZone", "MediSupply",
                             "TechCorp", "FashionHub", "Stationery World"],
            "Last Updated": [datetime.now().strftime("%Y-%m-%d")] * 10,
        }
        df = pd.DataFrame(data)
        df.to_csv(DATA_FILE, index=False)
        return df

    def save(self):
        self.df.to_csv(DATA_FILE, index=False)

    def next_id(self) -> str:
        if self.df.empty:
            return "ITM001"
        nums = self.df["ID"].str.extract(r"(\d+)").astype(int).max().values
        return f"ITM{str(int(nums[0]) + 1).zfill(3)}"

    def stats(self) -> dict:
        if self.df.empty:
            return {"total_items": 0, "total_value": 0,
                    "low_stock": 0, "out_of_stock": 0,
                    "avg_price": 0, "max_price": 0}
        qty   = self.df["Quantity"].to_numpy(dtype=float)
        price = self.df["Price (₹)"].to_numpy(dtype=float)
        return {
            "total_items":   int(len(self.df)),
            "total_value":   float(np.sum(qty * price)),
            "low_stock":     int(np.sum((qty > 0) & (qty <= LOW_STOCK_THRESHOLD))),
            "out_of_stock":  int(np.sum(qty == 0)),
            "avg_price":     float(np.mean(price)),
            "max_price":     float(np.max(price)),
        }

    def category_summary(self) -> pd.DataFrame:
        if self.df.empty:
            return pd.DataFrame()
        return (
            self.df.groupby("Category")
            .agg(
                Items     = ("Name",       "count"),
                Total_Qty = ("Quantity",   "sum"),
                Avg_Price = ("Price (₹)",  "mean"),
            )
            .reset_index()
            .sort_values("Total_Qty", ascending=False)
        )

    def low_stock_items(self) -> pd.DataFrame:
        mask = (self.df["Quantity"].astype(float) <= LOW_STOCK_THRESHOLD) & \
               (self.df["Quantity"].astype(float) >= 0)
        return self.df[mask]

    def search(self, query: str, category: str) -> pd.DataFrame:
        df = self.df.copy()
        if query:
            q = query.lower()
            mask = (
                df["Name"].str.lower().str.contains(q, na=False) |
                df["ID"].str.lower().str.contains(q, na=False) |
                df["Supplier"].str.lower().str.contains(q, na=False)
            )
            df = df[mask]
        if category and category != "All":
            df = df[df["Category"] == category]
        return df


class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = InventoryData()
        self.title("📦  Inventory Manager")
        self.geometry("1280x760")
        self.minsize(1000, 640)
        self.configure(bg=BG)

        self._setup_styles()
        self._build_layout()
        self._refresh_all()

    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Inv.Treeview",
                     background=SURFACE, foreground=TEXT,
                     fieldbackground=SURFACE, rowheight=30,
                     font=FONT_BODY, borderwidth=0)
        s.configure("Inv.Treeview.Heading",
                     background=SURFACE2, foreground=TEXT,
                     font=FONT_HEAD, relief="flat")
        s.map("Inv.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", TEXT)])
        s.configure("Dark.Vertical.TScrollbar",
                     background=SURFACE2, troughcolor=SURFACE,
                     borderwidth=0, arrowcolor=TEXT_DIM)
        s.configure("TCombobox",
                     fieldbackground=SURFACE2, background=SURFACE2,
                     foreground=TEXT, selectbackground=ACCENT)
        s.map("TCombobox",
              fieldbackground=[("readonly", SURFACE2)],
              foreground=[("readonly", TEXT)])

    def _build_layout(self):
        self.sidebar = tk.Frame(self, bg=SURFACE, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        self.nb = ttk.Notebook(self.main)
        self.nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_inventory = tk.Frame(self.nb, bg=BG)
        self.tab_analytics  = tk.Frame(self.nb, bg=BG)
        self.tab_alerts     = tk.Frame(self.nb, bg=BG)

        self.nb.add(self.tab_inventory, text="  📋 Inventory  ")
        self.nb.add(self.tab_analytics,  text="  📊 Analytics   ")
        self.nb.add(self.tab_alerts,     text="  ⚠️  Alerts       ")

        self._build_inventory_tab()
        self._build_analytics_tab()
        self._build_alerts_tab()

    def _build_sidebar(self):
        tk.Label(self.sidebar, text="📦", font=("Segoe UI", 32),
                 bg=SURFACE, fg=ACCENT).pack(pady=(30, 4))
        tk.Label(self.sidebar, text="Inventory", font=("Segoe UI", 14, "bold"),
                 bg=SURFACE, fg=TEXT).pack()
        tk.Label(self.sidebar, text="Manager", font=("Segoe UI", 14, "bold"),
                 bg=SURFACE, fg=ACCENT).pack(pady=(0, 30))

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=16)

        actions = [
            ("➕  Add Item",    self._open_add_dialog),
            ("✏️   Edit Item",   self._open_edit_dialog),
            ("🗑️   Delete Item", self._delete_item),
            ("📤  Export CSV",  self._export_csv),
            ("🔄  Refresh",     self._refresh_all),
        ]
        for label, cmd in actions:
            self._sidebar_btn(label, cmd)

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=16, pady=10)

        self.stat_frame = tk.Frame(self.sidebar, bg=SURFACE)
        self.stat_frame.pack(fill="x", padx=10)

    def _sidebar_btn(self, text, cmd):
        btn = tk.Button(
            self.sidebar, text=text, command=cmd,
            bg=SURFACE, fg=TEXT, font=FONT_BODY,
            activebackground=SURFACE2, activeforeground=ACCENT,
            relief="flat", anchor="w", padx=18, pady=10,
            cursor="hand2", borderwidth=0
        )
        btn.pack(fill="x", pady=1)
        btn.bind("<Enter>", lambda e: btn.config(bg=SURFACE2, fg=ACCENT))
        btn.bind("<Leave>", lambda e: btn.config(bg=SURFACE, fg=TEXT))

    def _update_stat_cards(self):
        for w in self.stat_frame.winfo_children():
            w.destroy()
        s = self.data.stats()
        cards = [
            ("Total Items",    str(s["total_items"]),            TEXT),
            ("Total Value",    f"₹{s['total_value']:,.0f}",      GREEN),
            ("Low Stock",      str(s["low_stock"]),              YELLOW),
            ("Out of Stock",   str(s["out_of_stock"]),           RED),
        ]
        for label, value, color in cards:
            f = tk.Frame(self.stat_frame, bg=SURFACE2, pady=8)
            f.pack(fill="x", pady=3)
            tk.Label(f, text=value, font=("Segoe UI", 15, "bold"),
                     bg=SURFACE2, fg=color).pack()
            tk.Label(f, text=label, font=FONT_SMALL,
                     bg=SURFACE2, fg=TEXT_DIM).pack()

    def _build_inventory_tab(self):
        bar = tk.Frame(self.tab_inventory, bg=BG, pady=12)
        bar.pack(fill="x", padx=20)

        tk.Label(bar, text="🔍", bg=BG, fg=TEXT_DIM, font=("Segoe UI", 13)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        search_entry = tk.Entry(
            bar, textvariable=self.search_var,
            bg=SURFACE2, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=FONT_BODY, width=28
        )
        search_entry.pack(side="left", ipady=6, padx=(4, 16))

        tk.Label(bar, text="Category:", bg=BG, fg=TEXT_DIM,
                 font=FONT_BODY).pack(side="left")
        self.cat_filter = tk.StringVar(value="All")
        cat_cb = ttk.Combobox(
            bar, textvariable=self.cat_filter,
            values=["All"] + CATEGORIES, state="readonly", width=18,
            font=FONT_BODY
        )
        cat_cb.pack(side="left", padx=(6, 0), ipady=4)
        cat_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        self.row_count_var = tk.StringVar()
        tk.Label(bar, textvariable=self.row_count_var,
                 bg=BG, fg=TEXT_DIM, font=FONT_SMALL).pack(side="right")

        tree_frame = tk.Frame(self.tab_inventory, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.tree = ttk.Treeview(
            tree_frame, columns=COLUMNS, show="headings",
            style="Inv.Treeview", selectmode="browse"
        )
        col_widths = [70, 160, 120, 80, 100, 130, 110]
        for col, w in zip(COLUMNS, col_widths):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_tree(c))
            self.tree.column(col, width=w, anchor="center", minwidth=60)
        self.tree.column("Name", anchor="w")
        self.tree.column("Supplier", anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview,
                            style="Dark.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure("odd",  background=SURFACE)
        self.tree.tag_configure("even", background="#253047")
        self.tree.tag_configure("low",  background="#7c2d12")
        self.tree.tag_configure("out",  background="#450a0a")

        self.tree.bind("<Double-1>", lambda _: self._open_edit_dialog())
        self._sort_col = None
        self._sort_asc = True

    def _sort_tree(self, col):
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        numeric = col in ("Quantity", "Price (₹)")
        self.data.df = self.data.df.sort_values(
            col, ascending=self._sort_asc,
            key=(lambda x: pd.to_numeric(x, errors="coerce")) if numeric else None
        ).reset_index(drop=True)
        self._apply_filter()

    def _populate_tree(self, df: pd.DataFrame):
        self.tree.delete(*self.tree.get_children())
        for i, (_, row) in enumerate(df.iterrows()):
            qty = float(row["Quantity"])
            if qty == 0:
                tag = "out"
            elif qty <= LOW_STOCK_THRESHOLD:
                tag = "low"
            else:
                tag = "odd" if i % 2 == 0 else "even"
            self.tree.insert("", "end", values=list(row[COLUMNS]), tags=(tag,))
        self.row_count_var.set(f"{len(df)} item(s)")

    def _apply_filter(self):
        q   = self.search_var.get().strip()
        cat = self.cat_filter.get()
        df  = self.data.search(q, cat)
        self._populate_tree(df)

    def _build_analytics_tab(self):
        wrap = tk.Frame(self.tab_analytics, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(wrap, text="📊  Analytics Overview", font=FONT_TITLE,
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 16))

        self.analytics_cards_frame = tk.Frame(wrap, bg=BG)
        self.analytics_cards_frame.pack(fill="x", pady=(0, 20))

        tk.Label(wrap, text="Category Breakdown", font=FONT_HEAD,
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 6))

        cat_frame = tk.Frame(wrap, bg=SURFACE)
        cat_frame.pack(fill="x")

        self.cat_tree = ttk.Treeview(
            cat_frame,
            columns=["Category", "Items", "Total Qty", "Avg Price (₹)"],
            show="headings", style="Inv.Treeview", height=9
        )
        for col, w in zip(["Category", "Items", "Total Qty", "Avg Price (₹)"],
                           [180, 100, 120, 150]):
            self.cat_tree.heading(col, text=col)
            self.cat_tree.column(col, width=w, anchor="center")
        self.cat_tree.column("Category", anchor="w")
        self.cat_tree.pack(fill="x", padx=2, pady=2)
        self.cat_tree.tag_configure("row", background=SURFACE)
        self.cat_tree.tag_configure("alt", background=SURFACE2)

        tk.Label(wrap, text="Stock Distribution (canvas chart)", font=FONT_HEAD,
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(20, 6))
        self.chart_canvas = tk.Canvas(wrap, bg=SURFACE, height=160,
                                      highlightthickness=0)
        self.chart_canvas.pack(fill="x")

    def _update_analytics(self):
        for w in self.analytics_cards_frame.winfo_children():
            w.destroy()
        s = self.data.stats()
        cards = [
            ("🧮  Total SKUs",    str(s["total_items"]),           ACCENT),
            ("💰  Inventory Value", f"₹{s['total_value']:,.2f}",   GREEN),
            ("📉  Avg Unit Price", f"₹{s['avg_price']:,.2f}",      TEXT),
            ("🏆  Highest Price",  f"₹{s['max_price']:,.2f}",      YELLOW),
        ]
        for label, value, color in cards:
            card = tk.Frame(self.analytics_cards_frame, bg=SURFACE,
                            padx=20, pady=12)
            card.pack(side="left", padx=8, pady=4, fill="x", expand=True)
            tk.Label(card, text=value, font=("Segoe UI", 16, "bold"),
                     bg=SURFACE, fg=color).pack(anchor="w")
            tk.Label(card, text=label, font=FONT_SMALL,
                     bg=SURFACE, fg=TEXT_DIM).pack(anchor="w")

        self.cat_tree.delete(*self.cat_tree.get_children())
        summary = self.data.category_summary()
        if not summary.empty:
            for i, (_, row) in enumerate(summary.iterrows()):
                tag = "row" if i % 2 == 0 else "alt"
                self.cat_tree.insert("", "end",
                    values=[row["Category"], int(row["Items"]),
                            int(row["Total_Qty"]),
                            f"₹{row['Avg_Price']:,.2f}"], tags=(tag,))

        self._draw_bar_chart()

    def _draw_bar_chart(self):
        c = self.chart_canvas
        c.delete("all")
        c.update_idletasks()
        W = c.winfo_width() or 800
        H = 160

        summary = self.data.category_summary()
        if summary.empty:
            c.create_text(W//2, H//2, text="No data", fill=TEXT_DIM,
                          font=FONT_BODY)
            return

        n     = len(summary)
        pad   = 40
        bar_w = max(20, (W - pad * 2) // (n * 2))
        gap   = bar_w
        maxq  = max(summary["Total_Qty"].max(), 1)

        bar_colors = [ACCENT, GREEN, YELLOW, "#ec4899",
                      "#14b8a6", "#f97316", "#a855f7", "#ef4444"]

        for i, (_, row) in enumerate(summary.iterrows()):
            x0 = pad + i * (bar_w + gap)
            bh = int((row["Total_Qty"] / maxq) * (H - 50))
            y0 = H - 25 - bh
            col = bar_colors[i % len(bar_colors)]
            c.create_rectangle(x0, y0, x0 + bar_w, H - 25, fill=col,
                                outline="", width=0)
            c.create_text(x0 + bar_w // 2, y0 - 6,
                          text=str(int(row["Total_Qty"])),
                          fill=TEXT, font=FONT_SMALL, anchor="s")
            cat_label = row["Category"][:8]
            c.create_text(x0 + bar_w // 2, H - 12,
                          text=cat_label, fill=TEXT_DIM,
                          font=("Segoe UI", 7), anchor="center")

    def _build_alerts_tab(self):
        wrap = tk.Frame(self.tab_alerts, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(wrap, text="⚠️  Stock Alerts", font=FONT_TITLE,
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 6))
        tk.Label(wrap, text=f"Items at or below {LOW_STOCK_THRESHOLD} units are flagged.",
                 font=FONT_BODY, bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 16))

        self.alert_tree = ttk.Treeview(
            wrap,
            columns=["ID", "Name", "Category", "Quantity", "Status"],
            show="headings", style="Inv.Treeview"
        )
        for col, w in zip(["ID", "Name", "Category", "Quantity", "Status"],
                           [80, 180, 130, 100, 120]):
            self.alert_tree.heading(col, text=col)
            self.alert_tree.column(col, width=w, anchor="center")
        self.alert_tree.column("Name", anchor="w")
        self.alert_tree.pack(fill="both", expand=True)
        self.alert_tree.tag_configure("out",  background="#450a0a", foreground=RED)
        self.alert_tree.tag_configure("low",  background="#451a03", foreground=YELLOW)

    def _update_alerts(self):
        self.alert_tree.delete(*self.alert_tree.get_children())
        df = self.data.low_stock_items()
        if df.empty:
            return
        for _, row in df.iterrows():
            qty = float(row["Quantity"])
            status = "🔴 Out of Stock" if qty == 0 else "🟡 Low Stock"
            tag    = "out" if qty == 0 else "low"
            self.alert_tree.insert("", "end",
                values=[row["ID"], row["Name"], row["Category"],
                        int(qty), status], tags=(tag,))

    def _refresh_all(self):
        self.data = InventoryData()
        self._apply_filter()
        self._update_stat_cards()
        self._update_analytics()
        self._update_alerts()

    def _open_add_dialog(self):
        self._item_dialog(mode="add")

    def _open_edit_dialog(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Select Item",
                                   "Please select an item to edit.", parent=self)
            return
        values = self.tree.item(sel, "values")
        self._item_dialog(mode="edit", row_values=values)

    def _item_dialog(self, mode="add", row_values=None):
        dlg = tk.Toplevel(self)
        dlg.title("Add New Item" if mode == "add" else "Edit Item")
        dlg.configure(bg=BG)
        dlg.geometry("460x500")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.transient(self)

        tk.Label(dlg,
                 text="➕ Add Item" if mode == "add" else "✏️ Edit Item",
                 font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT
                 ).pack(pady=(20, 16))

        fields_frame = tk.Frame(dlg, bg=BG)
        fields_frame.pack(padx=30, fill="x")

        labels = ["Name", "Category", "Quantity", "Price (₹)", "Supplier"]
        entries = {}

        for i, lbl in enumerate(labels):
            row = tk.Frame(fields_frame, bg=BG)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=lbl, width=12, anchor="w",
                     bg=BG, fg=TEXT_DIM, font=FONT_BODY).pack(side="left")

            if lbl == "Category":
                var = tk.StringVar()
                widget = ttk.Combobox(row, textvariable=var, values=CATEGORIES,
                                      state="readonly", font=FONT_BODY, width=22)
                widget.pack(side="left", ipady=5)
                entries[lbl] = var
            else:
                var = tk.StringVar()
                widget = tk.Entry(row, textvariable=var, bg=SURFACE2, fg=TEXT,
                                  insertbackground=TEXT, relief="flat",
                                  font=FONT_BODY, width=24)
                widget.pack(side="left", ipady=6)
                entries[lbl] = var

        if mode == "edit" and row_values:
            entries["Name"].set(row_values[1])
            entries["Category"].set(row_values[2])
            entries["Quantity"].set(row_values[3])
            entries["Price (₹)"].set(row_values[4])
            entries["Supplier"].set(row_values[5])

        def _validate_and_save():
            name      = entries["Name"].get().strip()
            category  = entries["Category"].get().strip()
            qty_raw   = entries["Quantity"].get().strip()
            price_raw = entries["Price (₹)"].get().strip()
            supplier  = entries["Supplier"].get().strip()

            if not all([name, category, qty_raw, price_raw, supplier]):
                messagebox.showerror("Missing Fields",
                                     "All fields are required.", parent=dlg)
                return
            try:
                qty   = int(qty_raw)
                price = float(price_raw)
                if qty < 0 or price < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Input",
                                     "Quantity must be a non-negative integer\n"
                                     "Price must be a non-negative number.", parent=dlg)
                return

            today = datetime.now().strftime("%Y-%m-%d")
            if mode == "add":
                new_id = self.data.next_id()
                new_row = pd.DataFrame([{
                    "ID": new_id, "Name": name, "Category": category,
                    "Quantity": qty, "Price (₹)": price,
                    "Supplier": supplier, "Last Updated": today
                }])
                self.data.df = pd.concat([self.data.df, new_row],
                                         ignore_index=True)
            else:
                item_id = row_values[0]
                mask = self.data.df["ID"] == item_id
                self.data.df.loc[mask, "Name"]         = name
                self.data.df.loc[mask, "Category"]     = category
                self.data.df.loc[mask, "Quantity"]     = qty
                self.data.df.loc[mask, "Price (₹)"]    = price
                self.data.df.loc[mask, "Supplier"]     = supplier
                self.data.df.loc[mask, "Last Updated"] = today

            self.data.save()
            dlg.destroy()
            self._refresh_all()

        btn_row = tk.Frame(dlg, bg=BG)
        btn_row.pack(pady=24)

        tk.Button(btn_row, text="  Cancel  ", command=dlg.destroy,
                  bg=SURFACE2, fg=TEXT_DIM, relief="flat",
                  font=FONT_BODY, cursor="hand2", padx=10, pady=6
                  ).pack(side="left", padx=8)
        tk.Button(btn_row,
                  text="  Save Item  " if mode == "add" else "  Update  ",
                  command=_validate_and_save,
                  bg=ACCENT, fg=TEXT, relief="flat",
                  font=FONT_HEAD, cursor="hand2", padx=10, pady=6
                  ).pack(side="left", padx=8)

    def _delete_item(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Select Item",
                                   "Please select an item to delete.", parent=self)
            return
        values  = self.tree.item(sel, "values")
        item_id = values[0]
        name    = values[1]
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete '{name}' ({item_id})?", parent=self):
            return
        self.data.df = self.data.df[self.data.df["ID"] != item_id].reset_index(drop=True)
        self.data.save()
        self._refresh_all()

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Inventory as CSV",
            initialfile=f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )
        if not path:
            return
        self.data.df.to_csv(path, index=False)
        messagebox.showinfo("Exported",
                            f"Inventory exported successfully!\n{path}", parent=self)


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()