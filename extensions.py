# -*- coding: utf-8 -*-
"""
Yalla Thailand Extensions - Extend existing models with custom fields.

1. AccountMove: Add package_type FK
2. SalesOrder: Add package_type FK
3. PurchaseOrder: Add package_type FK
"""
from modules.base.model_inheritance import ModelExtension
from modules.base.decorators import action, onchange
from django.db import models, transaction
from django.utils.translation import gettext as _
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class AccountMoveYallaExtension(ModelExtension):
    """
    Extend Account Move with package_type FK and client-paid-supplier action.
    """
    _inherit = 'account.move'
    _depends = ['account', 'tourism']

    package_type = models.ForeignKey(
        'tourism.PackageType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='account_moves',
        verbose_name=_("Package Type"),
        help_text=_("Tourism package type associated with this move")
    )

    related_bill = models.ForeignKey(
        'account.Move',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yalla_linked_invoices',
        verbose_name=_("Related Supplier Bill"),
        help_text=_("Vendor bill that the client paid directly to the supplier")
    )

    @action
    def action_client_paid_supplier(self):
        """
        Client paid the supplier directly. Create a bridging journal entry
        that closes both the customer invoice (receivable) and vendor bill (payable).
        """
        from modules.account.models import Move, MoveLine, AccountSettings
        from modules.account.services.reconciliation import ReconciliationService

        moves = self if hasattr(self, '__iter__') else [self]
        for invoice in moves:
            # --- Validations ---
            if invoice.state != 'posted':
                return {
                    'status': False, 'open_mode': 'message',
                    'message': _('Invoice must be posted first.'), 'data': {}
                }
            if not invoice.related_bill:
                return {
                    'status': False, 'open_mode': 'message',
                    'message': _('Please set a Related Supplier Bill first.'), 'data': {}
                }
            bill = invoice.related_bill
            if bill.state != 'posted':
                return {
                    'status': False, 'open_mode': 'message',
                    'message': _('The related supplier bill must be posted.'), 'data': {}
                }
            if invoice.payment_state == 'paid':
                return {
                    'status': False, 'open_mode': 'message',
                    'message': _('This invoice is already paid.'), 'data': {}
                }

            amount = invoice.amount_total

            # --- Get accounts ---
            try:
                settings = AccountSettings.objects.filter(
                    company=invoice.company
                ).first()
            except Exception:
                settings = None

            # Receivable account: from invoice's receivable line or default
            inv_receivable_line = invoice.line_ids.filter(
                account__account_type='asset_receivable'
            ).first()
            if inv_receivable_line:
                receivable_account = inv_receivable_line.account
            elif settings and settings.default_receivable_account:
                receivable_account = settings.default_receivable_account
            else:
                return {
                    'status': False, 'open_mode': 'message',
                    'message': _('No receivable account found.'), 'data': {}
                }

            # Payable account: from bill's payable line or default
            bill_payable_line = bill.line_ids.filter(
                account__account_type='liability_payable'
            ).first()
            if bill_payable_line:
                payable_account = bill_payable_line.account
            elif settings and settings.default_payable_account:
                payable_account = settings.default_payable_account
            else:
                return {
                    'status': False, 'open_mode': 'message',
                    'message': _('No payable account found.'), 'data': {}
                }

            # Misc journal
            misc_journal = None
            if settings and settings.default_misc_journal:
                misc_journal = settings.default_misc_journal
            if not misc_journal:
                from modules.account.models import Journal
                misc_journal = Journal.objects.filter(
                    type='general'
                ).first()
            if not misc_journal:
                return {
                    'status': False, 'open_mode': 'message',
                    'message': _('No miscellaneous journal configured.'), 'data': {}
                }

            # --- Create bridging journal entry ---
            with transaction.atomic():
                from modules.base.models import Branch
                branch = getattr(invoice, 'branch', None)
                if not branch:
                    branch = Branch.objects.first()

                from django.utils import timezone
                je = Move.objects.create(
                    name='',
                    date=timezone.now().date(),
                    journal=misc_journal,
                    move_type='entry',
                    currency=invoice.currency,
                    branch=branch,
                    ref=_('Client Paid Supplier: %(inv)s ↔ %(bill)s') % {
                        'inv': invoice.name, 'bill': bill.name
                    },
                )

                # DR Payable (partner = supplier from bill)
                je_debit_line = MoveLine.objects.create(
                    move=je,
                    name=_('Client paid supplier – %(bill)s') % {'bill': bill.name},
                    account=payable_account,
                    partner=bill.partner,
                    debit=amount,
                    credit=Decimal('0.00'),
                    date=je.date,
                    currency=invoice.currency,
                )

                # CR Receivable (partner = client from invoice)
                je_credit_line = MoveLine.objects.create(
                    move=je,
                    name=_('Client paid supplier – %(inv)s') % {'inv': invoice.name},
                    account=receivable_account,
                    partner=invoice.partner,
                    debit=Decimal('0.00'),
                    credit=amount,
                    date=je.date,
                    currency=invoice.currency,
                )

                # Post the JE
                if not je.name:
                    je.name = je._generate_name()
                je.state = 'posted'
                je.posted_before = True
                je.save()

                # --- Reconcile receivable: JE credit ↔ invoice's receivable debit ---
                if inv_receivable_line:
                    ReconciliationService.reconcile([inv_receivable_line, je_credit_line])

                # --- Reconcile payable: JE debit ↔ bill's payable credit ---
                if bill_payable_line:
                    ReconciliationService.reconcile([bill_payable_line, je_debit_line])

                # --- Update residual & payment_state on invoice ---
                inv_new_residual = max(invoice.amount_residual - amount, Decimal('0.00'))
                inv_ps = 'paid' if inv_new_residual <= 0 else 'partial'
                Move.objects.filter(pk=invoice.pk).update(
                    amount_residual=inv_new_residual,
                    payment_state=inv_ps,
                )

                # --- Update residual & payment_state on bill ---
                bill_new_residual = max(bill.amount_residual - amount, Decimal('0.00'))
                bill_ps = 'paid' if bill_new_residual <= 0 else 'partial'
                Move.objects.filter(pk=bill.pk).update(
                    amount_residual=bill_new_residual,
                    payment_state=bill_ps,
                )

            return {
                'status': True,
                'open_mode': 'message',
                'message': _(
                    'Done! Journal entry %(je)s created. '
                    'Invoice → %(inv_state)s, Bill → %(bill_state)s.'
                ) % {
                    'je': je.name,
                    'inv_state': inv_ps,
                    'bill_state': bill_ps,
                },
                'on_success': {'type': 'refresh'}

            }


