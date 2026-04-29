class PricingService:
    def __init__(self, tax_rate: float):
        self.tax_rate = tax_rate

    def calculate(self, items: list[dict], rules: list[dict]) -> dict:
        subtotal = sum(float(i["total"]) for i in items)
        discount = 0.0
        for r in rules:
            typ = r.get("type", "").strip().lower()
            val = float(r.get("value", 0) or 0)
            cond = r.get("condition", "").strip()
            if cond and not self._condition_ok(cond, items, subtotal):
                continue
            if typ == "percentage":
                discount += subtotal * (val / 100)
            elif typ == "fixed":
                discount += val
            elif typ == "conditional":
                discount += val
        discount = min(discount, subtotal)
        tax = (subtotal - discount) * self.tax_rate
        total = subtotal - discount + tax
        return {
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
        }

    def _condition_ok(self, expression: str, items: list[dict], subtotal: float) -> bool:
        total_qty = sum(float(i.get("quantity", 0)) for i in items)
        safe_locals = {"quantity": total_qty, "subtotal": subtotal}
        try:
            return bool(eval(expression, {"__builtins__": {}}, safe_locals))
        except Exception:
            return False
