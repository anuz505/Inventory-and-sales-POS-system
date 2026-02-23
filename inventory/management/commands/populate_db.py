import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import lorem_ipsum, timezone
from inventory.models import Supplier, Category, Product, StockMovement
from users.models import User
from sales.models import Sales, SalesItem, Customer


class Command(BaseCommand):
    help = "creates application data"

    def handle(self, *args, **options):
        self.stdout.write("Clearning existing data")
        SalesItem.objects.all().delete()
        Sales.objects.all().delete()
        Customer.objects.all().delete()
        StockMovement.objects.all().delete()
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

            product = Product.objects.create(
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

            # ── HISTORICAL TIMESTAMPS ────────────────────────────────────────
            # Backdate each product to a random point in the past year so that
            # time-series charts show a gradual inventory build-up rather than
            # everything appearing on the day the seeder was run.
            # .update() bypasses auto_now_add / auto_now restrictions entirely.
            # updated_at is set equal to created_at so it doesn't falsely
            # spike on today's date in "last updated" charts.
            product_created_at = timezone.now() - timedelta(
                days=random.randint(30, 365),
                hours=random.randint(8, 18),
                minutes=random.randint(0, 59),
            )
            Product.objects.filter(pk=product.pk).update(
                created_at=product_created_at,
                updated_at=product_created_at,
            )
            # ────────────────────────────────────────────────────────────────

        self.stdout.write(self.style.SUCCESS(f"Created {len(products_data)} products"))

        # Create multiple users for stock movements
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
        for user_data in users_data:
            password = user_data.pop("password")
            user, created = User.objects.get_or_create(
                username=user_data["username"], defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                users.append(user)
                self.stdout.write(
                    f"Created user: {user.username} ({user.get_role_display()})"
                )
            else:
                users.append(user)

        self.stdout.write(self.style.SUCCESS(f"Created/verified {len(users)} users"))

        # Create Stock Movements
        self.stdout.write("Creating stock movements...")
        all_products = list(Product.objects.all())
        stock_movements = []

        # Create initial stock-in movements (purchases)
        for product in all_products[:10]:
            StockMovement.objects.create(
                product=product,
                quantity=random.randint(20, 100),
                movement_type="IN",
                reason="PURCHASE",
                user=random.choice(users),
                notes=f"Initial stock purchase for {product.name}",
            )
            stock_movements.append("purchase")

        # Create some sales (stock-out)
        for product in random.sample(all_products, 8):
            StockMovement.objects.create(
                product=product,
                quantity=random.randint(5, 20),
                movement_type="OUT",
                reason="SALE",
                user=random.choice(users),
                notes=f"Customer purchase of {product.name}",
            )
            stock_movements.append("sale")

        # Create some returns (stock-in)
        for product in random.sample(all_products, 5):
            StockMovement.objects.create(
                product=product,
                quantity=random.randint(1, 5),
                movement_type="IN",
                reason="RETURN",
                user=random.choice(users),
                notes=f"Customer returned {product.name}",
            )
            stock_movements.append("return")

        # Create some damaged items (stock-out)
        for product in random.sample(all_products, 3):
            StockMovement.objects.create(
                product=product,
                quantity=random.randint(1, 3),
                movement_type="OUT",
                reason="DAMAGED",
                user=random.choice(users),
                notes=f"Damaged {product.name} removed from inventory",
            )
            stock_movements.append("damaged")

        # Create some manual adjustments
        for product in random.sample(all_products, 4):
            movement_type = random.choice(["IN", "OUT"])
            StockMovement.objects.create(
                product=product,
                quantity=random.randint(1, 10),
                movement_type=movement_type,
                reason="MANUAL",
                user=random.choice(users),
                notes=f"Manual inventory adjustment for {product.name}",
            )
            stock_movements.append("manual")

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(stock_movements)} stock movements")
        )

        # Create Customers
        self.stdout.write("Creating customers...")
        customers_data = [
            {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "phone_number": "5551234567",
                "address": "123 Main St, Springfield, IL",
            },
            {
                "name": "Emma Johnson",
                "email": "emma.j@example.com",
                "phone_number": "5552345678",
                "address": "456 Oak Ave, Portland, OR",
            },
            {
                "name": "Michael Brown",
                "email": "m.brown@example.com",
                "phone_number": "5553456789",
                "address": "789 Pine Rd, Austin, TX",
            },
            {
                "name": "Sarah Davis",
                "email": "sarah.davis@example.com",
                "phone_number": "5554567890",
                "address": "321 Elm St, Seattle, WA",
            },
            {
                "name": "David Wilson",
                "email": "d.wilson@example.com",
                "phone_number": "5555678901",
                "address": "654 Maple Dr, Denver, CO",
            },
            {
                "name": "Lisa Anderson",
                "email": "lisa.a@example.com",
                "phone_number": "5556789012",
                "address": "987 Cedar Ln, Miami, FL",
            },
            {
                "name": "James Taylor",
                "email": "james.t@example.com",
                "phone_number": "5557890123",
                "address": "147 Birch Blvd, Atlanta, GA",
            },
            {
                "name": "Jennifer Martinez",
                "email": "jen.martinez@example.com",
                "phone_number": "5558901234",
                "address": "258 Spruce St, Phoenix, AZ",
            },
        ]

        customers = []
        for customer_data in customers_data:
            customer = Customer.objects.create(**customer_data)
            customers.append(customer)

        self.stdout.write(self.style.SUCCESS(f"Created {len(customers)} customers"))

        # Create Sales
        self.stdout.write("Creating sales...")
        payment_methods = ["cash", "card", "upi", "net_banking", "wallet"]
        payment_statuses = ["completed", "pending", "refunded"]
        sales_records = []

        # Create 15 sales transactions
        for i in range(1, 16):
            customer = random.choice(customers)
            user = random.choice(users)
            payment_method = random.choice(payment_methods)
            payment_status = (
                random.choice(payment_statuses) if i % 7 == 0 else "completed"
            )

            # Create sale
            sale = Sales.objects.create(
                invoice_number=f"INV-{2026:04d}-{i:05d}",
                customer=customer,
                user=user,
                payment_method=payment_method,
                payment_status=payment_status,
                notes=f"Sale transaction {i}" if i % 3 == 0 else "",
            )

            # Add 1-5 random products to this sale
            num_items = random.randint(1, 5)
            selected_products = random.sample(all_products, num_items)

            sale_subtotal = Decimal("0")
            sale_discount = Decimal("0")

            for product in selected_products:
                quantity = random.randint(1, 5)
                unit_price = product.selling_price
                item_discount = Decimal(
                    str(random.choice([0, 0, 0, 5, 10, 15]))
                )  # Most items have no discount
                item_subtotal = (unit_price * quantity) - item_discount

                SalesItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount_amount=item_discount,
                    subtotal=item_subtotal,
                )

                sale_subtotal += unit_price * quantity
                sale_discount += item_discount

            # Update sale totals
            sale.subtotal = sale_subtotal
            sale.discount_amount = sale_discount
            sale.total_amount = sale_subtotal - sale_discount
            sale.save()

            sales_records.append(sale)

        self.stdout.write(self.style.SUCCESS(f"Created {len(sales_records)} sales"))

        # Count total sales items
        total_items = SalesItem.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Created {total_items} sales items"))

        self.stdout.write(self.style.SUCCESS("\n Database populated successfully!"))
