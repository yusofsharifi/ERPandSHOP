from sqlalchemy.orm import Session
from app.models.sales_orders import SalesOrder, SalesOrderLine
from app.models.inventory_item import InventoryItem
from app.models.ar_ap import Partner
from app.services.ar_ap_service import arap_service
from app.services.gl_service import gl_service
from app.models.gl_models import AuditLog
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4
import sqlalchemy as sa


class SalesOrderService:
    @staticmethod
    def _generate_order_no(db: Session, company_id) -> str:
        year = date.today().year
        # use gl_auto_number table similar to invoices
        row = db.execute("SELECT id, last_number FROM gl_auto_number WHERE company_id = :cid AND year = :yr FOR UPDATE", {'cid': str(company_id), 'yr': year}).fetchone()
        if row is None:
            new_id = str(uuid4())
            db.execute("INSERT INTO gl_auto_number (id, year, company_id, last_number) VALUES (:id, :yr, :cid, 1)", {'id': new_id, 'yr': year, 'cid': str(company_id)})
            last = 1
        else:
            last = int(row[1]) + 1
            db.execute("UPDATE gl_auto_number SET last_number = :ln WHERE company_id = :cid AND year = :yr", {'ln': last, 'cid': str(company_id), 'yr': year})
        seq = str(last).zfill(6)
        return f"SO{year}{seq}"

    @staticmethod
    def _compute_totals(lines: List[SalesOrderLine]) -> (Decimal, Decimal, Decimal, Decimal):
        total = Decimal('0')
        total_tax = Decimal('0')
        total_discount = Decimal('0')
        for l in lines:
            qty = Decimal(l.quantity or 0)
            unit = Decimal(l.unit_price or 0)
            discount = Decimal(l.discount or 0)
            tax_rate = Decimal(l.tax_rate or 0)
            base = qty * unit - discount
            tax = (base * tax_rate / Decimal('100'))
            line_total = (base + tax).quantize(Decimal('0.01'))
            total += line_total
            total_tax += tax
            total_discount += discount
        net = total
        return total, total_discount, total_tax, net

    @staticmethod
    def create_order(db: Session, payload, created_by=None):
        o = SalesOrder(
            company_id=payload.company_id,
            customer_id=payload.customer_id,
            date=payload.date or date.today(),
            expected_delivery_date=payload.expected_delivery_date,
            notes=payload.notes,
            status='draft',
        )
        db.add(o)
        db.flush()
        for l in payload.lines:
            ol = SalesOrderLine(order=o, product_id=l.product_id, description=l.description, quantity=l.quantity, unit_price=l.unit_price, discount=l.discount or 0, tax_rate=l.tax_rate or 0)
            db.add(ol)
        # compute totals
        db.commit()
        db.refresh(o)
        # compute and update totals
        total, total_discount, total_tax, net = SalesOrderService._compute_totals(o.lines)
        o.total_amount = total
        o.total_discount = total_discount
        o.total_tax = total_tax
        o.net_amount = net
        db.add(o)
        # audit
        al = AuditLog(entity_type='sales_order', entity_id=o.id, action='create', payload={'customer_id': str(o.customer_id)}, user_id=created_by)
        db.add(al)
        db.commit()
        db.refresh(o)
        return o

    @staticmethod
    def get_order(db: Session, order_id):
        return db.query(SalesOrder).filter(SalesOrder.id == order_id).first()

    @staticmethod
    def list_orders(db: Session, status: Optional[str]=None, customer_id: Optional[str]=None, date_from: Optional[date]=None, date_to: Optional[date]=None):
        q = db.query(SalesOrder)
        if status:
            q = q.filter(SalesOrder.status == status)
        if customer_id:
            q = q.filter(SalesOrder.customer_id == customer_id)
        if date_from:
            q = q.filter(SalesOrder.date >= date_from)
        if date_to:
            q = q.filter(SalesOrder.date <= date_to)
        return q.order_by(SalesOrder.date.desc()).all()

    @staticmethod
    def update_order(db: Session, order_id, payload, performed_by=None):
        o = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not o:
            raise KeyError('order_not_found')
        if o.status != 'draft':
            raise ValueError('cannot_update_non_draft')
        if payload.expected_delivery_date is not None:
            o.expected_delivery_date = payload.expected_delivery_date
        if payload.notes is not None:
            o.notes = payload.notes
        if payload.lines is not None:
            # remove existing lines
            db.query(SalesOrderLine).filter(SalesOrderLine.order_id == o.id).delete()
            for l in payload.lines:
                ol = SalesOrderLine(order=o, product_id=l.product_id, description=l.description, quantity=l.quantity, unit_price=l.unit_price, discount=l.discount or 0, tax_rate=l.tax_rate or 0)
                db.add(ol)
        db.add(o)
        # recompute totals
        db.commit()
        db.refresh(o)
        total, total_discount, total_tax, net = SalesOrderService._compute_totals(o.lines)
        o.total_amount = total
        o.total_discount = total_discount
        o.total_tax = total_tax
        o.net_amount = net
        db.add(o)
        al = AuditLog(entity_type='sales_order', entity_id=o.id, action='update', payload={}, user_id=performed_by)
        db.add(al)
        db.commit()
        db.refresh(o)
        return o

    @staticmethod
    def delete_order(db: Session, order_id, performed_by=None):
        o = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not o:
            raise KeyError('order_not_found')
        if o.status != 'draft':
            raise ValueError('cannot_delete_non_draft')
        db.delete(o)
        al = AuditLog(entity_type='sales_order', entity_id=o.id, action='delete', payload={}, user_id=performed_by)
        db.add(al)
        db.commit()
        return True

    @staticmethod
    def confirm_order(db: Session, order_id, performed_by=None):
        # reserve stock and mark confirmed
        o = db.query(SalesOrder).filter(SalesOrder.id == order_id).with_for_update().first()
        if not o:
            raise KeyError('order_not_found')
        if o.status != 'draft':
            raise ValueError('cannot_confirm_non_draft')
        # credit check
        partner = db.query(Partner).filter(Partner.id == o.customer_id).first()
        if partner and partner.credit_limit and partner.credit_limit > 0:
            # sum outstanding invoices
            from app.models.ar_ap import Invoice
            outstanding = db.query(sa.func.coalesce(sa.func.sum(Invoice.balance_amount),0)).filter(Invoice.partner_id == partner.id, Invoice.status.in_(['open','partial'])).scalar() or 0
            if Decimal(o.net_amount) + Decimal(outstanding) > Decimal(partner.credit_limit):
                raise ValueError('credit_limit_exceeded')
        # reserve stock: decrement inventory if available, otherwise raise
        for ln in o.lines:
            if ln.product_id:
                item = db.query(InventoryItem).filter(InventoryItem.id == ln.product_id).with_for_update().first()
                if not item:
                    raise ValueError('inventory_item_not_found')
                if item.quantity < ln.quantity:
                    raise ValueError('insufficient_stock')
                item.quantity = item.quantity - int(ln.quantity)
                db.add(item)
        o.status = 'confirmed'
        # generate order number
        try:
            o.order_no = SalesOrderService._generate_order_no(db, o.company_id)
        except Exception:
            o.order_no = None
        db.add(o)
        al = AuditLog(entity_type='sales_order', entity_id=o.id, action='confirm', payload={}, user_id=performed_by)
        db.add(al)
        db.commit()
        db.refresh(o)
        return o

    @staticmethod
    def invoice_order(db: Session, order_id, performed_by=None):
        # create invoice from order
        o = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not o:
            raise KeyError('order_not_found')
        if o.status not in ['confirmed','draft']:
            raise ValueError('cannot_invoice_order')
        # map lines to invoice lines
        invoice_lines = []
        from app.schemas.ar_ap import InvoiceLineIn, InvoiceCreate
        for ln in o.lines:
            invoice_lines.append(InvoiceLineIn(product_id=ln.product_id, description=ln.description, qty=ln.quantity, unit_price=ln.unit_price, tax_rate=ln.tax_rate))
        inv_payload = InvoiceCreate(partner_id=o.customer_id, invoice_type='sale', date=o.date, due_date=o.expected_delivery_date, currency='USD', lines=invoice_lines)
        inv = arap_service.create_invoice(db, inv_payload)
        o.status = 'invoiced'
        db.add(o)
        al = AuditLog(entity_type='sales_order', entity_id=o.id, action='invoice', payload={'invoice_id': str(inv.id)}, user_id=performed_by)
        db.add(al)
        db.commit()
        db.refresh(o)
        return {'order': o, 'invoice': inv}

    @staticmethod
    def ship_order(db: Session, order_id, carrier=None, tracking_code=None, performed_by=None):
        o = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not o:
            raise KeyError('order_not_found')
        if o.status not in ['invoiced','confirmed']:
            raise ValueError('cannot_ship_order')
        o.status = 'shipped'
        db.add(o)
        al = AuditLog(entity_type='sales_order', entity_id=o.id, action='ship', payload={'carrier': carrier, 'tracking_code': tracking_code}, user_id=performed_by)
        db.add(al)
        db.commit()
        db.refresh(o)
        return o


sales_order_service = SalesOrderService()
