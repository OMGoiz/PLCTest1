from pathlib import Path
from tkinter import messagebox

from models.catalog_models import ClientsModel, ProductsModel, PricingRulesModel, QuotesModel, QuoteItemsModel
from services.pricing_service import PricingService
from utils.validators import required, non_negative
from utils.helpers import today_iso


class AppController:
    def __init__(self, config_service, file_service, id_service, logger):
        self.cfg = config_service
        self.file_service = file_service
        self.id_service = id_service
        self.logger = logger
        self._init_models()

    def _init_models(self):
        paths = self.cfg.data["file_paths"]
        self.clients = ClientsModel(self.file_service, paths["clients"], ["id", "name", "rfc", "email", "phone"])
        self.products = ProductsModel(self.file_service, paths["products"], ["id", "name", "description", "price", "cost"])
        self.quotes = QuotesModel(self.file_service, paths["quotes"], ["id", "client_id", "date", "subtotal", "tax", "total", "status"])
        self.quote_items = QuoteItemsModel(self.file_service, paths["quote_items"], ["quote_id", "product_id", "quantity", "unit_price", "total"])
        self.rules = PricingRulesModel(self.file_service, paths["pricing_rules"], ["id", "type", "value", "condition"])

    def create_quote(self, client_id: str, item_rows: list[dict], status: str = "Draft"):
        required(client_id, "Cliente")
        if not item_rows:
            raise ValueError("Debe agregar al menos un producto")

        for item in item_rows:
            required(item.get("product_id"), "Producto")
            qty = non_negative(item.get("quantity"), "Cantidad")
            price = non_negative(item.get("unit_price"), "Precio unitario")
            item["quantity"] = qty
            item["unit_price"] = price
            item["total"] = round(qty * price, 2)

        pricing = PricingService(float(self.cfg.data.get("tax_rate", 0.16)))
        calc = pricing.calculate(item_rows, self.rules.all())

        quote_id = self.id_service.generate_quote_id()
        quotes = self.quotes.all()
        quotes.append({
            "id": quote_id,
            "client_id": client_id,
            "date": today_iso(),
            "subtotal": calc["subtotal"],
            "tax": calc["tax"],
            "total": calc["total"],
            "status": status,
        })
        self.quotes.save_all(quotes)

        items = self.quote_items.all()
        for i in item_rows:
            items.append({
                "quote_id": quote_id,
                "product_id": i["product_id"],
                "quantity": i["quantity"],
                "unit_price": i["unit_price"],
                "total": i["total"],
            })
        self.quote_items.save_all(items)
        self.logger.info("Quote created: %s", quote_id)
        return quote_id, calc

    def export_quote_txt(self, quote_id: str):
        out = Path("exports")
        out.mkdir(exist_ok=True)
        quote = next((q for q in self.quotes.all() if q["id"] == quote_id), None)
        if not quote:
            raise ValueError("Cotización no encontrada")
        items = [i for i in self.quote_items.all() if i["quote_id"] == quote_id]
        file_path = out / f"{quote_id}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{self.cfg.data['company_name']}\n")
            f.write(f"Cotización: {quote_id}\nFecha: {quote['date']}\n\n")
            f.write("Items:\n")
            for it in items:
                f.write(f"- {it['product_id']} | qty={it['quantity']} | unit={it['unit_price']} | total={it['total']}\n")
            f.write(f"\nSubtotal: {quote['subtotal']}\nTax: {quote['tax']}\nTotal: {quote['total']}\n")
        return file_path
