from flask import Flask, redirect, url_for, request, render_template, Response
from flask_mail import Mail, Message
import os
import json
import requests
from multiprocessing import Pool

app = Flask(__name__)


def send_mail(form_msg, form_name, form_email):
    print("inside async")
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587  # 465 for SSL
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False  # True
    app.config['MAIL_USERNAME'] = 'dibyadasiscool@gmail.com'
    app.config['MAIL_PASSWORD'] = 'samsunghp'
    print("all config done")
    mail = Mail(app)
    print("init mail app")
    form_data = form_msg  # request.form['msg']
    print("message taken")
    msg = Message('Query', sender='dibyadasiscool@gmail.com',
                  recipients=['dibyadas998@gmail.com'])
    print("message init")
    msg.body = "Query sent by:- " + form_name + "\n" + \
        form_data + "\n" + "Email-ID is:- " + form_email
    print("body made")
    print("going to send the msg")
    mail.send(msg)
    print("sent")
    return None


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