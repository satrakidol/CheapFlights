# from flask_mail import Mail, Message

# app.config.update(
# MAIL_SERVER=os.environ.get('MAIL_SERVER'),
# MAIL_PORT=os.environ.get('MAIL_PORT'),
# MAIL_USE_TLS=True, #os.environ.get('MAIL_USE_TLS'),
# MAIL_USE_SSL=False, #os.environ.get('MAIL_USE_SSL'),
# MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
# MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
# )




# app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
# app.config['MAIL_PORT'] = 2525
# app.config['MAIL_USERNAME'] = '29d982c335cfe7'
# app.config['MAIL_PASSWORD'] = '6c73e952f1b209'
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False

# mail = Mail(app)

# @main.route('/email')
# def email():
#     message = Message(
#         subject = "Hey Test",
#         recipients = ['ap22017@hua.gr'],
#         sender='ap22017@hua.gr'
#     )
#     message.body = "Hey George"
#     mail.send(message)

#     return "sent"