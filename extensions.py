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
        Check outstanding payable balance for this supplier
        and open a pre-filled payment form to settle the net difference.
        Uses Move.amount_residual to correctly handle partially-paid bills.
        """
        from modules.account.models import Move

        partners = self if hasattr(self, '__iter__') else [self]
        for partner in partners:
            # Sum outstanding amounts on vendor bills (what we owe supplier)
            vendor_bills = Move.objects.filter(
                partner=partner,
                move_type='in_invoice',
                state='posted',
            ).exclude(payment_state='paid')
            total_bills = sum(
                m.amount_residual for m in vendor_bills
            ) or Decimal('0.00')

            # Sum outstanding amounts on vendor credit notes (supplier owes us)
            vendor_credits = Move.objects.filter(
                partner=partner,
                move_type='in_refund',
                state='posted',
            ).exclude(payment_state='paid')
            total_credits = sum(
                m.amount_residual for m in vendor_credits
            ) or Decimal('0.00')

            # positive = we owe supplier, negative = supplier owes us
            net = total_bills - total_credits

            if abs(net) < Decimal('0.01'):
                return {
                    'status': True, 'open_mode': 'message',
                    'message': _('Account is already settled for %(name)s.') % {
                        'name': partner.name
                    },
                    'data': {}
                }

            if net > 0:
                # We owe supplier → outbound payment
                payment_type = 'outbound'
                menu_key = 'account_vendor_payments'
                abs_amount = float(net)
            else:
                # Supplier owes us → inbound payment
                payment_type = 'inbound'
                menu_key = 'account_customer_payments'
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
    _depends = ['tourism', 'yalla_thailand', 'payment_omise']

    available_trips = models.ManyToManyField(
        'yalla_thailand.AvailableTrip',
        blank=True,
        related_name='tour_bookings',
        verbose_name=_("Available Trips"),
        help_text=_("Select trips to auto-populate the programs tab")
    )

    @onchange('available_trips')
    def _onchange_available_trips(self):
        raw_trips = self.available_trips
        trips = raw_trips.all() if hasattr(raw_trips, 'all') else raw_trips
        if not trips:
            self.programs = []
            return

        from datetime import datetime, timedelta
        from django.utils import timezone

        booking_start = self.start_date
        if booking_start:
            if isinstance(booking_start, str):
                booking_start = datetime.strptime(booking_start, '%Y-%m-%d').date()
        else:
            booking_start = timezone.now().date()

        program_entries = []
        for i, trip in enumerate(trips):
            program_date = booking_start + timedelta(days=i)
            entry = {
                'day_number': i + 1,
                'program_date': program_date.isoformat(),
                'title': trip.name,
                'description': trip.description or '',
                'lunch_option': trip.lunch or '',
                'price_per_person': float(trip.sell_prc_adult or 0),
                'cost_price': float(trip.net_prc_adult or 0),
                'child_price': float(trip.sell_prc_child or 0),
                'child_cost': float(trip.net_prc_child or 0),
                'markup': float(trip.min_markup or 0),
                'actual_adult_price': float(trip.sell_prc_adult or 0),
                'actual_child_price': float(trip.sell_prc_child or 0),
                'notes': trip.note or '',
            }
            if trip.supplier:
                entry['supplier'] = {'id': trip.supplier.id, 'name': trip.supplier.name}
            program_entries.append(entry)
        self.programs = program_entries

    @action
    def send_omise_payment_link(self):
        """Queue Omise payment link sends for each booking's sale order
        via WhatsApp / Messenger / Instagram."""
        from modules.payment_omise.tasks import send_omise_payment_link_task

        bookings = self if hasattr(self, '__iter__') else [self]
        queued = 0
        errors = []
        user_id = None

        first = next(iter(bookings), None)
        if first and hasattr(first, 'env') and first.env.user:
            user_id = first.env.user.id

        for booking in bookings:
            order = getattr(booking, 'sale_order', None)
            if not order:
                errors.append(
                    _("Booking %(name)s: no sale order linked") % {'name': booking.name}
                )
                continue
            partner = order.partner or getattr(booking, 'partner', None)
            if not partner:
                errors.append(
                    _("Booking %(name)s: no partner") % {'name': booking.name}
                )
                continue
            if not (
                getattr(partner, 'whatsapp_account', None)
                or getattr(partner, 'facebook_page', None)
                or getattr(partner, 'instagram_account', None)
            ):
                errors.append(
                    _("Booking %(name)s: %(partner)s has no WhatsApp / Messenger / Instagram") % {
                        'name': booking.name, 'partner': partner.name
                    }
                )
                continue

            send_omise_payment_link_task.delay(order.id, user_id)
            queued += 1

        if errors:
            message = _("Queued %(n)s payment link(s). Errors: %(e)s") % {
                'n': queued, 'e': '; '.join(errors)
            }
            stat = queued > 0
        else:
            message = _("Queued %(n)s payment link(s) for sending") % {'n': queued}
            stat = True

        return {
            'status': stat,
            'open_mode': 'message',
            'message': message,
            'data': {'queued': queued, 'errors': errors},
        }

    @action
    def action_create_so_and_pos(self):
        """Combined: create sales quotation and supplier POs in one click.

        Reuses tourism.tourbooking.action_create_quotation and
        action_create_purchase_order. Safe to re-run: existing SO is
        reused, existing (booking, supplier) POs are skipped.
        """
        from modules.purchase.models import Order as PurchaseOrder

        bookings = self if hasattr(self, '__iter__') else [self]
        summaries = []
        errors = []

        for booking in bookings:
            had_so = bool(booking.sale_order)
            po_count_before = PurchaseOrder.objects.filter(tour_booking=booking).count()

            try:
                q_resp = booking.action_create_quotation()
                if isinstance(q_resp, dict) and q_resp.get('status') is False:
                    errors.append(_("%(name)s: %(msg)s") % {
                        'name': booking.name,
                        'msg': q_resp.get('message') or _('quotation failed'),
                    })
                    continue
            except Exception as e:
                errors.append(_("%(name)s: quotation error – %(err)s") % {
                    'name': booking.name, 'err': str(e),
                })
                continue

            if hasattr(booking, 'refresh_from_db'):
                booking.refresh_from_db(fields=['sale_order'])

            try:
                p_resp = booking.action_create_purchase_order()
                if isinstance(p_resp, dict) and p_resp.get('status') is False:
                    errors.append(_("%(name)s PO: %(msg)s") % {
                        'name': booking.name,
                        'msg': p_resp.get('message') or _('no POs created'),
                    })
            except Exception as e:
                errors.append(_("%(name)s: PO error – %(err)s") % {
                    'name': booking.name, 'err': str(e),
                })

            po_count_after = PurchaseOrder.objects.filter(tour_booking=booking).count()
            new_pos = po_count_after - po_count_before
            so_name = booking.sale_order.name if booking.sale_order else '—'
            so_label = _('reused') if had_so else _('created')
            summaries.append(
                _('%(b)s: SO %(so)s (%(state)s), %(n)s new PO(s)') % {
                    'b': booking.name, 'so': so_name,
                    'state': so_label, 'n': new_pos,
                }
            )

        message = '\n'.join(summaries) if summaries else _('Nothing processed.')
        if errors:
            message = message + '\n' + _('Errors:') + ' ' + '; '.join(errors)

        return {
            'status': bool(summaries),
            'open_mode': 'message',
            'message': message,
            'data': {},
            'on_success': {'type': 'refresh'},
        }


class TourProgramYallaExtension(ModelExtension):
    """
    Extend TourProgram with pickup_time, hotel, room_num,
    and actual pricing fields for agents.
    """
    _inherit = 'tourism.tourprogram'

    pickup_time = models.DateTimeField(
        _("Pickup Time"),
        blank=True,
        null=True,
        help_text=_("Pickup time for this program day")
    )

    hotel = models.ForeignKey(
        'base.Partner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tour_programs_hotel',
        verbose_name=_("Hotel"),
        help_text=_("Hotel for this program day")
    )

    room_num = models.CharField(
        _("Room Number"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Room number at the hotel")
    )

    voucher_number = models.CharField(
        _("Voucher Number"),
        max_length=64,
        blank=True,
        null=True,
        help_text=_("Auto-generated voucher number")
    )

    actual_adult_price = models.DecimalField(
        _("Actual Adult Price"),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        null=True,
        blank=True,
        help_text=_("Agent's actual adult selling price")
    )

    actual_child_price = models.DecimalField(
        _("Actual Child Price"),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        null=True,
        blank=True,
        help_text=_("Agent's actual child selling price")
    )
    STOP_ACTIVITY_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('9+', '9+'),
        ('custom', 'Custom'),
    ]
    
    stop_activity = models.CharField(
        _("Stop/Activity"),
        max_length=10,
        choices=STOP_ACTIVITY_CHOICES,
        null=True,
        blank=True,
    )

    LUNCH_CHOICES = [
        ('none', 'None'),
        ('island', 'Island'),
        ('onboard', 'Onboard'),
        ('restaurant', 'Rest.'),
        ('extra', 'Extra'),
    ]

    lunch_option = models.CharField(
        _("Lunch"),
        max_length=20,
        choices=LUNCH_CHOICES,
        null=True,
        blank=True,
    )

    @onchange('price_per_person')
    def _validate_price_per_person_floor(self):
        """Reject adult selling price below cost + markup; snap to floor."""
        cost = self.cost_price
        markup = self.markup
        actual = self.price_per_person

        if isinstance(cost, str):
            cost = Decimal(cost) if cost else Decimal('0.00')
        if isinstance(markup, str):
            markup = Decimal(markup) if markup else Decimal('0.00')
        if isinstance(actual, str):
            actual = Decimal(actual) if actual else Decimal('0.00')

        cost = cost or Decimal('0.00')
        markup = markup or Decimal('0.00')
        actual = actual or Decimal('0.00')

        min_allowed = cost + markup
        if actual and actual < min_allowed:
            return {
                'value': {'price_per_person': float(min_allowed)},
                'warning': {
                    'title': 'Error',
                    'message': _(
                        'Adult Price (%(actual)s) cannot be lower than '
                        'cost + markup (%(min)s). Resetting to minimum.'
                    ) % {'actual': actual, 'min': min_allowed}
                }
            }

    @onchange('child_price')
    def _validate_child_price_floor(self):
        """Reject child selling price below child_cost + markup; snap to floor."""
        cost = self.child_cost
        markup = self.markup
        actual = self.child_price

        if isinstance(cost, str):
            cost = Decimal(cost) if cost else Decimal('0.00')
        if isinstance(markup, str):
            markup = Decimal(markup) if markup else Decimal('0.00')
        if isinstance(actual, str):
            actual = Decimal(actual) if actual else Decimal('0.00')

        cost = cost or Decimal('0.00')
        markup = markup or Decimal('0.00')
        actual = actual or Decimal('0.00')

        min_allowed = cost + markup
        if actual and actual < min_allowed:
            return {
                'value': {'child_price': float(min_allowed)},
                'warning': {
                    'title': 'Error',
                    'message': _(
                        'Child Price (%(actual)s) cannot be lower than '
                        'child cost + markup (%(min)s). Resetting to minimum.'
                    ) % {'actual': actual, 'min': min_allowed}
                }
            }

    def pre_create(self):
        """Auto-generate voucher number on creation."""
        if not self.voucher_number:
            from modules.base.models import Sequence
            try:
                self.voucher_number = Sequence.get_next_by_code('tourism.voucher')
            except Exception:
                pass

    @action
    def action_print_voucher(self):
        """Print tour program voucher as PDF."""
        from modules.base.services.report_service import report_service

        for program in self:
            return report_service.generate_report(
                report_name='tourism.report_program_voucher',
                record_ids=[program.id],
                user=program.env.user if hasattr(program, 'env') else None
            )


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
                    'menu_item_key': 'yalla_thailand_available_tours',
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
