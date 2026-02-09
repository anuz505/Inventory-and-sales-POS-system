import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from django.db.models import Sum
from .models import Sales


def generate_invoice_pdf(sale_id):
    """
    Generate a professional PDF invoice for a sale.
    Returns a BytesIO buffer containing the PDF.
    """
    try:
        # Fetch sale with related data
        sale = (
            Sales.objects.select_related("customer", "user")
            .prefetch_related("items__product")
            .get(id=sale_id)
        )
    except Sales.DoesNotExist:
        raise ValueError(f"Sale with ID {sale_id} not found")

    # Create buffer
    buffer = io.BytesIO()

    # Create PDF canvas
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # 612 x 792 points

    # ==================== HEADER SECTION ====================
    # Company Info (Top)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1 * inch, height - 1 * inch, "INVENTORY SYSTEM")

    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 1.3 * inch, "123 Business Street")
    c.drawString(1 * inch, height - 1.5 * inch, "City, State 12345")
    # c.drawString(1 * inch, height - 1.7 * inch, "Phone: (555) 123-4567")
    c.drawString(1 * inch, height - 1.9 * inch, "Email: info@inventory.com")

    # Invoice Title (Right side)
    c.setFont("Helvetica-Bold", 20)
    c.drawRightString(width - 1 * inch, height - 1 * inch, "INVOICE")

    # Invoice Details (Right side)
    c.setFont("Helvetica", 10)
    c.drawRightString(
        width - 1 * inch, height - 1.4 * inch, f"Invoice #: {sale.invoice_number}"
    )
    c.drawRightString(
        width - 1 * inch,
        height - 1.6 * inch,
        f"Date: {sale.created_at.strftime('%B %d, %Y')}",
    )
    c.drawRightString(
        width - 1 * inch, height - 1.8 * inch, f"Payment: {sale.payment_method}"
    )

    # Payment Status Badge
    status_color = (
        colors.green
        if sale.payment_status == "paid"
        else colors.orange if sale.payment_status == "pending" else colors.red
    )
    c.setFillColor(status_color)
    c.drawRightString(
        width - 1 * inch, height - 2.0 * inch, f"Status: {sale.payment_status.upper()}"
    )
    c.setFillColor(colors.black)

    # Horizontal line separator
    c.setStrokeColor(colors.grey)
    c.line(1 * inch, height - 2.3 * inch, width - 1 * inch, height - 2.3 * inch)

    # ==================== CUSTOMER SECTION ====================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 2.7 * inch, "BILL TO:")

    c.setFont("Helvetica", 10)
    y_position = height - 3.0 * inch
    c.drawString(1 * inch, y_position, sale.customer.name)

    if sale.customer.email:
        y_position -= 0.2 * inch
        c.drawString(1 * inch, y_position, f"Email: {sale.customer.email}")

    # if sale.customer.phone:
    #     y_position -= 0.2 * inch
    #     c.drawString(1 * inch, y_position, f"Phone: {sale.customer.phone}")

    if sale.customer.address:
        y_position -= 0.2 * inch
        c.drawString(1 * inch, y_position, f"Address: {sale.customer.address}")

    # Sales Person Info (Right side)
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 1 * inch, height - 2.7 * inch, "SALES PERSON:")

    c.setFont("Helvetica", 10)
    c.drawRightString(
        width - 1 * inch,
        height - 3.0 * inch,
        sale.user.username if sale.user else "N/A",
    )

    # ==================== LINE ITEMS TABLE ====================
    # Prepare table data
    table_data = [["Product", "Quantity", "Unit Price", "Discount", "Subtotal"]]

    for item in sale.items.all():
        table_data.append(
            [
                item.product.name[:30],  # Truncate long names
                str(item.quantity),
                f"${item.unit_price:.2f}",
                f"${item.discount_amount:.2f}",
                f"${item.subtotal:.2f}",
            ]
        )

    # Create table
    table = Table(
        table_data, colWidths=[3 * inch, 1 * inch, 1 * inch, 1 * inch, 1.5 * inch]
    )

    # Style the table
    table.setStyle(
        TableStyle(
            [
                # Header row styling
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                # Body rows styling
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),  # Align numbers center
                ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Align product names left
                ("TOPPADDING", (0, 1), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                # Alternating row colors
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.Color(0.95, 0.95, 0.95)],
                ),
            ]
        )
    )

    # Calculate table position (below customer info)
    table_y_position = y_position - 0.5 * inch

    # Draw table
    table.wrapOn(c, width, height)
    table.drawOn(c, 1 * inch, table_y_position - len(table_data) * 0.3 * inch)

    # ==================== TOTALS SECTION ====================
    totals_y_start = table_y_position - len(table_data) * 0.3 * inch - 0.5 * inch

    # Calculate totals
    items_subtotal = sum(item.subtotal for item in sale.items.all())
    total_discount = (
        sum(item.discount_amount for item in sale.items.all()) + sale.discount_amount
    )

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 2.5 * inch, totals_y_start, "Subtotal:")
    c.drawRightString(width - 1 * inch, totals_y_start, f"${items_subtotal:.2f}")

    totals_y_start -= 0.25 * inch
    c.drawRightString(width - 2.5 * inch, totals_y_start, "Discount:")
    c.drawRightString(width - 1 * inch, totals_y_start, f"-${total_discount:.2f}")

    # Draw line above total
    totals_y_start -= 0.1 * inch
    c.line(width - 4 * inch, totals_y_start, width - 1 * inch, totals_y_start)

    # Grand Total
    totals_y_start -= 0.25 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 2.5 * inch, totals_y_start, "TOTAL:")
    c.drawRightString(width - 1 * inch, totals_y_start, f"${sale.total_amount:.2f}")

    # ==================== NOTES SECTION ====================
    if sale.notes:
        notes_y_position = totals_y_start - 0.5 * inch
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1 * inch, notes_y_position, "Notes:")

        c.setFont("Helvetica", 9)
        notes_y_position -= 0.2 * inch

        # Wrap notes text if too long
        max_width = 70  # characters per line
        words = sale.notes.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        for line in lines[:5]:  # Limit to 5 lines
            c.drawString(1 * inch, notes_y_position, line)
            notes_y_position -= 0.15 * inch

    # ==================== FOOTER ====================
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 0.75 * inch, "Thank you for your business!")
    c.drawCentredString(
        width / 2,
        0.5 * inch,
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
    )

    # Save PDF
    c.showPage()
    c.save()

    # Reset buffer position to beginning
    buffer.seek(0)
    return buffer
