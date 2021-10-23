import logging
# import smtplib
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict
from emails.template import JinjaTemplate
import emails

# from services.email_service import send_email, send_reset_password_email

# subject = "Grab dinner this weekend?"
# body = 'How about dinner at 6pm this saturday?'
# msg = f"Subject: {subject}\n\n{body}"
# with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
# 	smtp.ehlo()
# 	smtp.starttls()
# 	smtp.ehlo()
#
# 	smtp.login(user='armansoltanian@gmail.com', password="ukjoxtwvciesgqnq")
# 	smtp.sendmail(
# 		'armansoltanian@gmail.com',
# 		'armansoltanian@gmail.com',
# 		msg
# 	)
msg = EmailMessage()
msg['Subject'] = 'grab dinner at night'
msg['From'] = 'armansoltanian@gmail.com'
msg['to'] = 'armansoltanian@gmail.com'
msg.set_content('how about dinner tonight')


def sent_id():
	with open(Path('/app/email-templates/build') / "new_account.html") as f:
		template_str = f.read()
	Message = emails.Message(
		subject='test grab dinner at night',
		mail_from='api.myawesomesite.io',
		mail_to='armansoltanian@gmail.com',
		# text='text message',
		html=JinjaTemplate(template_str),
	)
	smtp_options = {
		"host": 'smtp.gmail.com',
		"port": '587',
		"tls": True,
		"user": 'armansoltanian@gmail.com',
		"password": 'ukjoxtwvciesgqnq'
	}
	res = Message.send(
		smtp=smtp_options
	)
	print(res)
	return res
a=sent_id()
print(a)
# with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
# 	smtp.ehlo()
# 	smtp.starttls()
# 	smtp.ehlo()
# 	smtp.login(user='armansoltanian@gmail.com', password="ukjoxtwvciesgqnq")
# 	smtp.send_message(msg)

# def test_send_email(
# 	email_to: str,
# 	subject_template: str = "",
# 	html_template: str = "",
# 	environment: Dict[str, Any] = {},
# ) -> None:
# 	# assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
# 	message = emails.Message(
# 		subject=JinjaTemplate(subject_template),
# 		html=JinjaTemplate(html_template),
# 		mail_from=('myawesomesite', 'armansoltanian@gmail.com'),
# 	)
# 	# smtp_options = {
# 	# 	"host": 'smtp.gmail.com', "port": '587', "tls": True, "user": 'armansoltanian@gmail.com',
# 	# 	"password": 'ukjoxtwvciesgqnq'
# 	# }
# 	smtp_options = {"host": 'smtp.gmail.com', "port": '587'}
# 	smtp_options["tls"] = True
# 	smtp_options["user"] = 'armansoltanian@gmail.com'
# 	smtp_options["password"] = 'ukjoxtwvciesgqnq'
# 	response = message.send(to=email_to, render=environment, smtp=smtp_options)
# 	logging.info(f"send email result: {response}")
