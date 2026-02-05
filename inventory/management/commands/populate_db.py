import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum
from inventory.models import Supplier, Category, Product


class Command(BaseCommand):
    help = "creates application data"

    def handle(self, *args, **options):
        self.stdout.write("Clearning existing data")
        Product.objects.all().delete()
        Category.objects.all().delete()
        Supplier.objects.all().delete()

        self.stdout.write("Creating Categories")
        categories = [
            Category.objects.create(
                name="Electronics", description="Electronic devices and accessories"
            ),
            Category.objects.create(
                name="Clothing", description="Apparel and fashion items"
            ),
            Category.objects.create(
                name="Food & Beverages", description="Food items and drinks"
            ),
            Category.objects.create(name="Books", description="Books and publications"),
            Category.objects.create(
                name="Furniture", description="Home and office furniture"
            ),
        ]
        self.stdout.write(self.style.SUCCESS(f"Created {len(categories)} categories"))
        # Create Suppliers
        self.stdout.write("Creating suppliers...")
        suppliers = [
            Supplier.objects.create(
                name="Tech Distributors Inc",
                email="contact@techdist.com",
                phone=1234567890,
                address="123 Tech Street, Silicon Valley, CA",
            ),
            Supplier.objects.create(
                name="Fashion Wholesale Ltd",
                email="info@fashionwholesale.com",
                phone=9876543210,
                address="456 Fashion Ave, New York, NY",
            ),
            Supplier.objects.create(
                name="Global Foods Supply",
                email="sales@globalfoods.com",
                phone=5551234567,
                address="789 Food Lane, Chicago, IL",
            ),
            Supplier.objects.create(
                name="Book Publishers Co",
                email="orders@bookpub.com",
                phone=5559876543,
                address="321 Library Rd, Boston, MA",
            ),
            Supplier.objects.create(
                name="Furniture Depot",
                email="support@furnituredepot.com",
                phone=5555555555,
                address="654 Furniture Blvd, Houston, TX",
            ),
        ]
        self.stdout.write(self.style.SUCCESS(f"Created {len(suppliers)} suppliers"))

        # Create Products
        self.stdout.write("Creating products...")
        products_data = [
            # Electronics
            ("Laptop", "Electronics", "Tech Distributors Inc", 800, 1200, 50),
            ("Smartphone", "Electronics", "Tech Distributors Inc", 500, 750, 100),
            ("Wireless Mouse", "Electronics", "Tech Distributors Inc", 15, 30, 200),
            ("USB Cable", "Electronics", "Tech Distributors Inc", 5, 12, 500),
            ("Headphones", "Electronics", "Tech Distributors Inc", 50, 100, 150),
            # Clothing
            ("T-Shirt", "Clothing", "Fashion Wholesale Ltd", 8, 20, 300),
            ("Jeans", "Clothing", "Fashion Wholesale Ltd", 25, 60, 150),
            ("Jacket", "Clothing", "Fashion Wholesale Ltd", 40, 100, 75),
            ("Sneakers", "Clothing", "Fashion Wholesale Ltd", 35, 80, 120),
            # Food & Beverages
            ("Coffee Beans", "Food & Beverages", "Global Foods Supply", 10, 18, 120),
            ("Organic Pasta", "Food & Beverages", "Global Foods Supply", 3, 8, 250),
            ("Energy Drink", "Food & Beverages", "Global Foods Supply", 1.5, 3.5, 400),
            ("Green Tea", "Food & Beverages", "Global Foods Supply", 5, 12, 180),
            # Books
            ("Python Programming", "Books", "Book Publishers Co", 20, 45, 80),
            ("Django Guide", "Books", "Book Publishers Co", 25, 55, 60),
            ("Web Development", "Books", "Book Publishers Co", 30, 65, 45),
            ("Data Science", "Books", "Book Publishers Co", 35, 70, 55),
            # Furniture
            ("Office Chair", "Furniture", "Furniture Depot", 100, 250, 40),
            ("Desk", "Furniture", "Furniture Depot", 200, 450, 25),
            ("Bookshelf", "Furniture", "Furniture Depot", 75, 180, 35),
            ("Standing Desk", "Furniture", "Furniture Depot", 300, 650, 15),
        ]
        for idx, (name, cat_name, sup_name, cost, price, stock) in enumerate(
            products_data, 1
        ):
            category = next(c for c in categories if c.name == cat_name)
            supplier = next(s for s in suppliers if s.name == sup_name)

            Product.objects.create(
                name=name,
                sku=f"SKU-{idx:05d}",
                description=f"High quality {name.lower()} from {supplier.name}",
                category=category,
                supplier=supplier,
                cost_price=Decimal(str(cost)),
                selling_price=Decimal(str(price)),
                stock_quantity=stock,
                low_stock_limit=random.randint(10, 30),
            )

        self.stdout.write(self.style.SUCCESS(f"Created {len(products_data)} products"))
        self.stdout.write(self.style.SUCCESS("\n Database populated successfully!"))
