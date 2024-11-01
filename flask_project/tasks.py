import os
from celery import shared_task
from flask_mail import Message
from flask import render_template
from flask_project import celery, mail
from flask_project.models import Service_Request, Customer, Service_Professional
import logging
from celery.schedules import crontab
from flask_project import app as capp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task
def send_daily_reminders():
    logger.info("Sending daily reminders...")

    with capp.app_context():
        pending_requests = Service_Request.query.filter_by(service_status="requested").all()
        for request in pending_requests:
            for professional in Service_Professional.query.filter_by(service_id=request.service_id).all():
                if professional:
                    msg = Message('Pending Service Request', recipients=[professional.email])
                    msg.body = f"Reminder: There is an unassigned pending service request for {request.service.name}. Please take action."
                    mail.send(msg)
    return "Reminders Sent"

@shared_task
def send_monthly_report():
    with capp.app_context():
        customers = Customer.query.all()
        for customer in customers:
            past_requests = Service_Request.query.filter_by(customer_id=customer.id).all()
            html_content = render_template('monthly_report.html', requests=past_requests, customer=customer)
            msg = Message('Your Monthly Activity Report', recipients=[customer.email])
            msg.html = html_content
            mail.send(msg)
    logger.info("Monthly reports sent.")

@celery.task
def export_as_csv(professional_id):
    file_path = ''
    with capp.app_context():
        closed_requests = Service_Request.query.filter_by(service_professional_id=professional_id).all()
        csv_content = "Service_ID,Service_Status,Customer_ID,Date_of_Request\n"
        for request in closed_requests:
            csv_content += f"{request.service_id},{request.service_id},{request.customer_id},{request.date_of_request}\n"
        static_dir = os.path.join(capp.root_path, 'static')
        file_path = os.path.join(static_dir+"/reports", f'service_requests_{professional_id}.csv')
        with open(file_path, 'w') as file:
            file.write(csv_content)
    return file_path

@celery.on_after_configure.connect # type: ignore
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=9, minute=0), send_daily_reminders.s()) # type: ignore
    
    sender.add_periodic_task(crontab(hour=9, minute=0, day_of_month='1'), send_monthly_report.s()) # type: ignore
