# chat_utils.py

import os
from pathlib import Path
from google.oauth2 import service_account
from langchain_google_vertexai import ChatVertexAI
from langchain.schema import Document
from vertexai.language_models import TextEmbeddingModel
from google.cloud import aiplatform

# -------------------------------
# Función para configurar credenciales de Google Cloud
# -------------------------------
def setup_google_credentials(credentials_path: str = "creds/credentials.json"):
    """
    Configura las credenciales de Google Cloud desde un archivo JSON.
    
    Args:
        credentials_path (str): Ruta al archivo de credenciales JSON
    
    Returns:
        service_account.Credentials: Objeto de credenciales configurado
    """
    # Si la ruta no es absoluta, construir la ruta absoluta desde la raíz del proyecto
    if not os.path.isabs(credentials_path):
        # Obtener la ruta del directorio actual del archivo
        current_dir = Path(__file__).parent
        # Subir un nivel para llegar a la raíz del proyecto
        project_root = current_dir.parent
        # Construir la ruta completa al archivo de credenciales
        credentials_path = project_root / credentials_path
    
    # Convertir a string si es un objeto Path
    credentials_path = str(credentials_path)
    
    # Debug: imprimir información útil
    print(f"[DEBUG] Buscando credenciales en: {credentials_path}")
    print(f"[DEBUG] Directorio actual existe: {os.path.exists(os.path.dirname(credentials_path))}")
    print(f"[DEBUG] Archivo existe: {os.path.exists(credentials_path)}")
    
    if not os.path.exists(credentials_path):
        # Listar archivos en el directorio para ayudar con debug
        parent_dir = os.path.dirname(credentials_path)
        if os.path.exists(parent_dir):
            files_in_dir = os.listdir(parent_dir)
            print(f"[DEBUG] Archivos en {parent_dir}: {files_in_dir}")
        
        raise FileNotFoundError(
            f"Archivo de credenciales no encontrado en: {credentials_path}\n"
            f"Asegúrate de que el archivo credentials.json existe en la carpeta creds/"
        )
    
    # Configurar la variable de entorno para las credenciales
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    
    # Cargar las credenciales desde el archivo
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        print(f"[DEBUG] Credenciales cargadas exitosamente desde: {credentials_path}")
        return credentials
    except Exception as e:
        raise RuntimeError(f"Error al cargar credenciales desde {credentials_path}: {e}")

# -------------------------------
# Clase para configurar Vertex AI LLM
# -------------------------------
class VertexAILLM:
    def __init__(
        self,
        project: str,
        model_name: str = "gemini-2.5-pro-preview-05-06",
        temperature: float = 0,
        max_output_tokens: int = 4000,
        location: str = "global",
        credentials_path: str = "creds/credentials.json"
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.project = project
        self.location = location
        self.credentials_path = credentials_path

        # Configurar credenciales
        self.credentials = setup_google_credentials(self.credentials_path)

        # Inicializa el modelo al crear la clase
        self.llm = ChatVertexAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            project=self.project,
            location=self.location,
            credentials=self.credentials
        )

    def get_model(self):
        """Devuelve la instancia del modelo configurado"""
        return self.llm


# -------------------------------
# Clase para cargar prompts desde archivos .txt
# -------------------------------
class PromptLoader:
    @staticmethod
    def load_txt_prompt(path: str) -> str:
        """
        Carga el contenido de un archivo .txt y lo retorna como string.
        
        Args:
            path (str): Ruta al archivo .txt
        
        Returns:
            str: Contenido del archivo
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo '{path}' no fue encontrado.")
        except Exception as e:
            raise RuntimeError(f"Error al leer el archivo '{path}': {e}")
