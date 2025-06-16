# 🛡️ Asistente Virtual Póliza Express - Documentación Completa

## 📋 Descripción

El **Asistente Virtual Póliza Express** es una aplicación integral que combina una **API REST** con una **interfaz web Streamlit** para automatizar el análisis de elegibilidad de Póliza Express mediante procesamiento inteligente de documentos.

### 🎯 Funcionalidades Principales

- **Extracción automática de datos** de cédulas de ciudadanía (OCR con IA)
- **Análisis de certificados de defunción** con extracción de fechas
- **Consulta automática** en registraduría nacional
- **Evaluación de productos financieros** y saldos
- **Determinación inteligente** de elegibilidad para Póliza Express
- **Interfaz web intuitiva** para carga de documentos
- **API REST completa** para integración con otros sistemas

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │───▶│   FastAPI       │───▶│   LangGraph     │
│   Frontend      │    │   Backend       │    │   Agents        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   Google        │
         │                       │              │   Gemini Vision │
         │                       │              └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │   File Manager  │
         │              │   (Temp Files)  │
         └──────────────┴─────────────────┘
```

### 🤖 Agentes Especializados

1. **Supervisor Agent**: Coordina el flujo completo del proceso
2. **Cedula Agent**: Extrae números de documento usando OCR
3. **Registraduria Agent**: Consulta estado civil y vital
4. **Defuncion Agent**: Extrae fechas de certificados de defunción
5. **Saldo Agent**: Evalúa productos financieros y elegibilidad

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- Credenciales de Google Cloud Platform (Vertex AI)
- Credenciales de Azure OpenAI

### 1. Instalación de Dependencias

```bash
# Clonar repositorio
git clone <repository-url>
cd react-agent

# Crear ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -e .
```

### 2. Configuración de Credenciales

#### Google Cloud (Vertex AI)
```bash
# Colocar archivo de credenciales en:
src/creds/credentials.json
```

#### Variables de Entorno
```bash
# Crear archivo .env
PROJECT_ID=tu-proyecto-gcp
```

### 3. Verificar Estructura de Archivos

```
react-agent/
├── src/
│   ├── react_agent/
│   │   ├── api.py           # API FastAPI
│   │   ├── graph.py         # Configuración del grafo
│   │   ├── nodes.py         # Definición de agentes
│   │   ├── tools.py         # Herramientas especializadas
│   │   ├── state.py         # Estados del sistema
│   │   ├── file_manager.py  # Gestión de archivos
│   │   └── server.py        # Configuración del servidor
│   ├── doc_pruebas/         # Documentos de prueba
│   └── creds/               # Credenciales
├── streamlit_app.py         # Interfaz web
├── run_api.py              # Ejecutor de API
├── run_streamlit.py        # Ejecutor de Streamlit
└── seguros_bolivar.png     # Logo (agregar aquí)
```

---

## 🖥️ Uso del Sistema

### Opción 1: Interfaz Web Streamlit (Recomendado)

#### 1. Iniciar los Servicios

```bash
# Terminal 1: Iniciar API
source venv/bin/activate
python run_api.py

# Terminal 2: Iniciar Streamlit
source venv/bin/activate
python run_streamlit.py
```

#### 2. Usar la Interfaz Web

1. **Abrir navegador**: http://localhost:8501
2. **Cargar documentos**:
   - Subir archivo PDF de cédula de ciudadanía
   - Subir archivo PDF de certificado de defunción
3. **Procesar análisis**: Hacer clic en "Procesar Análisis de Póliza Express"
4. **Revisar resultados**: Ver análisis completo y determinación de elegibilidad

#### 3. Funcionalidades de la Interfaz

- **Validación de archivos**: Solo acepta PDFs válidos
- **Feedback en tiempo real**: Indicadores de progreso y estado
- **Gestión de sesiones**: Cada carga genera un ID único
- **Resultados detallados**: Información completa del análisis
- **Enlaces útiles**: Acceso directo a documentación de API

### Opción 2: API REST Directa

#### Endpoints Principales

##### 1. Verificar Estado de la API
```bash
curl http://localhost:8000/health
```

##### 2. Cargar Documentos
```bash
curl -X POST "http://localhost:8000/upload-documentos" \
  -F "cedula=@cedula.pdf" \
  -F "defuncion=@certificado_defuncion.pdf"
