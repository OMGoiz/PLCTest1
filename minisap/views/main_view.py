import tkinter as tk
from tkinter import ttk, messagebox


class MainView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("MiniSAP Cotizador Pro")
        self.geometry("1000x650")
        self._build_menu()
        self._build_body()

    def _build_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="New Quote", command=self.open_new_quote)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menu.add_cascade(label="File", menu=file_menu)

        catalogs = tk.Menu(menu, tearoff=0)
        catalogs.add_command(label="Clients", command=lambda: self.load_table("clients"))
        catalogs.add_command(label="Products", command=lambda: self.load_table("products"))
        menu.add_cascade(label="Catalogs", menu=catalogs)

        quotes_m = tk.Menu(menu, tearoff=0)
        quotes_m.add_command(label="New Quote", command=self.open_new_quote)
        quotes_m.add_command(label="View Quotes", command=lambda: self.load_table("quotes"))
        menu.add_cascade(label="Quotes", menu=quotes_m)

        tools = tk.Menu(menu, tearoff=0)
        tools.add_command(label="Reload CSV Data", command=self.reload_data)
        menu.add_cascade(label="Tools", menu=tools)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "MiniSAP Cotizador Pro"))
        menu.add_cascade(label="Help", menu=help_menu)

    def _build_body(self):
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)
        self.search_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.search_var).pack(fill="x")
        self.tree = ttk.Treeview(frm)
        self.tree.pack(fill="both", expand=True)
        self.load_table("quotes")

    def load_table(self, name):
        self.tree.delete(*self.tree.get_children())
        if name == "clients":
            rows = self.controller.clients.all()
        elif name == "products":
            rows = self.controller.products.all()
        else:
            rows = self.controller.quotes.all()
        if not rows:
            return
        cols = list(rows[0].keys())
        self.tree["columns"] = cols
        self.tree["show"] = "headings"
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="w")
        for r in rows:
            self.tree.insert("", "end", values=[r[c] for c in cols])

    def reload_data(self):
        self.controller.cfg.reload()
        self.controller._init_models()
        self.load_table("quotes")
        messagebox.showinfo("OK", "Datos recargados")

    def open_new_quote(self):
        QuoteEditor(self, self.controller)


class QuoteEditor(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Nueva Cotización")
        self.geometry("700x500")
        self.items = []
        self._build()

    def _build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Label(top, text="Client ID").grid(row=0, column=0)
        self.client = tk.StringVar()
        ttk.Entry(top, textvariable=self.client).grid(row=0, column=1, sticky="ew")

        ttk.Label(top, text="Product ID").grid(row=1, column=0)
        self.prod = tk.StringVar()
        ttk.Entry(top, textvariable=self.prod).grid(row=1, column=1)
        ttk.Label(top, text="Qty").grid(row=1, column=2)
        self.qty = tk.StringVar(value="1")
        ttk.Entry(top, textvariable=self.qty, width=8).grid(row=1, column=3)
        ttk.Button(top, text="Agregar", command=self.add_item).grid(row=1, column=4)

        self.tree = ttk.Treeview(self, columns=["product_id", "quantity", "unit_price", "total"], show="headings")
        for c in ["product_id", "quantity", "unit_price", "total"]:
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Button(self, text="Guardar Draft", command=self.save_quote).pack(pady=8)

    def add_item(self):
        pid = self.prod.get().strip()
        prod = next((p for p in self.controller.products.all() if p["id"] == pid), None)
        if not prod:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        qty = float(self.qty.get())
        unit = float(prod["price"])
        total = qty * unit
        row = {"product_id": pid, "quantity": qty, "unit_price": unit, "total": total}
        self.items.append(row)
        self.tree.insert("", "end", values=[pid, qty, unit, total])

    def save_quote(self):
        try:
            qid, calc = self.controller.create_quote(self.client.get(), self.items, "Draft")
            messagebox.showinfo("Guardado", f"{qid} total={calc['total']}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
