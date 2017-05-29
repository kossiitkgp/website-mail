from flask import Flask, redirect, url_for, request, render_template, Response
from flask_mail import Mail, Message
import os
import json
import requests
from multiprocessing import Pool


app = Flask(__name__)


def send_mail(form_msg, form_name, form_email):
    print("inside async")
    app.config['MAIL_SERVER'] = os.environ['MAIL_SERVER']
    app.config['MAIL_PORT'] = os.environ['MAIL_PORT']  # 465 for SSL
    app.config['MAIL_USE_TLS'] = os.environ['MAIL_USE_TLS']
    app.config['MAIL_USE_SSL'] = os.environ['MAIL_USE_SSL']  # True
    app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
    print("all config done")
    mail = Mail(app)
    print("init KOSS mail app")

    # query mail to KOSS
    form_data = form_msg  # request.form['msg']
    print("message taken")
    msg = Message('Query', sender='dibyadasiscool@gmail.com',
                  recipients=[os.environ['KOSS_EMAIL_ID']])
    print("message init")
    msg.body = "Query sent by:- " + form_name + "\n\n" +\
        form_data + "\n\n" + "Email-ID is:- " + form_email
    print("body made")
    print("going to send the msg")
    mail.send(msg)
    print("sent")

    # conformation mail to user
    print("message taken")
    msg = Message('Query Recieved', sender='dibyadasiscool@gmail.com',
                  recipients=[form_email])
    print("message init")
    msg.body = "Hi "+sender_name+",\n\n"+"Your message has been recieved by us and we will responded to it soon."+"\nThank-you for communicating with us, hope your query will cleared by our team."+"\n\n\nKOSS IIT Kharagpur"
    print("body made")
    print("going to send the msg")
    mail.send(msg)
    print("sent")

    slack_notifier(form_msg, form_name, form_email)
    return None


def slack_notifier(form_msg, form_name, form_email,count=0):
    headers = {"Content-Type": "application/json"}

    data = json.dumps({"text": "Query from "+form_name+"<"+form_email+">\n\n"+"QUERY : "+form_msg+"\n\nPlease respond soon."})
       
    r = requests.post(os.environ["SLACK_WEBHOOK_URL"], headers=headers, data=data)

    if r.status_code!=200:
        if count<=2:
            print("error "+r.status_code+" !!! trying again")
            count+=1
            slack_notifier(form_msg, form_name, form_email,count)
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


@app.route('/captcha',methods=['POST'])
def captcha():
    t = json.loads(request.data.decode("utf-8"))
    key = t['key']
    gcaptcha = t['gcaptcha']
    r = requests.post("https://www.google.com/recaptcha/api/siteverify",data = { 'secret' : key, 'response' : gcaptcha } )
    if json.loads(r.content.decode('utf-8'))['success'] == True:
        return ("sent", 200, {'Access-Control-Allow-Origin': '*'})
    else:
        return ("Not sent", 400, {'Access-Control-Allow-Origin': '*'})


# if __name__ == "__main__":  # This is for local testin
#     app.run(host='localhost', port=3453, debug=True)


if __name__ == "__main__":  # This will come in use when
    port = int(os.environ.get("PORT", 5000))  # the app is deployed on heroku
    app.run(host='0.0.0.0', port=port,debug=True)