class PartnerYallaExtension(ModelExtension):
    """
    Extend Partner with supplier settlement action.
    """
    _inherit = 'base.partner'
    _depends = ['base', 'account']

    @action
    def action_supplier_settlement(self):
        """
        Check unreconciled payable balance for this supplier
        and open a pre-filled payment form to settle the net difference.
        """
        from modules.account.models import MoveLine

        partners = self if hasattr(self, '__iter__') else [self]
        for partner in partners:
            # Query all unreconciled lines on payable accounts for this partner
            payable_lines = MoveLine.objects.filter(
                partner=partner,
                account__account_type='liability_payable',
                move__state='posted',
                reconciled=False,
            )

            total_debit = payable_lines.aggregate(
                total=models.Sum('debit')
            )['total'] or Decimal('0.00')
            total_credit = payable_lines.aggregate(
                total=models.Sum('credit')
            )['total'] or Decimal('0.00')

            net = total_debit - total_credit

            if abs(net) < Decimal('0.01'):
                return {
                    'status': True, 'open_mode': 'message',
                    'message': _('Account is already settled for %(name)s.') % {
                        'name': partner.name
                    },
                    'data': {}
                }

            if net > 0:
                # Supplier owes us → inbound payment
                payment_type = 'inbound'
                menu_key = 'account_customer_payments'
                abs_amount = float(net)
            else:
                # We owe supplier → outbound payment
                payment_type = 'outbound'
                menu_key = 'account_vendor_payments'
                abs_amount = float(abs(net))

            return {
                'status': True,
                'open_mode': 'slideover',
                'data': {
                    'menu_item_key': menu_key,
                    'view_type': 'form',
                    'context': {
                        'default_fields': {
                            'partner': partner,
                            'amount': abs_amount,
                            'payment_type': payment_type,
                        }
                    },
                    'type': 'action',
                    'title': _('Settle Account – %(name)s') % {'name': partner.name}
                }
            }