```

**Respuesta:**
```json
{
  "mensaje": "Documentos cargados exitosamente",
  "session_id": "uuid-generado",
  "archivos_cargados": {
    "cedula": "cedula.pdf",
    "defuncion": "certificado_defuncion.pdf"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

##### 3. Procesar Consulta con Documentos
```bash
curl -X POST "http://localhost:8000/consulta-con-archivos" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-del-paso-anterior",
    "mensaje": "Consultar elegibilidad para Póliza Express"
  }'
```

**Respuesta:**
```json
{
  "respuesta": "Análisis completo con determinación de elegibilidad",
  "session_id": "uuid-sesion",
  "timestamp": "2024-01-15T10:35:00",
  "estado": "completado",
  "detalles": {
    "tipo_consulta": "con_archivos_cargados",
    "numero_mensajes": 15,
    "archivos_utilizados": ["cedula", "defuncion"]
  }
}
```

##### 4. Otros Endpoints Útiles

```bash
# Listar todas las sesiones
curl http://localhost:8000/sesiones

# Obtener detalles de una sesión
curl http://localhost:8000/sesion/{session_id}

# Eliminar una sesión
curl -X DELETE http://localhost:8000/sesion/{session_id}

# Documentación interactiva
# Abrir: http://localhost:8000/docs
```

---

## 🔧 Configuración Avanzada

### Personalización de Prompts

Los prompts de los agentes se pueden modificar en `src/react_agent/nodes.py`:

```python
# Ejemplo: Modificar comportamiento del agente de cédula
cedula_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[cedula_tool],
    prompt="Tu prompt personalizado aquí...",
    name="cedula_agent",
)
```

### Configuración de Modelos

- **Modelos de OpenAI**: Configurados en nodes.py
- **Google Gemini Vision**: Configurado en tools.py para OCR
- **Parámetros de LangGraph**: Configurables en graph.py

### Gestión de Archivos Temporales

Los archivos se almacenan temporalmente en `/tmp/react_agent_uploads/` y se limpian automáticamente.

### Logging y Monitoreo

- **Logs de API**: Configurados en `src/react_agent/server.py`
- **Logs de Streamlit**: Visibles en consola
- **Métricas**: Disponibles en endpoints de estado

---

## 🧪 Desarrollo y Testing

### Estructura para Testing

```bash
# Crear archivos de prueba
mkdir tests/
touch tests/test_api.py
touch tests/test_agents.py
touch tests/test_tools.py
```

### Debugging

```bash
# Ejecutar con logs detallados
DEBUG=1 python run_api.py

# Verificar conexiones
curl http://localhost:8000/health
curl http://localhost:8501/health  # Si está disponible
```

### Desarrollo de Nuevos Agentes

1. **Definir herramientas** en `tools.py`
2. **Crear agente** en `nodes.py`
3. **Actualizar grafo** en `graph.py`
4. **Probar endpoints** en `api.py`

---

## 📊 Casos de Uso

### 1. Evaluación Automática de Elegibilidad
- **Input**: Cédula + Certificado de defunción
- **Proceso**: Extracción → Validación → Consultas → Análisis
- **Output**: Determinación de elegibilidad con justificación

### 2. Integración con Sistemas Existentes
- **Uso de API REST**: Para integrar con sistemas de seguros
- **Webhooks**: Para notificaciones automáticas
- **Batch processing**: Para procesar múltiples casos

### 3. Validación de Documentos
- **OCR avanzado**: Extracción precisa de datos
- **Validación cruzada**: Verificación entre múltiples fuentes
- **Detección de inconsistencias**: Alertas automáticas

---

## 🛠️ Troubleshooting

### Problemas Comunes

#### 1. Error de Credenciales
```bash
# Verificar archivo de credenciales
ls -la src/creds/credentials.json

# Verificar variables de entorno
echo $PROJECT_ID
```

#### 2. API No Disponible
```bash
# Verificar puerto
lsof -i :8000

# Reiniciar API
pkill -f "python run_api.py"
python run_api.py
```

#### 3. Problemas con PDFs
- **Verificar formato**: Solo PDFs válidos
- **Tamaño máximo**: Límite de 10MB por archivo
- **Contenido**: Documentos deben ser legibles

#### 4. Problemas de Memoria
```bash
# Limpiar archivos temporales
rm -rf /tmp/react_agent_uploads/*

# Reiniciar servicios
pkill -f "streamlit\|uvicorn"
```

### Logs de Debug

```bash
# Ver logs en tiempo real
tail -f /var/log/react-agent.log  # Si está configurado

# Logs de API
# Revisar salida de run_api.py

# Logs de Streamlit
# Revisar salida de run_streamlit.py
```

---

## 🤝 Contribución

### Guías de Contribución

1. **Fork del repositorio**
2. **Crear rama de feature**: `git checkout -b feature/nueva-funcionalidad`
3. **Commits descriptivos**: Seguir convenciones de commit
4. **Tests**: Agregar tests para nueva funcionalidad
5. **Pull Request**: Describir cambios detalladamente

### Estándares de Código

- **PEP 8**: Para código Python
- **Type hints**: Usar anotaciones de tipo
- **Docstrings**: Documentar funciones y clases
- **Tests**: Cobertura mínima del 80%

---

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo LICENSE.

---

## 🔗 Enlaces Útiles

- **Documentación de LangGraph**: https://langchain-ai.github.io/langgraph/
- **Streamlit Docs**: https://docs.streamlit.io/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Google Vertex AI**: https://cloud.google.com/vertex-ai/docs

---

## 📞 Soporte

Para soporte técnico o consultas:

1. **Issues de GitHub**: Para reportar bugs
2. **Discussions**: Para preguntas generales
3. **Wiki**: Para documentación extendida

---

**Última actualización**: Enero 2024  
**Versión**: 1.0.0 