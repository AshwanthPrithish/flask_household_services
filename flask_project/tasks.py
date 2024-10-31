from celery import shared_task
from flask_mail import Message
from datetime import datetime, timedelta
from flask import render_template
from flask_project import mail, db
from flask_project.models import Service_Request, Customer, Service_Professional

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task
def send_daily_reminders():
    logger.info("sending daily remainer...")
    # pending_requests = Service_Request.query.filter_by(service_status="requested").all()
    # for request in pending_requests:
    #     for professional in Service_Professional.query.filter_by(service_id=request.service_id).all():
    #         if professional:
    #             msg = Message('Pending Service Request', recipients=[professional.email])
    #             msg.body = f"Reminder: There is an unassigned pending service request for {request.service.name}. Please take action."
    #             mail.send(msg)
    return "Reminders Sent"

@shared_task
def send_monthly_report(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        past_requests = Service_Request.query.filter_by(customer_id=customer.id).all()
        html_content = render_template('monthly_report.html', requests=past_requests, customer=customer)
        msg = Message('Your Monthly Activity Report', recipients=[customer.email])
        msg.html = html_content
        mail.send(msg)
    return f"Report sent to {customer.email}" # type: ignore

@shared_task
def export_as_csv(professional_id):
    # Export service requests closed by the professional as CSV
    professional = Service_Professional.query.get(professional_id)
    closed_requests = Service_Request.query.filter_by(service_professional_id=professional_id, service_status="completed").all()
    # Prepare CSV content
    csv_content = "Service ID, Customer ID, Date of Request, Remarks\n"
    for request in closed_requests:
        csv_content += f"{request.service_id}, {request.customer_id}, {request.date_of_request}, {request.remarks}\n"
    # Optionally save to file or send via email
    file_path = f"/path/to/csv/service_requests_{professional_id}.csv"
    with open(file_path, 'w') as file:
        file.write(csv_content)
    return file_path
