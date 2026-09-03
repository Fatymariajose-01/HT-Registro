import abc
import smtplib
import urllib.request
import urllib.error
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class EmailProvider(abc.ABC):
    @abc.abstractmethod
    def send_validation_email(self, to_email: str, name: str, token: str) -> bool:
        """
        Envía un correo electrónico de validación de cuenta al usuario.
        """
        pass

class ConsoleEmailProvider(EmailProvider):
    """
    Proveedor para desarrollo: imprime el correo en la consola.
    """
    def send_validation_email(self, to_email: str, name: str, token: str) -> bool:
        validation_url = f"http://localhost:5000/api/verify?token={token}"
        print("\n" + "=" * 60)
        print("SIMULACIÓN DE ENVÍO DE CORREO (CONSOLE PROVIDER)")
        print(f"Para: {name} <{to_email}>")
        print("Asunto: Verifica tu cuenta")
        print("-" * 60)
        print(f"Hola {name},")
        print("Gracias por registrarte. Por favor, verifica tu cuenta haciendo clic en el siguiente enlace:")
        print(f"-> {validation_url}")
        print("=" * 60 + "\n")
        return True

class SMTPEmailProvider(EmailProvider):
    """
    Proveedor real: envía correos utilizando un servidor SMTP configurable (ej. Gmail SMTP).
    """
    def send_validation_email(self, to_email: str, name: str, token: str) -> bool:
        # Recuperar credenciales y configuración
        smtp_server = Config.SMTP_SERVER.strip() if Config.SMTP_SERVER else "smtp.gmail.com"
        try:
            smtp_port = int(Config.SMTP_PORT) if Config.SMTP_PORT else 587
        except (ValueError, TypeError):
            smtp_port = 587

        smtp_username = Config.SMTP_USERNAME.strip() if Config.SMTP_USERNAME else ""
        smtp_password = Config.SMTP_PASSWORD.strip() if Config.SMTP_PASSWORD else ""
        sender_email = (Config.SMTP_SENDER or smtp_username).strip()
        
        if not smtp_server or not smtp_username or not smtp_password:
            print("\n" + "=" * 60)
            print("ERROR: Configuración de SMTP incompleta en .env.")
            print("Asegúrate de definir SMTP_SERVER, SMTP_USERNAME y SMTP_PASSWORD.")
            print("=" * 60 + "\n")
            return False

        validation_url = f"http://localhost:5000/api/verify?token={token}"
        
        # Crear mensaje
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verifica tu cuenta - Registro Extensible"
        message["From"] = f"Registro Extensible <{sender_email}>"
        message["To"] = to_email

        # Versión de texto plano
        text = f"""
        Hola {name},

        ¡Gracias por registrarte! Para activar tu cuenta, por favor haz clic en el siguiente enlace:
        {validation_url}

        Si no te has registrado en nuestro sistema, puedes ignorar este correo.
        """
        
        # Versión HTML con estilo
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
              <h2 style="color: #4f46e5; text-align: center;">¡Bienvenido, {name}!</h2>
              <p style="font-size: 16px; line-height: 1.5;">Gracias por unirte a nuestra plataforma. Para completar tu registro y activar tu cuenta de forma segura, por favor haz clic en el botón de abajo:</p>
              <div style="text-align: center; margin: 30px 0;">
                <a href="{validation_url}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Verificar mi Cuenta</a>
              </div>
              <p style="font-size: 14px; color: #777; text-align: center;">O copia y pega el siguiente enlace en tu navegador:</p>
              <p style="font-size: 14px; text-align: center; word-break: break-all;"><a href="{validation_url}" style="color: #4f46e5;">{validation_url}</a></p>
              <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
              <p style="font-size: 12px; color: #999; text-align: center;">Si no has creado esta cuenta, puedes ignorar este mensaje de forma segura.</p>
            </div>
          </body>
        </html>
        """

        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))

        try:
            if smtp_port == 465:
                # Conexión directa SSL (ej. puerto 465)
                with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15) as server:
                    server.login(smtp_username, smtp_password)
                    server.sendmail(sender_email, to_email, message.as_string())
            else:
                # Conexión estándar TLS / STARTTLS (ej. Gmail puerto 587)
                with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(sender_email, to_email, message.as_string())

            print(f"Correo de verificación enviado exitosamente a {to_email} vía SMTP ({smtp_server}:{smtp_port}).")
            return True
        except smtplib.SMTPAuthenticationError as auth_err:
            print("\n" + "=" * 60)
            print(f"ERROR DE AUTENTICACIÓN SMTP: {auth_err}")
            if "gmail.com" in smtp_server.lower():
                print("NOTA PARA GMAIL:")
                print("1. Google no permite iniciar sesión con tu contraseña habitual de Google.")
                print("2. Debes generar una 'Contraseña de aplicación' de 16 caracteres:")
                print("   -> Ve a tu Cuenta de Google -> Seguridad -> Verificación en dos pasos -> Contraseñas de aplicaciones.")
                print("3. Pega esa clave de 16 caracteres en SMTP_PASSWORD en tu archivo .env.")
            print("=" * 60 + "\n")
            return False
        except Exception as e:
            print(f"Error al enviar correo vía SMTP ({smtp_server}:{smtp_port}): {e}")
            return False

class SendGridEmailProvider(EmailProvider):
    """
    Proveedor real: envía correos utilizando la API v3 de SendGrid.
    """
    def send_validation_email(self, to_email: str, name: str, token: str) -> bool:
        api_key = Config.SENDGRID_API_KEY
        sender_email = (Config.SMTP_SENDER or "noreply@sistemaextensible.com").strip()
        
        # Si no hay API Key real, hacemos fallback a consola para que no falle el desarrollo local
        if not api_key or api_key == "SG.tu_api_key_aqui" or api_key.startswith("SG.mock_key"):
            print("\n" + "=" * 60)
            print("AVISO: SendGrid no está configurado con una API Key real en .env.")
            print("Para probar localmente sin API Key real, puedes usar EMAIL_PROVIDER=console")
            print("SIMULACIÓN DE ENVÍO DE CORREO (FALLBACK A CONSOLA):")
            validation_url = f"http://localhost:5000/api/verify?token={token}"
            print(f"Para: {name} <{to_email}>")
            print(f"Enlace de validación: {validation_url}")
            print("=" * 60 + "\n")
            return True

        validation_url = f"http://localhost:5000/api/verify?token={token}"
        
        # Construir cuerpo del correo según API v3 de SendGrid
        payload = {
            "personalizations": [
                {
                    "to": [{"email": to_email, "name": name}],
                    "subject": "Verifica tu cuenta - Registro Extensible"
                }
            ],
            "from": {
                "email": sender_email,
                "name": "Registro Extensible"
            },
            "content": [
                {
                    "type": "text/plain",
                    "value": f"Hola {name},\n\nGracias por registrarte. Verifica tu cuenta haciendo clic en: {validation_url}"
                },
                {
                    "type": "text/html",
                    "value": f"""
                    <html>
                      <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                          <h2 style="color: #4f46e5; text-align: center;">¡Bienvenido, {name}!</h2>
                          <p style="font-size: 16px; line-height: 1.5;">Gracias por registrarte. Para completar la validación de tu cuenta, haz clic en el siguiente enlace:</p>
                          <div style="text-align: center; margin: 30px 0;">
                            <a href="{validation_url}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Verificar Cuenta</a>
                          </div>
                          <p style="font-size: 12px; color: #999; text-align: center;">Si no has solicitado esta cuenta, puedes ignorar este mensaje.</p>
                        </div>
                      </body>
                    </html>
                    """
                }
            ]
        }
        
        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/mail/send",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status in (200, 202):
                    print(f"Correo de verificación enviado exitosamente a {to_email} vía API de SendGrid.")
                    return True
                else:
                    print(f"SendGrid retornó un código de estado inesperado: {response.status}")
                    return False
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"Error HTTP al enviar correo vía SendGrid: {e.code} - {e.reason}")
            print(f"Detalle de error de SendGrid: {error_body}")
            return False
        except Exception as e:
            print(f"Error general al enviar correo vía SendGrid: {e}")
            return False

class EmailProviderFactory:
    """
    Fábrica encargada de instanciar el proveedor de correo activo 
    según la configuración en las variables de entorno.
    """
    _providers = {
        "console": ConsoleEmailProvider,
        "smtp": SMTPEmailProvider,
        "gmail": SMTPEmailProvider,
        "sendgrid": SendGridEmailProvider
    }

    @classmethod
    def get_provider(cls) -> EmailProvider:
        provider_name = Config.EMAIL_PROVIDER.lower() if Config.EMAIL_PROVIDER else "console"
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            print(f"Advertencia: Proveedor '{provider_name}' no reconocido. Usando 'console' por defecto.")
            return ConsoleEmailProvider()
        return provider_class()
