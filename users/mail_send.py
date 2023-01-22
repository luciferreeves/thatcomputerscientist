# python script for sending SMTP configuration with Oracle Cloud Infrastructure Email Delivery
import smtplib 
import email.utils
from email.message import EmailMessage
import ssl
from django.conf import settings

def send_email(sender, sender_name, recipient, subject, body_html, body_text):
    # Replace sender@example.com with your "From" address.
    # This address must be verified.
    # this is the approved sender email
    SENDER = sender
    SENDERNAME = sender_name
    
    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = recipient
    
    # Replace the USERNAME_SMTP value with your Email Delivery SMTP username.
    USERNAME_SMTP = settings.USERNAME_SMTP
    
    # Put the PASSWORD value from your Email Delivery SMTP password into the following file.
    PASSWORD_SMTP = settings.PASSWORD_SMTP
    
    # If you're using Email Delivery in a different region, replace the HOST value with an appropriate SMTP endpoint.
    # Use port 25 or 587 to connect to the SMTP endpoint.
    HOST = settings.EMAIL_HOST
    PORT = settings.EMAIL_PORT
    
    # The subject line of the email.
    SUBJECT = subject
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = body_text
    
    # The HTML body of the email.
    BODY_HTML = body_html

    # create message container
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = RECIPIENT

    # make the message multi-part alternative, making the content the first part
    msg.add_alternative(BODY_TEXT, subtype='text')
    # this adds the additional part to the message
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.add_alternative(BODY_HTML, subtype='html')

    # Try to send the message.
    try: 
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        # most python runtimes default to a set of trusted public CAs that will include the CA used by OCI Email Delivery.
        # However, on platforms lacking that default (or with an outdated set of CAs), customers may need to provide a capath that includes our public CA.
        server.starttls(context=ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None))
        # smtplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        # our requirement is that SENDER is the same as From address set previously
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.close()
    # Display an error message if something goes wrong.
    except Exception as e:
        return e
    else:
        return True