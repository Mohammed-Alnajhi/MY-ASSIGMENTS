from fastapi import FastAPI
from db.database import SessionLocal
from models.product import Product

app = FastAPI()

@app.get("/products")
def get_products():
    db = SessionLocal()
    products = db.query(Product).all()

    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "price": p.price
        })

    db.close()
    return result