class SalesOrderYallaExtension(ModelExtension):
    """
    Extend Sales Order with package_type FK.
    """
    _inherit = 'sales.salesorder'
    _depends = ['sales', 'tourism']

    package_type = models.ForeignKey(
        'tourism.PackageType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_orders',
        verbose_name=_("Package Type"),
        help_text=_("Tourism package type associated with this sales order")
    )


class PurchaseOrderYallaExtension(ModelExtension):
    """
    Extend Purchase Order with package_type FK.
    """
    _inherit = 'purchase.order'
    _depends = ['purchase', 'tourism']

    package_type = models.ForeignKey(
        'tourism.PackageType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders_package_type',
        verbose_name=_("Package Type"),
        help_text=_("Tourism package type associated with this purchase order")
    )


class TourBookingYallaExtension(ModelExtension):
    """
    Extend TourBooking with available_trips M2M.
    Selecting trips auto-populates the Programs tab (one program per trip).
    """
    _inherit = 'tourism.tourbooking'
    _depends = ['tourism', 'yalla_thailand']

    available_trips = models.ManyToManyField(
        'yalla_thailand.AvailableTrip',
        blank=True,
        related_name='tour_bookings',
        verbose_name=_("Available Trips"),
        help_text=_("Select trips to auto-populate the programs tab")
    )

    @onchange('available_trips')
    def _onchange_available_trips(self):
        
        trips = self.available_trips.all() if self.pk else self.available_trips
        if not trips:
            return

        from datetime import datetime, timedelta
        from django.utils import timezone

        booking_start = self.start_date
        if booking_start:
            if isinstance(booking_start, str):
                booking_start = datetime.strptime(booking_start, '%Y-%m-%d').date()
        else:
            booking_start = timezone.now().date()

        if self.pk:
            from modules.tourism.models import TourProgram
            self.programs.all().delete()
            for i, trip in enumerate(trips):
                program_date = booking_start + timedelta(days=i)
                TourProgram.objects.create(
                    booking=self,
                    day_number=i + 1,
                    program_date=program_date,
                    title=trip.name,
                    description=trip.note or '',
                    breakfast=False, lunch=False, dinner=False,
                    price_per_person=trip.sell_prc_adult or 0,
                    cost_price=trip.net_prc_adult or 0,
                    notes='',
                    supplier=trip.supplier,
                )
            self.compute_totals_from_bookings()
        else:
            program_entries = []
            for i, trip in enumerate(trips):
                program_date = booking_start + timedelta(days=i)
                entry = {
                    'day_number': i + 1,
                    'program_date': program_date.isoformat(),
                    'title': trip.name,
                    'description': trip.note or '',
                    'breakfast': False, 'lunch': False, 'dinner': False,
                    'price_per_person': float(trip.sell_prc_adult or 0),
                    'cost_price': float(trip.net_prc_adult or 0),
                    'notes': '',
                }
                if trip.supplier:
                    entry['supplier'] = {'id': trip.supplier.id, 'name': trip.supplier.name}
                program_entries.append(entry)
            self.programs = program_entries


class ConversationTourismExtension(ModelExtension):
    """
    Add Yalla Thailand trip browsing capabilities to chat conversations.
    Enables staff to open the AvailableTrip kanban view directly from chat.
    """
    _inherit = 'chat.conversation'
    _depends = ['chat', 'yalla_thailand']

    @action
    def get_trips_list(self):
        """Open Yalla Thailand trips kanban from chat, passing conversation context."""
        for conversation in self:
            return {
                'status': True,
                'open_mode': 'slideover',
                'data': {
                    'menu_item_key': 'yalla_thailand_available_trips',
                    'view_type': 'kanban',
                    'context': {'conversation_id': str(conversation.id)},
                    'type': 'action',
                    'title': _('Available Trips'),
                },
            }

    def handle_adding_participant(self):
        """
        When a participant is added to a conversation, check if the social_partner
        has any leads in stage 1 and advance them to stage 2.
        """
        partner = getattr(self, 'social_partner', None)
        if not partner:
            return

        from modules.crm.models import Lead
        lead = Lead.objects.filter(partner=partner, stage_id=1).order_by('-created_at').first()
        if lead:
            lead.stage_id = 2
            lead.save(update_fields=['stage_id'])
            logger.info(
                "handle_adding_participant: moved lead %s for partner %s from stage 1 to stage 2",
                lead.id, partner.id
            )
