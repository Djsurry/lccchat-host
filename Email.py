import sendgrid
import os
from sendgrid.helpers.mail import *
def sendEmail(to, subject, msg):
    sg = sendgrid.SendGridAPIClient(apikey=os.getenv("SENDGRID"))
    from_email = Email("lccchat.noreply@gmail.com")
    to_email = Email(to)
    content = Content("text/plain",msg)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    
