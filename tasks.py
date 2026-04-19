# -*- coding: utf-8 -*-
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_program_voucher_task(self, program_id, user_id=None):
    """Generate a tour program voucher PDF and send it to the booking's
    partner via WhatsApp / Messenger / Instagram."""
    from modules.tourism.models import TourProgram
    from modules.base.services.report_service import report_service
    from modules.chat.services.omnichannel_send_service import OmnichannelSendService

    try:
        program = TourProgram.objects.select_related('booking__partner').get(id=program_id)
        booking = program.booking
        partner = booking.partner if booking else None

        if not partner:
            return {'success': False, 'program_id': program_id, 'error': 'No booking partner associated'}

        user = None
        system_partner = None
        if user_id:
            from modules.base.models import User
            user = User.objects.filter(id=user_id).select_related('partner').first()
            if user:
                system_partner = user.partner

        report = report_service.generate_report(
            report_name='tourism.report_program_voucher',
            record_ids=[program.id],
            user=user,
        )
        if not report.get('status'):
            raise Exception(report.get('message') or 'Voucher report generation failed')

        pdf_url = report.get('data', {}).get('pdf_url')
        filename = report.get('data', {}).get('filename') or 'voucher.pdf'
        if not pdf_url:
            raise Exception('Voucher PDF URL missing from report response')

        result = OmnichannelSendService().send_and_broadcast(
            partner,
            {'url': pdf_url},
            message_type='document',
            filename=filename,
            caption=f"Voucher {program.voucher_number or ''}".strip(),
            conversation=None,
            system_partner=system_partner,
            websocket=True,
        )

        if result.get('success'):
            logger.info(
                f"send_program_voucher_task: program {program_id} sent via "
                f"{result.get('channel')} to partner {partner.id}"
            )
            return {
                'success': True,
                'program_id': program_id,
                'channel': result.get('channel'),
                'message_id': result.get('message_id'),
            }
        raise Exception(result.get('error') or 'Unknown error')

    except TourProgram.DoesNotExist:
        return {'success': False, 'program_id': program_id, 'error': 'Program not found'}
    except Exception as e:
        logger.error(f"Program {program_id}: Error sending voucher — {e}", exc_info=True)
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2 ** self.request.retries * 10)
        return {'success': False, 'program_id': program_id, 'error': str(e)}
