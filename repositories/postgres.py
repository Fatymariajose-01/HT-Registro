import json
import psycopg2
import uuid
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from config import Config
from .base import BaseUserRepository

class PostgresUserRepository(BaseUserRepository):
    """Implementación del repositorio de usuarios para PostgreSQL."""

    def get_admin_connection(self):
        """Establece conexión a la base de datos por defecto 'postgres' para tareas administrativas."""
        return psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database="postgres"
        )

    def get_connection(self):
        """Establece conexión a la base de datos de la aplicación."""
        return psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )

    def init_db(self):
        """
        Inicializa PostgreSQL de manera automática:
        1. Crea la base de datos si no existe.
        2. Crea la tabla 'users' con los campos core y la columna JSONB 'extra_data'.
        """
        conn = None
        try:
            conn = self.get_admin_connection()
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (Config.DB_NAME,))
                exists = cursor.fetchone()
                if not exists:
                    cursor.execute(f"CREATE DATABASE {Config.DB_NAME};")
                    print(f"[PostgreSQL] Base de datos '{Config.DB_NAME}' creada con éxito.")
                else:
                    print(f"[PostgreSQL] Base de datos '{Config.DB_NAME}' ya existe.")
        except Exception as e:
            print(f"[PostgreSQL] Alerta administrativa: {e}. Intentando conectar directamente...")
        finally:
            if conn:
                conn.close()

        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    age INTEGER NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    extra_data JSONB DEFAULT '{}'::jsonb,
                    is_verified BOOLEAN DEFAULT FALSE,
                    verification_token VARCHAR(255) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                cursor.execute(create_table_query)
                
                alter_queries = [
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255) UNIQUE;"
                ]
                for query in alter_queries:
                    cursor.execute(query)
                    
                conn.commit()
                print("[PostgreSQL] Tabla 'users' verificada/creada exitosamente.")
        except Exception as e:
            print(f"[PostgreSQL] Error al inicializar tabla 'users': {e}")
            raise e
        finally:
            if conn:
                conn.close()

    def save_user(self, form_data: dict, registered_fields: list) -> tuple[bool, str, str | None]:
        """Guarda un usuario en PostgreSQL con contraseña hasheada y token de validación."""
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
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
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
                user_id = cursor.fetchone()[0]
                conn.commit()
                return True, f"Usuario registrado exitosamente con ID: {user_id}. Se ha enviado un correo de verificación.", verification_token
        except psycopg2.errors.UniqueViolation:
            if conn:
                conn.rollback()
            return False, "El correo electrónico ya se encuentra registrado.", None
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error en base de datos al guardar usuario: {str(e)}", None
        finally:
            if conn:
                conn.close()

    def get_all_users(self) -> list[dict]:
        """Recupera todos los usuarios de PostgreSQL."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, email, name, last_name, age, extra_data, is_verified, created_at FROM users ORDER BY created_at DESC;")
                records = cursor.fetchall()
                for rec in records:
                    if rec.get("created_at"):
                        rec["created_at"] = rec["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                return records
        except Exception as e:
            print(f"[PostgreSQL] Error al recuperar usuarios: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def verify_user_token(self, token: str) -> tuple[bool, str]:
        """Verifica el token de usuario en PostgreSQL."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, email, is_verified FROM users WHERE verification_token = %s;", (token,))
                row = cursor.fetchone()
                if not row:
                    return False, "Token de verificación inválido o vencido."
                
                user_id, email, is_verified = row
                if is_verified:
                    return True, "Esta cuenta ya ha sido verificada anteriormente."
                
                cursor.execute("UPDATE users SET is_verified = True WHERE id = %s;", (user_id,))
                conn.commit()
                return True, "Cuenta verificada con éxito. ¡Ya puedes usar tu cuenta!"
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error en base de datos al verificar cuenta: {str(e)}"
        finally:
            if conn:
                conn.close()
