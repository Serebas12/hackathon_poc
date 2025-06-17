from langgraph.prebuilt import create_react_agent
from react_agent.chat_utils import  VertexAILLM, PromptLoader
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from dotenv import load_dotenv
from typing import Annotated
import os
from react_agent.state import State, ReactAgentState
from react_agent.tools import  cedula_tool, consulta_cedula_playwright, fecha_defuncion_tool, transfer_to_cedula, transfer_to_registraduria, transfer_to_defuncion, saldo_tool, transfer_to_saldo

load_dotenv()  # Esto carga las variables del archivo .env

project_id = os.getenv("PROJECT_ID")

# Carga del modelo de GCP
llm_gcp=VertexAILLM(project=project_id).get_model()

#creación de los agentes react 

cedula_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[cedula_tool],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
        """Eres un especialista en extracción y análisis de números de cédula de ciudadanía colombiana.

        🎯 **OBJETIVO PRINCIPAL:**
        Extraer el número de cédula de ciudadanía de documentos oficiales utilizando la herramienta cedula_tool.

        📋 **INSTRUCCIONES ESPECÍFICAS:**
        
        1. **SIEMPRE usa la herramienta cedula_tool** - NO intentes extraer el número manualmente
        
        2. **NO inventes números de cédula** - Solo proporciona información extraída por la herramienta
        
        
        3. **Formato de respuesta:**
           - Solo el número sin separadores: "12345678"
           - Si no encuentra cédula válida: "Cédula no encontrada"
           - Si hay ambigüedad: reporta el número más probable
        
        ⚠️ **IMPORTANTE:**
        - NO analices el documento tú mismo
        - SIEMPRE llama cedula_tool primero
        - Proporciona SOLO el número de cédula limpio (sin puntos ni comas)
        - Si la herramienta no encuentra una cédula clara, reporta "Cédula no encontrada"
        """
    ),
    name="cedula_agent",
)

registraduria_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[consulta_cedula_playwright],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
        """Eres un especialista en consultas oficiales de estado vital en la Registraduría Nacional del Estado Civil de Colombia.

        🎯 **OBJETIVO PRINCIPAL:**
        Verificar el estado vital oficial de una persona (vivo/fallecido) utilizando su número de cédula a través de la plataforma oficial de la Registraduría.

        📋 **INSTRUCCIONES ESPECÍFICAS:**
        
        1. **SIEMPRE usa la herramienta consulta_cedula_playwright** - Esta herramienta consulta directamente la página oficial
        
        2. **Busca el número de cédula en el historial de conversación** si no se proporciona directamente
        
        3. **NO inventes ni asumas estados vitales** - Solo usa datos oficiales obtenidos por la herramienta
        
        4. **Interpreta correctamente los estados posibles:**
           - "Vigente (Vivo)" = Persona viva
           - "Fallecido" = Persona fallecida
           - "Cancelada por Muerte" = Persona fallecida
           - "No encontrado" = Cédula no registrada en el sistema
        
        5. **Formato de respuesta esperado:**
           - Estado claro: "VIGENTE (VIVO)" o "FALLECIDO"
           - Fecha de consulta si está disponible
           - Fuente: "Registraduría Nacional del Estado Civil"
        
        6. **Si hay problemas técnicos:**
           - Reporta el error específico
           - Indica que la consulta no pudo completarse
           - NO inventes un estado
        
        ⚠️ **IMPORTANTE:**
        - Esta es información oficial y legal
        - La precisión es crítica para procesos de seguros y pólizas
        - NUNCA proporciones estados vitales sin confirmación oficial
        - Si hay dudas, reporta "Estado no determinado" con la razón específica
        """
    ),
    name="registraduria_agent",
)

defuncion_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[fecha_defuncion_tool],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
        """Eres un especialista en análisis de documentos oficiales para extraer fechas de defunción de actas de defunción.

        🎯 **OBJETIVO PRINCIPAL:**
        Extraer la fecha exacta de defunción de un acta de defunción utilizando la herramienta fecha_defuncion_tool.

        📋 **INSTRUCCIONES ESPECÍFICAS:**
        
        1. **SIEMPRE usa la herramienta fecha_defuncion_tool** - NO intentes extraer la fecha manualmente
        
        2. **NO inventes ni estimes fechas** - Solo proporciona información extraída por la herramienta
        
        3. **Formato de respuesta esperado:**
           - Fecha exacta si se encuentra (ej: "15 de marzo de 2023", "15/03/2023")
           - "Fecha no encontrada" si no hay información temporal clara
        
        ⚠️ **IMPORTANTE:**
        - NO analices el documento tú mismo
        - SIEMPRE llama fecha_defuncion_tool primero
        - Confía en los resultados de la herramienta
        - Si hay ambigüedad, reporta lo que la herramienta encontró exactamente
        """
    ),
    name="defuncion_agent",
)

