from flask import Flask, redirect, url_for, request, render_template, Response
import os
import json
import requests
from multiprocessing import Pool
import sendgrid
from sendgrid.helpers.mail import *

html =  """\
        <html>
          <head></head>
          <body>
            <p>Greetings from KOSS, IIT Kharagpur.<br>
               We, at Kharagpur Open Source Society, are glad to announce that this year we will be conducting the third edition of Kharagpur Winter of Code (KWoC), a one month programme, open to students all across the globe.
            </p>
            <p>We thank you for your previous participation with the programme and would like to invite you for mentoring in the third edition.</p>
            <p>This would be your chance to grow your Open Source project and help budding developers at the same time.</p>
            <p>Please register your project at: <a href="https://kwoc.kossiitkgp.org/mentor_form">https://kwoc.kossiitkgp.org/mentor_form</a><br>
            You can read more about mentoring in the Mentor Manual: <a href="http://bit.ly/kwoc18mentormanual">http://bit.ly/kwoc18mentormanual</a>
            </p>
            <p>With regards,<br>
            <a href="https://kossiitkgp.org">Kharagpur Open Source Society</a>,<br>
            <a href="http://iitkgp.ac.in">Indian Institute of Technology Kharagpur</a>.
          </body>
        </html>
        """ # The /n separates the message from the headers

def reg_mail(form_email):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
    # print("init")
    from_email = Email('KWoC <kwoc@kossiitkgp.in>')
    # print("email init")
    to_email = form_email
    # print("email init2")
    subject = "KWoC 2018: Request for Mentorship"
    # print("subject")
    content = Content("text/html", html );
    # print("content")
    for id in to_email:
        mail = Mail(from_email=from_email, subject=subject,
                    to_email=Email(id), content=content)
        # print("mail init")
        try:
            response = sg.client.mail.send.post(request_body=mail.get())
            print("sent to "+str(id))
        except urllib.error.HTTPError:
            print("not sent")
        except Exception:
            print("Some other exception occured. Not sent")

emails = []
reg_mail(emails)