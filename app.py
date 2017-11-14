from flask import Flask, redirect, url_for, request, render_template, Response
import os
import json
import requests
from multiprocessing import Pool
import sendgrid
from sendgrid.helpers.mail import *
import urllib

app = Flask(__name__)

# reg_message_old = """
# Hey,<br><br>

# Thanks for mentoring and registering your project with us. We will get in touch with you soon!
# <br><br>
# Regards,<br>
# <strong>Kharagpur Open Source Society</strong>
# """


reg_message = """
Hello {},<br><br>

Thank you for registering your project {} in Kharagpur Winter of Code 2017. We will get in touch with you soon!
<br>
Meanwhile you can read the Mentor's manual <a href='https://kwoc.kossiitkgp.in/static/files/KWoCMentorManual.pdf'>here</a>.<br><br>

Regards,<br>
<strong>Kharagpur Open Source Society</strong>
"""



query_message = """

Hi {},<br><br>

Your message has been recieved by us and we will respond to it soon. Thank you for communicating with us. Have a good day!.
<br><br>
Regards, <br>
<strong>Kharagpur Open Source Society</strong>

"""


def send_mail(form_msg, form_name, form_email):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
    # print("init")
    from_email = Email(form_email)
    # print("email init")
    to_email = [Email(os.environ['KOSS_EMAIL']),Email('dibyadascool@gmail.com')]
    # print("email init2")
    subject = "Query"
    # print("subject")
    content = Content("text/plain", "Query sent by:- " + form_name + "\n\n\n" +
                      "Message:- " + form_msg + "\n")
    # print("content")
    for id in to_email:
        mail = Mail(from_email=from_email, subject=subject,
                    to_email=id, content=content)
        # print("mail init")
        try:
            response = sg.client.mail.send.post(request_body=mail.get())
            # print("sent")
        except urllib.error.HTTPError:
            print("not sent")
            slack_notifier(mode=1)
        except Exception:
            print("Some other exception occured. Not sent")
            slack_notifier(mode=2)

    from_email = Email(email=os.environ['KOSS_EMAIL'],name="Kharagpur Open Source Society")
    # print("email init")
    to_email = Email(form_email)
    # print("email init2")
    subject = "Query Recieved"
    # print("subject")
    content = Content("text/html", query_message.format(form_name))
    # print("content")
    mail = Mail(from_email=from_email, subject=subject,
                to_email=to_email, content=content)
    # print("mail init")
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        # print("sent")
    except urllib.error.HTTPError:
        print("not sent")
        slack_notifier(mode=1)
    except Exception:
        print("Some other exception occured. Not sent")
        slack_notifier(mode=2)

    slack_notifier(form_msg, form_name, form_email)
    return None


# slack notifier module
def slack_notifier(form_msg="", form_name="", form_email="", mode=0, count=0):
    headers = {"Content-Type": "application/json"}
    if mode == 0:
        data = json.dumps({"text": ("Query from {}<{}>\n\nQUERY : {}\n\n{}Please respond"
                            " soon.".format(form_name,form_email,form_msg,"="*17+"\n"))})

    elif mode == 1:
        data = json.dumps({"text": "HTTP Error occured in the mailing app\
                               \n\n Please Check."})
    else:
        data = json.dumps({"text": "Some Error occured in the mailing app\
                               \n\n Please Check."})

    r = requests.post(
           os.environ["SLACK_WEBHOOK_URL"], headers=headers, data=data)

    if r.status_code != 200:
        if count <= 2:
            print("error "+str(r.status_code)+" !!! trying again")
            count += 1
            slack_notifier(form_msg, form_name, form_email, count)
        else:
            print("terminated!!!")
    else:
        print("notification sent!!!")


@app.route('/mail', methods=['POST'])
def mail():
    pool = Pool(processes=10)
    r = pool.apply_async(
        send_mail, [request.form['msg'],
                    request.form['name'],
                    request.form['email']])
    return ("sent", 200, {'Access-Control-Allow-Origin': '*'})


@app.route('/captcha', methods=['POST'])
def captcha():
    t = json.loads(request.data.decode("utf-8"))
    gcaptcha = t['gcaptcha']
    r = requests.post("https://www.google.com/recaptcha/api/siteverify",
                      data={'secret': os.environ['KEY'], 'response': gcaptcha})
    if json.loads(r.content.decode('utf-8'))['success'] is True:
        return ("sent", 200, {'Access-Control-Allow-Origin': '*'})
    else:
        return ("Not sent", 400, {'Access-Control-Allow-Origin': '*'})


@app.route('/update_sheet',methods=['POST'])
def update_sheet():
    sheet_url = "https://script.google.com/macros/s/AKfycbzvd8_P6BrP-C04-4KwbM3z-3Mh7_BGnkmDCRCU-Vg5BSug_ETx/exec"
    json_d = request.form.to_dict()
    print(json_d)
    r = requests.post(sheet_url,data=json_d)
    print(r.status_code)
    reg_mail(json_d['name'],json_d['email'],json_d['project'])
    return ("updated", 200, {'Access-Control-Allow-Origin': '*'})


def reg_mail(name,form_email,project):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
    from_email = Email(form_email)
    to_email = [Email('dibyadascool@gmail.com'),Email(os.environ['KOSS_EMAIL'])]  # os.environ['KWOC_EMAIL']

    subject = "Mentor Registration"

    content = Content("text/plain", "New registration by:- " + name );

    for id in to_email:
        mail = Mail(from_email=from_email, subject=subject,
                    to_email=id, content=content)
        try:
            response = sg.client.mail.send.post(request_body=mail.get())
        except urllib.error.HTTPError:
            print("not sent")
        except Exception:
            print("Some other exception occured. Not sent")

    from_email = Email(email=os.environ['KWOC_EMAIL'],name="Kharagpur Winter of Code")
    to_email = Email(form_email)
    subject = "Thank you for registering project {} in Kharagpur Winter of Code 2017".format(project)

    content = Content('text/html',reg_message.format(name,project))

    mail = Mail(from_email=from_email, subject=subject,
                to_email=to_email, content=content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except urllib.error.HTTPError:
        print("not sent")
    except Exception as e:
        print(e)
        print("Some other exception occured. Not sent")
    return None

# if __name__ == "__main__":  # This is for local testin
#     app.run(host='localhost', port=3453, debug=True)


if __name__ == "__main__":  # This will come in use when
    port = int(os.environ.get("PORT", 5000))  # the app is deployed on heroku
    app.run(host='0.0.0.0', port=port, debug=True)