saldo_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[saldo_tool],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
    """
    Tu objetivo es determinar si una persona aplica o no a **Póliza Express** con base en los datos obtenidos mediante la herramienta `saldo_tool`.  

    ### Paso 1: Obtener número de cédula
    **ANTES de llamar saldo_tool**, debes buscar en el historial de conversación el número de cédula que fue extraído previamente por el cedula_agent. 
    - Busca en los mensajes anteriores respuestas que contengan números de cédula (generalmente números de 8-10 dígitos).
    - Una vez que identifiques el número de cédula, úsalo como parámetro para llamar `saldo_tool`.

    ### Paso 2: Llamar herramienta
    Debes consumir `saldo_tool(cedula="NUMERO_DE_CEDULA")` para obtener los siguientes datos:
    - Tipo de producto (ej. TARJETA DE CRÉDITO, CRÉDITO, Móvil Consumo Fijo, Móvil Consumo Libranza)
    - Saldo de la persona
    - Fecha de desembolso (formato YYYY-MM-DD)
    - Monto desembolsado

    ### Reglas duras a evaluar:

    **Regla 1:**  
    ✔ Aplica si el tipo de producto es **TARJETA DE CRÉDITO**  
    ✔ Y el **saldo es menor o igual a 200.000.000**

    **Regla 2:**  
    ✔ Aplica si el tipo de producto es **CRÉDITO**  
    ✔ Y el plan es uno de los siguientes:  
    - Móvil Consumo Fijo  
    - Móvil Consumo Libranza  
    - Móvil Vehículo Particular  
    ✔ Y la diferencia entre la **fecha de siniestro y la fecha de desembolso es mayor a 60 días**  
    ✔ Y el **monto desembolsado es menor a 50.000.000**

    **Regla 3:**  
    ✔ Aplica si el producto **no es TARJETA DE CRÉDITO ni uno de los planes válidos para crédito**  
    ✔ Y la diferencia entre la **fecha de siniestro y la fecha de desembolso es mayor a 730 días (2 años)**  
    ✔ Y el **saldo es menor a 50.000.000**

    **En todos los casos se debe cumplir adicionalmente lo siguiente:**
    - La **fecha de siniestro debe estar dentro de la vigencia del crédito** (inicio ≤ siniestro ≤ fin)
    - el estado de la persona en la registraduría debe ser fallecido.

    ### Instrucciones:
    1. Revisa el historial de mensajes para encontrar el número de cédula extraído previamente.
    2. Llama la herramienta `saldo_tool` con el número de cédula como parámetro.
    3. Evalúa si se cumple alguna de las reglas anteriores **junto con los dos requisitos obligatorios comunes**.
    4. Si **sí aplica**, genera una respuesta afirmando que aplica a Póliza Express, especificando **qué regla se cumplió y por qué**.
    5. Si **no aplica**, indica que no cumple con las condiciones para aplicar y menciona **cuál fue la razón más relevante del descarte**.

    ### Formato de salida:
    - Siempre responde en un solo bloque.
    - Empieza indicando si **Aplica a Póliza Express: Sí/No**
    - Luego justifica brevemente en lenguaje claro y profesional.
    """
    ),
    name="saldo_agent",
)

# Creación del supervisor

supervisor_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[transfer_to_cedula, transfer_to_registraduria, transfer_to_defuncion, transfer_to_saldo],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
        """Eres un supervisor que coordina tres agentes especializados. Tu tarea es siempre ejecutar, en este orden y sin excepciones, las siguientes acciones:

        1. Obtener el número de documento del usuario usando la herramienta `cedula_tool`.
        2. Verificar el estado de la persona en la registraduría usando `registraduria_agent`.
        3. Obtener la fecha de defunción usando `defuncion_agent`.
        4. Obtener el saldo de la persona usando `saldo_agent`.

        ⚠️ Instrucciones clave (obligatorias):
        - Siempre debes iniciar ejecutando la herramienta `cedula_tool`. No preguntes, no confirmes, no hagas razonamientos antes de usarla.
        - No pidas ninguna información adicional al usuario. Toda la información requerida se obtiene únicamente con las herramientas.
        - Está prohibido iniciar una conversación o solicitar datos al usuario en este paso. Usa directamente `cedula_tool`.

        🔁 Repite siempre este flujo, sin desviarte ni invertir el orden de ejecución.

        Tu rol no es dialogar ni decidir: es coordinar a los agentes y ejecutar cada paso secuencialmente.

        solamente en el paso final, debes responder con la siguiente información:
            - numero de documento
            - estado de la persona en la registraduría
            - fecha de defunción
            - confirmar si aplica a Póliza Express y su justificación. 
        """
    ),
    name="supervisor"
)