from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from datetime import datetime
import os


def generate_report(
        crop,
        market,
        highest,
        lowest,
        average,
        volatility,
        recommendation
):

    os.makedirs("reports", exist_ok=True)

    filename = f"reports/{crop}_report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "<b>AgriPrice Insight Report</b>",
        styles["Title"]
    )

    elements.append(title)

    elements.append(Spacer(1, 20))

    subtitle = Paragraph(
        f"Generated on : {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        styles["Normal"]
    )

    elements.append(subtitle)

    elements.append(Spacer(1, 20))

    data = [

        ["Crop", crop],

        ["Market", market],

        ["Highest Price", f"₹ {highest:.2f}"],

        ["Lowest Price", f"₹ {lowest:.2f}"],

        ["Average Price", f"₹ {average:.2f}"],

        ["Volatility", f"{volatility:.2f}"],

        ["Recommendation", recommendation]

    ]

    table = Table(data)

    table.setStyle(

        TableStyle([

            ("BACKGROUND", (0,0), (-1,0), colors.green),

            ("TEXTCOLOR", (0,0), (-1,-1), colors.black),

            ("GRID", (0,0), (-1,-1), 1, colors.grey),

            ("BACKGROUND", (0,0), (0,-1), colors.lightgreen),

            ("BOTTOMPADDING", (0,0), (-1,-1), 10),

            ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold")

        ])

    )

    elements.append(table)

    elements.append(Spacer(1,25))

    footer = Paragraph(

        "AgriPrice Insight - Advanced Market Analytics Platform",

        styles["Heading2"]

    )

    elements.append(footer)

    doc.build(elements)

    return filename