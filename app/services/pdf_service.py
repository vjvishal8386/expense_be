from io import BytesIO
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFService:
    """Service for generating PDF documents"""
    
    def __init__(self):
        self.page_size = A4
        self.margin = 0.75 * inch
        
    def generate_expense_report(
        self,
        expenses: List[dict],
        current_user_name: str,
        friend_name: str,
        balance: float,
        currency_symbol: str = "₹"
    ) -> BytesIO:
        """
        Generate a PDF report of expenses between two users
        
        Args:
            expenses: List of expense dictionaries with keys:
                - id, amount, description, date, paid_by_user_id, userAId, userBId
            current_user_name: Name of the current user
            friend_name: Name of the friend
            balance: Current balance (positive = friend owes, negative = user owes)
            currency_symbol: Currency symbol to use (default: ₹)
            
        Returns:
            BytesIO: PDF file as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Container for PDF elements
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4F46E5'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.textColor = colors.HexColor('#374151')
        
        # Title
        title = Paragraph("Expense Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Report Info
        report_date = datetime.now().strftime("%B %d, %Y")
        report_time = datetime.now().strftime("%I:%M %p")
        
        info_data = [
            ["Generated on:", f"{report_date} at {report_time}"],
            ["Between:", f"{current_user_name} and {friend_name}"],
        ]
        
        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Balance Summary
        balance_heading = Paragraph("Balance Summary", heading_style)
        elements.append(balance_heading)
        
        if balance > 0:
            balance_text = f"{friend_name} owes {current_user_name}: {currency_symbol}{abs(balance):.2f}"
            balance_color = colors.HexColor('#059669')  # Green
        elif balance < 0:
            balance_text = f"{current_user_name} owes {friend_name}: {currency_symbol}{abs(balance):.2f}"
            balance_color = colors.HexColor('#DC2626')  # Red
        else:
            balance_text = "All expenses are settled up!"
            balance_color = colors.HexColor('#4F46E5')  # Blue
        
        balance_para = Paragraph(
            balance_text,
            ParagraphStyle(
                'Balance',
                parent=normal_style,
                fontSize=14,
                textColor=balance_color,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER
            )
        )
        elements.append(balance_para)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Expenses Table
        if expenses:
            expenses_heading = Paragraph("Expense Details", heading_style)
            elements.append(expenses_heading)
            
            # Table headers
            table_data = [[
                "Date",
                "Description",
                "Amount",
                "Paid By"
            ]]
            
            # Add expense rows
            total_amount = Decimal(0)
            for expense in expenses:
                # Handle date formatting (could be date or datetime object)
                expense_date = expense['date']
                if isinstance(expense_date, (datetime, date)):
                    date_str = expense_date.strftime("%b %d, %Y")
                else:
                    # If it's a string, try to parse it
                    try:
                        if isinstance(expense_date, str):
                            parsed_date = datetime.strptime(expense_date, "%Y-%m-%d")
                            date_str = parsed_date.strftime("%b %d, %Y")
                        else:
                            date_str = str(expense_date)
                    except:
                        date_str = str(expense_date)
                
                description = expense['description']
                amount = float(expense['amount'])
                total_amount += Decimal(str(amount))
                
                # Determine who paid
                # In the expense structure, userAId is always current_user, userBId is always friend
                # So if paidByUserId == userAId, current user paid; if paidByUserId == userBId, friend paid
                if expense.get('paidByUserId') == expense.get('userAId'):
                    paid_by_name = current_user_name
                else:
                    paid_by_name = friend_name
                
                table_data.append([
                    date_str,
                    description,
                    f"{currency_symbol}{amount:.2f}",
                    paid_by_name
                ])
            
            # Add total row
            table_data.append([
                "",
                Paragraph("<b>Total</b>", normal_style),
                Paragraph(f"<b>{currency_symbol}{float(total_amount):.2f}</b>", normal_style),
                ""
            ])
            
            # Create table
            expenses_table = Table(
                table_data,
                colWidths=[1.2 * inch, 3.5 * inch, 1.2 * inch, 1.5 * inch]
            )
            
            expenses_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),  # Amount column right-aligned
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F9FAFB')]),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E5E7EB')),
                ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
                ('TOPPADDING', (0, 1), (-1, -2), 8),
                
                # Total row
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F3F4F6')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#4F46E5')),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
            ]))
            
            elements.append(expenses_table)
        else:
            no_expenses = Paragraph(
                "No expenses recorded yet.",
                ParagraphStyle(
                    'NoExpenses',
                    parent=normal_style,
                    fontSize=12,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#6B7280')
                )
            )
            elements.append(no_expenses)
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Footer
        footer_text = "Generated by Spend Book"
        footer = Paragraph(
            footer_text,
            ParagraphStyle(
                'Footer',
                parent=normal_style,
                fontSize=8,
                textColor=colors.HexColor('#9CA3AF'),
                alignment=TA_CENTER
            )
        )
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer


# Global instance
pdf_service = PDFService()

