"""
StockVision AI - Export Service

Generates CSV and PDF reports for stock data.
"""

import io
import csv
import logging
from typing import Optional



logger = logging.getLogger("stockvision.export_service")


class ExportService:
    """Generate exportable data files."""

    @staticmethod
    def generate_csv(data: list[dict], filename: str = "export") -> str:
        """Generate CSV string from a list of dicts."""
        if not data:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    @staticmethod
    def generate_pdf_report(
        ticker: str,
        info: dict,
        analytics: dict,
        forecast: Optional[dict] = None,
    ) -> bytes:
        """Generate a PDF report for a stock analysis."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            story.append(Paragraph(f"StockVision AI — {ticker} Report", styles["Title"]))
            story.append(Spacer(1, 20))

            # Stock Info
            story.append(Paragraph("Stock Information", styles["Heading2"]))
            info_data = [
                ["Ticker", ticker],
                ["Name", str(info.get("name", "—"))],
                ["Exchange", str(info.get("exchange", "—"))],
                ["Sector", str(info.get("sector", "—"))],
                ["Current Price", f"${info.get('current_price', 0):.2f}"],
            ]
            info_table = Table(info_data, colWidths=[150, 300])
            info_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))

            # Analytics
            if analytics:
                story.append(Paragraph("Financial Analytics", styles["Heading2"]))
                analytics_data = [
                    ["CAGR", f"{(analytics.get('cagr', 0) or 0) * 100:.2f}%"],
                    ["Volatility", f"{(analytics.get('volatility', 0) or 0) * 100:.2f}%"],
                    ["Sharpe Ratio", f"{analytics.get('sharpe_ratio', 0) or 0:.4f}"],
                    ["Sortino Ratio", f"{analytics.get('sortino_ratio', 0) or 0:.4f}"],
                    ["Max Drawdown", f"{(analytics.get('max_drawdown', 0) or 0) * 100:.2f}%"],
                    ["52W High", f"${analytics.get('fifty_two_week_high', 0) or 0:.2f}"],
                    ["52W Low", f"${analytics.get('fifty_two_week_low', 0) or 0:.2f}"],
                ]
                a_table = Table(analytics_data, colWidths=[150, 300])
                a_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1e293b")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
                ]))
                story.append(a_table)

            # Disclaimer
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                "Disclaimer: This report is for educational and informational purposes only. "
                "Not financial advice. Past performance does not guarantee future results.",
                styles["Normal"]
            ))

            doc.build(story)
            return buffer.getvalue()

        except ImportError:
            logger.warning("reportlab not installed — PDF export unavailable")
            return b""
