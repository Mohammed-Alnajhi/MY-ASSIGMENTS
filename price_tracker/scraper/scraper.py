import requests
from bs4 import BeautifulSoup
import re

from db.database import SessionLocal, engine
from models.product import Product, Base

Base.metadata.create_all(bind=engine)

db = SessionLocal()

url = "https://books.toscrape.com/"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

items = soup.select(".product_pod")

for item in items:
    name = item.h3.a["title"]
    
    price = item.select_one(".price_color").text
    
    price = re.findall(r"\d+\.\d+", price)[0]
    price = float(price)

    product = Product(name=name, price=price)
    db.add(product)

db.commit()
db.close()

print("Data Inserted Successfully")
