from email import encoders
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from ftplib import FTP
import time
import schedule
from config import settings

def get_csv(ip:str, user:str, passwd:str):
    ftp = FTP(ip, user=user, passwd=passwd)

    ftp.cwd('UserLogs/Csv')
    ftp.retrlines('LIST')
    with open(f'{settings.EMAIL.ASSUNTO}.csv', 'wb') as file:
        ftp.retrbinary(f'RETR {settings.SUEZ.NOME_ARQUIVO}', file.write)



def send_mail():
    msg = MIMEMultipart()
       

    msg['From'] = settings.EMAIL.ENDERECO
    msg['To'] = ','.join(settings.EMAIL.DESTINATARIOS)
    msg['Subject'] = settings.EMAIL.ASSUNTO

    body = "Integração SUEZ"

    msg.attach(MIMEText(body, 'plain'))    
    
    get_csv(
        ip=settings.SUEZ.FTP,
        user=settings.SUEZ.USUARIO,
        passwd=settings.SUEZ.SENHA
    )
    
    filename = f'{settings.EMAIL.ASSUNTO}.csv'
    
    anexo = open(filename, 'rb')
    
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((anexo).read())
    encoders.encode_base64(p)

    p.add_header('Content-Disposition',"anexo; filename= %s" % filename)
    msg.attach(p)
    text = msg.as_string()

    s = smtplib.SMTP(settings.EMAIL.SMTP)
    s.ehlo()
    s.starttls()
    s.login(settings.EMAIL.ENDERECO,settings.EMAIL.SENHA)
    s.sendmail(settings.EMAIL.ENDERECO, settings.EMAIL.DESTINATARIOS, text)
    s.quit()


schedule.every(settings.INTERVALO).hour.do(send_mail)

send_mail()

while True:
    try:
        schedule.run_pending()
    except Exception as e:
        print(e)    
    time.sleep(1)