import random
from decimal import Decimal
from datetime import date, datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from inventory.models import Category, Product, StockMovement, Supplier
from sales.models import Customer, Sales, SalesItem
from users.models import User


def random_dt(year, month, max_day=None):
    """Return a random timezone-aware datetime within the given year/month."""
    if month == 12:
        days_in_month = (date(year + 1, 1, 1) - date(year, 12, 1)).days
    else:
        days_in_month = (date(year, month + 1, 1) - date(year, month, 1)).days
    if max_day is not None:
        days_in_month = min(days_in_month, max_day)
    return make_aware(
        datetime(
            year,
            month,
            random.randint(1, days_in_month),
            random.randint(8, 20),
            random.randint(0, 59),
            random.randint(0, 59),
        )
    )


class Command(BaseCommand):
    help = "Populates the database with sample data for visualization (2026)"

    def handle(self, *args, **options):

        # ── CLEAR ────────────────────────────────────────────────────────────
        self.stdout.write("Clearing existing data...")
        SalesItem.objects.all().delete()
        Sales.objects.all().delete()
        Customer.objects.all().delete()
        StockMovement.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Supplier.objects.all().delete()

        # ── CATEGORIES ───────────────────────────────────────────────────────
        self.stdout.write("Creating categories...")
        categories = {
            c.name: c
            for c in [
                Category.objects.create(
                    name="Electronics", description="Electronic devices and accessories"
                ),
                Category.objects.create(
                    name="Clothing", description="Apparel and fashion items"
                ),
                Category.objects.create(
                    name="Food & Beverages", description="Food items and drinks"
                ),
                Category.objects.create(
                    name="Books", description="Books and publications"
                ),
                Category.objects.create(
                    name="Furniture", description="Home and office furniture"
                ),
            ]
        }
        self.stdout.write(self.style.SUCCESS(f"Created {len(categories)} categories"))

        # ── SUPPLIERS ────────────────────────────────────────────────────────
        self.stdout.write("Creating suppliers...")
        suppliers = {
            s.name: s
            for s in [
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
        }
        self.stdout.write(self.style.SUCCESS(f"Created {len(suppliers)} suppliers"))

        # ── PRODUCTS ─────────────────────────────────────────────────────────
        self.stdout.write("Creating products...")
        products_data = [
            # name, category, supplier, cost, price, stock
            ("Laptop", "Electronics", "Tech Distributors Inc", 800, 1200, 50),
            ("Smartphone", "Electronics", "Tech Distributors Inc", 500, 750, 100),
            ("Wireless Mouse", "Electronics", "Tech Distributors Inc", 15, 30, 200),
            ("USB Cable", "Electronics", "Tech Distributors Inc", 5, 12, 500),
            ("Headphones", "Electronics", "Tech Distributors Inc", 50, 100, 150),
            ("T-Shirt", "Clothing", "Fashion Wholesale Ltd", 8, 20, 300),
            ("Jeans", "Clothing", "Fashion Wholesale Ltd", 25, 60, 150),
            ("Jacket", "Clothing", "Fashion Wholesale Ltd", 40, 100, 75),
            ("Sneakers", "Clothing", "Fashion Wholesale Ltd", 35, 80, 120),
            ("Coffee Beans", "Food & Beverages", "Global Foods Supply", 10, 18, 120),
            ("Organic Pasta", "Food & Beverages", "Global Foods Supply", 3, 8, 250),
            ("Energy Drink", "Food & Beverages", "Global Foods Supply", 1.5, 3.5, 400),
            ("Green Tea", "Food & Beverages", "Global Foods Supply", 5, 12, 180),
            ("Python Programming", "Books", "Book Publishers Co", 20, 45, 80),
            ("Django Guide", "Books", "Book Publishers Co", 25, 55, 60),
            ("Web Development", "Books", "Book Publishers Co", 30, 65, 45),
            ("Data Science", "Books", "Book Publishers Co", 35, 70, 55),
            ("Office Chair", "Furniture", "Furniture Depot", 100, 250, 40),
            ("Desk", "Furniture", "Furniture Depot", 200, 450, 25),
            ("Bookshelf", "Furniture", "Furniture Depot", 75, 180, 35),
            ("Standing Desk", "Furniture", "Furniture Depot", 300, 650, 15),
        ]

        products = []
        for idx, (name, cat_name, sup_name, cost, price, stock) in enumerate(
            products_data, 1
        ):
            product = Product.objects.create(
                name=name,
                sku=f"SKU-{idx:05d}",
                description=(
                    f"High quality {name.lower()} from " f"{suppliers[sup_name].name}"
                ),
                category=categories[cat_name],
                supplier=suppliers[sup_name],
                cost_price=Decimal(str(cost)),
                selling_price=Decimal(str(price)),
                stock_quantity=stock,
                low_stock_limit=random.randint(10, 30),
            )
            created_at = random_dt(2025, random.randint(6, 12))
            Product.objects.filter(pk=product.pk).update(
                created_at=created_at, updated_at=created_at
            )
            products.append(product)

        self.stdout.write(self.style.SUCCESS(f"Created {len(products)} products"))

        # ── USERS ────────────────────────────────────────────────────────────
        self.stdout.write("Creating users...")
        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "role": "admin",
                "phone_number": "1234567890",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "staff1",
                "email": "staff1@example.com",
                "password": "root",
                "role": "staff",
                "phone_number": "2345678901",
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "username": "staff2",
                "email": "staff2@example.com",
                "password": "root",
                "role": "staff",
                "phone_number": "3456789012",
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "username": "manager1",
                "email": "manager1@example.com",
                "password": "root",
                "role": "manager",
                "phone_number": "4567890123",
                "is_staff": True,
                "is_superuser": False,
            },
        ]
        users = []
        for data in users_data:
            password = data.pop("password")
            user, created = User.objects.get_or_create(
                username=data["username"], defaults=data
            )
            if created:
                user.set_password(password)
                user.save()
            users.append(user)
            self.stdout.write(f"  {'Created' if created else 'Found'}: {user.username}")
        self.stdout.write(self.style.SUCCESS(f"Created/verified {len(users)} users"))

        # ── STOCK MOVEMENTS ──────────────────────────────────────────────────
        self.stdout.write("Creating stock movements...")

        def make_movement(product, qty, m_type, reason, note):
            sm = StockMovement.objects.create(
                product=product,
                quantity=qty,
                movement_type=m_type,
                reason=reason,
                user=random.choice(users),
                notes=note,
            )
            StockMovement.objects.filter(pk=sm.pk).update(
                created_at=random_dt(2025, random.randint(6, 12))
            )

        for product in products[:10]:
            make_movement(
                product,
                random.randint(20, 100),
                "IN",
                "PURCHASE",
                f"Initial stock purchase for {product.name}",
            )
        for product in random.sample(products, 8):
            make_movement(
                product,
                random.randint(5, 20),
                "OUT",
                "SALE",
                f"Customer purchase of {product.name}",
            )
        for product in random.sample(products, 5):
            make_movement(
                product,
                random.randint(1, 5),
                "IN",
                "RETURN",
                f"Customer returned {product.name}",
            )
        for product in random.sample(products, 3):
            make_movement(
                product,
                random.randint(1, 3),
                "OUT",
                "DAMAGED",
                f"Damaged {product.name} removed from inventory",
            )
        for product in random.sample(products, 4):
            make_movement(
                product,
                random.randint(1, 10),
                random.choice(["IN", "OUT"]),
                "MANUAL",
                f"Manual adjustment for {product.name}",
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {StockMovement.objects.count()} stock movements"
            )
        )

        # ── CUSTOMERS ────────────────────────────────────────────────────────
        self.stdout.write("Creating customers...")
        customers = [
            Customer.objects.create(
                name="John Smith",
                email="john.smith@example.com",
                phone_number="5551234567",
                address="123 Main St, Springfield, IL",
            ),
            Customer.objects.create(
                name="Emma Johnson",
                email="emma.j@example.com",
                phone_number="5552345678",
                address="456 Oak Ave, Portland, OR",
            ),
            Customer.objects.create(
                name="Michael Brown",
                email="m.brown@example.com",
                phone_number="5553456789",
                address="789 Pine Rd, Austin, TX",
            ),
            Customer.objects.create(
                name="Sarah Davis",
                email="sarah.davis@example.com",
                phone_number="5554567890",
                address="321 Elm St, Seattle, WA",
            ),
            Customer.objects.create(
                name="David Wilson",
                email="d.wilson@example.com",
                phone_number="5555678901",
                address="654 Maple Dr, Denver, CO",
            ),
            Customer.objects.create(
                name="Lisa Anderson",
                email="lisa.a@example.com",
                phone_number="5556789012",
                address="987 Cedar Ln, Miami, FL",
            ),
            Customer.objects.create(
                name="James Taylor",
                email="james.t@example.com",
                phone_number="5557890123",
                address="147 Birch Blvd, Atlanta, GA",
            ),
            Customer.objects.create(
                name="Jennifer Martinez",
                email="jen.martinez@example.com",
                phone_number="5558901234",
                address="258 Spruce St, Phoenix, AZ",
            ),
            Customer.objects.create(
                name="Robert Lee",
                email="robert.lee@example.com",
                phone_number="5559012345",
                address="369 Walnut Way, Nashville, TN",
            ),
            Customer.objects.create(
                name="Amanda Clark",
                email="amanda.c@example.com",
                phone_number="5550123456",
                address="741 Willow Ct, Minneapolis, MN",
            ),
        ]
        self.stdout.write(self.style.SUCCESS(f"Created {len(customers)} customers"))

        # ── SALES — ALL MONTHS OF 2026 UP TO TODAY ──────────────────────────
        self.stdout.write("Creating 2026 sales...")

        payment_methods = ["cash", "card", "upi", "net_banking", "wallet"]
        payment_statuses = [
            "completed",
            "completed",
            "completed",
            "pending",
            "refunded",
        ]

        # Vary volume per month — seasonal ramp-up toward Q4
        sales_per_month = {
            1: 12,
            2: 10,
            3: 14,
            4: 11,
            5: 13,
            6: 15,
            7: 12,
            8: 16,
            9: 14,
            10: 18,
            11: 22,
            12: 25,
        }

        invoice_counter = 1
        today = date.today()

        for month in range(1, today.month + 1):
            max_day = today.day if month == today.month else None
            for _ in range(sales_per_month[month]):
                sale_dt = random_dt(2026, month, max_day=max_day)

                # Step 1: create the sale row (created_at=None at this point)
                sale = Sales.objects.create(
                    invoice_number=f"INV-2026-{invoice_counter:05d}",
                    customer=random.choice(customers),
                    user=random.choice(users),
                    payment_method=random.choice(payment_methods),
                    payment_status=random.choice(payment_statuses),
                    notes=(
                        f"Sale {invoice_counter}" if invoice_counter % 5 == 0 else ""
                    ),
                )

                # Step 2: stamp the timestamp — before any further .save()
                Sales.objects.filter(pk=sale.pk).update(
                    created_at=sale_dt, updated_at=sale_dt
                )

                # Step 3: create sale items
                subtotal = Decimal("0")
                discount = Decimal("0")

                for product in random.sample(products, random.randint(1, 5)):
                    quantity = random.randint(1, 5)
                    unit_price = product.selling_price
                    item_discount = Decimal(
                        str(random.choice([0, 0, 0, 5, 10, 15, 20]))
                    )
                    item_subtotal = (unit_price * quantity) - item_discount

                    SalesItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        discount_amount=item_discount,
                        subtotal=item_subtotal,
                        created_at=sale_dt,
                    )

                    subtotal += unit_price * quantity
                    discount += item_discount

                # Step 4: update totals via .filter().update() — never .save()
                # Using .save() here would flush the stale in-memory object and
                # overwrite created_at back to None in the database.
                Sales.objects.filter(pk=sale.pk).update(
                    subtotal=subtotal,
                    discount_amount=discount,
                    total_amount=subtotal - discount,
                )

                invoice_counter += 1

            self.stdout.write(f"  Month {month:02d}: {sales_per_month[month]} sales")

        self.stdout.write(
            self.style.SUCCESS(f"\nCreated {Sales.objects.count()} sales")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created {SalesItem.objects.count()} sales items")
        )
        self.stdout.write(self.style.SUCCESS("✅ Database populated successfully!"))
