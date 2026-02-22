import random
from decimal import Decimal
from datetime import timedelta, datetime
import math
from django.utils import timezone
from django.core.management.base import BaseCommand
from inventory.models import Supplier, Category, Product, StockMovement
from users.models import User
from sales.models import Sales, SalesItem, Customer


class Command(BaseCommand):
    help = "Creates realistic application data with meaningful timestamps for visualization"

    # -------------------------------------------------------------------------
    # Date/time helpers
    # -------------------------------------------------------------------------

    def business_hour_datetime(self, base_date):
        """Return base_date with a realistic business-hour time attached."""
        hour = random.choices(
            range(8, 21),
            weights=[2, 5, 8, 10, 8, 12, 10, 8, 6, 5, 4, 3, 2],
            k=1,
        )[0]
        minute = random.randint(0, 59)
        return base_date.replace(
            hour=hour, minute=minute, second=random.randint(0, 59), microsecond=0
        )

    def date_range_dates(self, start_days_ago, end_days_ago=0, n=1):
        """Return n random dates between start_days_ago and end_days_ago."""
        results = []
        for _ in range(n):
            days = random.randint(end_days_ago, start_days_ago)
            dt = timezone.now() - timedelta(days=days)
            results.append(dt.replace(microsecond=0))
        return results if n > 1 else results[0]

    def trending_sale_date(self, index, total, max_days_ago=365):
        """
        Returns a date that biases more recent dates for higher-index sales,
        simulating business growth over time.
        """
        progress = index / total
        latest_possible = int((1 - progress) * max_days_ago)
        earliest_possible = max(latest_possible + 30, max_days_ago)
        days_ago = random.randint(latest_possible, earliest_possible)
        base = timezone.now() - timedelta(days=days_ago)
        return self.business_hour_datetime(base)

    def is_weekend(self, dt):
        return dt.weekday() >= 5

    def seasonal_multiplier(self, dt):
        """Higher sales around Nov–Dec (holiday) and Jun–Jul (summer)."""
        month = dt.month
        seasonal = {
            1: 0.7,
            2: 0.7,
            3: 0.8,
            4: 0.9,
            5: 1.0,
            6: 1.2,
            7: 1.3,
            8: 1.0,
            9: 0.9,
            10: 1.0,
            11: 1.4,
            12: 1.6,
        }
        return seasonal.get(month, 1.0)

    def pick_realistic_date(self, index, total, max_days_ago=365):
        """Combines growth trend + seasonality + weekday preference."""
        for _ in range(20):
            candidate = self.trending_sale_date(index, total, max_days_ago)
            weight = self.seasonal_multiplier(candidate)
            if self.is_weekend(candidate):
                weight *= 0.7
            if random.random() < weight / 1.6:
                return candidate
        return candidate  # fallback

    # -------------------------------------------------------------------------
    # Main handler
    # -------------------------------------------------------------------------

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        SalesItem.objects.all().delete()
        Sales.objects.all().delete()
        Customer.objects.all().delete()
        StockMovement.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Supplier.objects.all().delete()

        # --- Categories ---
        self.stdout.write("Creating categories...")
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
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(categories)} categories"))

        # --- Suppliers ---
        self.stdout.write("Creating suppliers...")
        suppliers_data = [
            (
                "Tech Distributors Inc",
                "contact@techdist.com",
                1234567890,
                "123 Tech Street, CA",
            ),
            (
                "Fashion Wholesale Ltd",
                "info@fashionwholesale.com",
                9876543210,
                "456 Fashion Ave, NY",
            ),
            (
                "Global Foods Supply",
                "sales@globalfoods.com",
                5551234567,
                "789 Food Lane, IL",
            ),
            (
                "Book Publishers Co",
                "orders@bookpub.com",
                5559876543,
                "321 Library Rd, MA",
            ),
            (
                "Furniture Depot",
                "support@furnituredepot.com",
                5555555555,
                "654 Furniture Blvd, TX",
            ),
        ]
        suppliers = []
        for name, email, phone, address in suppliers_data:
            suppliers.append(
                Supplier.objects.create(
                    name=name, email=email, phone=phone, address=address
                )
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(suppliers)} suppliers"))

        # --- Products ---
        # Products were "added to the system" staggered between 300–365 days ago.
        # We use .update() after creation to bypass auto_now_add on created_at,
        # and set updated_at equal to created_at so it doesn't show today's date.
        self.stdout.write("Creating products...")
        products_data = [
            ("Laptop", "Electronics", "Tech Distributors Inc", 800, 1200, 50),
            ("Smartphone", "Electronics", "Tech Distributors Inc", 500, 750, 100),
            ("Wireless Earbuds", "Electronics", "Tech Distributors Inc", 30, 80, 120),
            ("T-Shirt", "Clothing", "Fashion Wholesale Ltd", 8, 20, 300),
            ("Jeans", "Clothing", "Fashion Wholesale Ltd", 25, 60, 150),
            ("Winter Jacket", "Clothing", "Fashion Wholesale Ltd", 60, 150, 80),
            ("Coffee Beans", "Food & Beverages", "Global Foods Supply", 10, 18, 200),
            ("Organic Pasta", "Food & Beverages", "Global Foods Supply", 3, 8, 250),
            ("Green Tea", "Food & Beverages", "Global Foods Supply", 5, 12, 180),
            ("Python Programming", "Books", "Book Publishers Co", 20, 45, 80),
            ("Django Guide", "Books", "Book Publishers Co", 25, 55, 60),
            ("Data Science 101", "Books", "Book Publishers Co", 22, 48, 70),
            ("Office Chair", "Furniture", "Furniture Depot", 100, 250, 40),
            ("Standing Desk", "Furniture", "Furniture Depot", 200, 450, 25),
            ("Bookshelf", "Furniture", "Furniture Depot", 80, 180, 35),
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
            # Override auto_now_add — stagger product listing dates over the past year.
            # updated_at is set to the same value so it doesn't falsely show today.
            product_created_at = timezone.now() - timedelta(
                days=random.randint(300, 365),
                hours=random.randint(8, 18),
                minutes=random.randint(0, 59),
            )
            Product.objects.filter(pk=product.pk).update(
                created_at=product_created_at,
                updated_at=product_created_at,
            )

        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(products_data)} products"))

        # --- Users ---
        self.stdout.write("Creating users...")
        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "staff1",
                "email": "staff1@example.com",
                "password": "root",
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "username": "staff2",
                "email": "staff2@example.com",
                "password": "root",
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
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(users)} users"))

        all_products = list(Product.objects.all())

        # --- Stock Movements ---
        self.stdout.write("Creating stock movements...")
        sm_count = 0

        for product in all_products:
            # 1. Initial purchase (~340–365 days ago)
            days_ago = random.randint(340, 365)
            initial_dt = timezone.now() - timedelta(days=days_ago)
            mv = StockMovement.objects.create(
                product=product,
                quantity=random.randint(50, 150),
                movement_type="IN",
                reason="PURCHASE",
                user=users[0],
                notes=f"Initial stock purchase for {product.name}",
            )
            StockMovement.objects.filter(pk=mv.pk).update(created_at=initial_dt)
            sm_count += 1

            # 2. Periodic restocks — roughly every 6–8 weeks over the past year
            restock_intervals = sorted(
                random.sample(range(20, 330), k=random.randint(3, 6))
            )
            for days_ago in restock_intervals:
                dt = timezone.now() - timedelta(
                    days=days_ago, hours=random.randint(8, 17)
                )
                mv = StockMovement.objects.create(
                    product=product,
                    quantity=random.randint(20, 80),
                    movement_type="IN",
                    reason="PURCHASE",
                    user=random.choice(users),
                    notes=f"Restock order for {product.name}",
                )
                StockMovement.objects.filter(pk=mv.pk).update(created_at=dt)
                sm_count += 1

            # 3. Occasional adjustments / losses
            for _ in range(random.randint(1, 3)):
                days_ago = random.randint(1, 330)
                dt = timezone.now() - timedelta(
                    days=days_ago, hours=random.randint(9, 18)
                )
                movement_type = random.choice(["OUT", "OUT", "ADJUSTMENT"])
                reason = random.choice(["DAMAGE", "RETURN", "ADJUSTMENT"])
                mv = StockMovement.objects.create(
                    product=product,
                    quantity=random.randint(1, 10),
                    movement_type=movement_type,
                    reason=reason,
                    user=random.choice(users),
                    notes=f"{reason.capitalize()} adjustment for {product.name}",
                )
                StockMovement.objects.filter(pk=mv.pk).update(created_at=dt)
                sm_count += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ {sm_count} stock movements"))

        # --- Customers ---
        self.stdout.write("Creating customers...")
        customer_names = [
            ("Alice Johnson", "alice@example.com", "5550001001"),
            ("Bob Martinez", "bob@example.com", "5550001002"),
            ("Carol Lee", "carol@example.com", "5550001003"),
            ("David Kim", "david@example.com", "5550001004"),
            ("Emma Wilson", "emma@example.com", "5550001005"),
            ("Frank Davis", "frank@example.com", "5550001006"),
            ("Grace Park", "grace@example.com", "5550001007"),
            ("Henry Brown", "henry@example.com", "5550001008"),
            ("Isla Moore", "isla@example.com", "5550001009"),
            ("Jack Taylor", "jack@example.com", "5550001010"),
        ]
        customers = []
        for i, (name, email, phone) in enumerate(customer_names):
            customers.append(
                Customer.objects.create(
                    name=name,
                    email=email,
                    phone_number=phone,
                    address=f"{random.randint(1, 999)} Main St",
                )
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(customers)} customers"))

        # --- Sales ---
        self.stdout.write("Creating sales...")
        TOTAL_SALES = 120
        payment_methods = ["cash", "card", "card", "upi", "net_banking", "wallet"]
        payment_statuses = ["completed"] * 10 + ["pending"] * 2 + ["refunded"] * 1

        for i in range(1, TOTAL_SALES + 1):
            sale_date = self.pick_realistic_date(i, TOTAL_SALES, max_days_ago=365)
            customer = random.choice(customers)
            user = random.choice(users)
            pay_method = random.choice(payment_methods)
            pay_status = random.choice(payment_statuses)

            sale = Sales.objects.create(
                invoice_number=f"INV-{sale_date.year:04d}-{i:05d}",
                customer=customer,
                user=user,
                payment_method=pay_method,
                payment_status=pay_status,
                notes=f"Sale transaction {i}" if i % 4 == 0 else "",
            )
            Sales.objects.filter(pk=sale.pk).update(created_at=sale_date)

            num_items = random.randint(1, 4)
            selected_products = random.sample(all_products, num_items)
            sale_subtotal = Decimal("0")
            sale_discount = Decimal("0")

            for product in selected_products:
                if product.selling_price < 50:
                    quantity = random.randint(1, 8)
                elif product.selling_price < 200:
                    quantity = random.randint(1, 4)
                else:
                    quantity = random.randint(1, 2)

                unit_price = product.selling_price
                item_discount = Decimal(
                    str(random.choices([0, 5, 10, 15], weights=[60, 20, 15, 5])[0])
                )
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

            sale.subtotal = sale_subtotal
            sale.discount_amount = sale_discount
            sale.total_amount = sale_subtotal - sale_discount
            sale.save()

        self.stdout.write(self.style.SUCCESS(f"  ✓ {TOTAL_SALES} sales records"))
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ {SalesItem.objects.count()} sales items")
        )
        self.stdout.write(
            self.style.SUCCESS(
                "\n🎉 Database populated with realistic historical data!\n"
                "   Trends baked in:\n"
                "   • Products listed 300–365 days ago with staggered timestamps\n"
                "   • updated_at starts equal to created_at (not today)\n"
                "   • Sales volume grows over time (business growth curve)\n"
                "   • Nov–Dec and Jun–Jul seasonal spikes\n"
                "   • Weekdays busier than weekends\n"
                "   • Business-hours time distribution (peaks at 11 AM and 1 PM)\n"
                "   • Stock restocks every ~6–8 weeks per product\n"
                "   • Card payments dominant; cash/UPI/etc. as secondary\n"
                "   • Expensive items sold in lower quantities\n"
            )
        )
