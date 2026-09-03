import json
import uuid
import pymysql
import pymysql.cursors
import pymysql.err
from werkzeug.security import generate_password_hash
from config import Config
from .base import BaseUserRepository

class MySQLUserRepository(BaseUserRepository):
    """Implementación del repositorio de usuarios para MySQL / MariaDB."""

    def get_admin_connection(self):
        """Establece conexión al servidor MySQL para tareas administrativas (creación de BD)."""
        return pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_connection(self):
        """Establece conexión a la base de datos de la aplicación en MySQL."""
        return pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def init_db(self):
        """
        Inicializa MySQL de manera automática:
        1. Crea la base de datos si no existe.
        2. Crea la tabla 'users' con columnas core y columna JSON 'extra_data'.
        """
        conn = None
        try:
            conn = self.get_admin_connection()
            with conn.cursor() as cursor:
                create_db_query = f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                cursor.execute(create_db_query)
                conn.commit()
                print(f"[MySQL] Base de datos '{Config.DB_NAME}' verificada/creada exitosamente.")
        except Exception as e:
            print(f"[MySQL] Alerta administrativa: {e}. Intentando conectar directamente...")
        finally:
            if conn:
                conn.close()

        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    extra_data JSON NULL,
                    is_verified BOOLEAN DEFAULT FALSE,
                    verification_token VARCHAR(255) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
                cursor.execute(create_table_query)
                conn.commit()
                print("[MySQL] Tabla 'users' verificada/creada exitosamente.")
        except Exception as e:
            print(f"[MySQL] Error crítico al inicializar tabla 'users': {e}")
            raise e
        finally:
            if conn:
                conn.close()

    def save_user(self, form_data: dict, registered_fields: list) -> tuple[bool, str, str | None]:
        """Guarda un usuario en MySQL con contraseña hasheada y token de validación."""
        core_keys = {"email", "name", "last_name", "age", "password"}
        
        email = form_data.get("email", "").strip().lower()
        name = form_data.get("name", "").strip()
        last_name = form_data.get("last_name", "").strip()
        
        try:
            age = int(form_data.get("age"))
        except (ValueError, TypeError):
            return False, "La edad debe ser un número válido.", None
            
        password_hash = generate_password_hash(form_data.get("password", ""))
        verification_token = uuid.uuid4().hex
        
        extra_data = {}
        for field in registered_fields:
            if field.name not in core_keys:
                extra_data[field.name] = form_data.get(field.name)
                
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO users (email, name, last_name, age, password, extra_data, verification_token)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (
                    email,
                    name,
                    last_name,
                    age,
                    password_hash,
                    json.dumps(extra_data),
                    verification_token
                ))
                user_id = cursor.lastrowid
                conn.commit()
                return True, f"Usuario registrado exitosamente con ID: {user_id}. Se ha enviado un correo de verificación.", verification_token
        except pymysql.err.IntegrityError as e:
            if conn:
                conn.rollback()
            if len(e.args) > 0 and e.args[0] == 1062:
                return False, "El correo electrónico ya se encuentra registrado.", None
            return False, f"Error de duplicidad o integridad en MySQL: {str(e)}", None
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error en base de datos al guardar usuario: {str(e)}", None
        finally:
            if conn:
                conn.close()

    def get_all_users(self) -> list[dict]:
        """Recupera todos los registros de usuarios desde MySQL."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, email, name, last_name, age, extra_data, is_verified, created_at FROM users ORDER BY created_at DESC;")
                records = cursor.fetchall()
                for rec in records:
                    # Normalizar created_at
                    if rec.get("created_at") and hasattr(rec["created_at"], "strftime"):
                        rec["created_at"] = rec["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Normalizar boolean en MySQL (TINYINT 1/0 a bool)
                    rec["is_verified"] = bool(rec.get("is_verified"))
                    
                    # Normalizar extra_data si viene como string en versiones específicas
                    if isinstance(rec.get("extra_data"), str):
                        try:
                            rec["extra_data"] = json.loads(rec["extra_data"])
                        except Exception:
                            rec["extra_data"] = {}
                    elif rec.get("extra_data") is None:
                        rec["extra_data"] = {}
                return records
        except Exception as e:
            print(f"[MySQL] Error al recuperar usuarios: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def verify_user_token(self, token: str) -> tuple[bool, str]:
        """Verifica el token de usuario en MySQL."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, email, is_verified FROM users WHERE verification_token = %s;", (token,))
                row = cursor.fetchone()
                if not row:
                    return False, "Token de verificación inválido o vencido."
                
                user_id = row["id"]
                is_verified = bool(row["is_verified"])
                if is_verified:
                    return True, "Esta cuenta ya ha sido verificada anteriormente."
                
                cursor.execute("UPDATE users SET is_verified = TRUE WHERE id = %s;", (user_id,))
                conn.commit()
                return True, "Cuenta verificada con éxito. ¡Ya puedes usar tu cuenta!"
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error en base de datos al verificar cuenta: {str(e)}"
        finally:
            if conn:
                conn.close()
