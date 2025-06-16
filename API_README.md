# 🚀 API del Asistente Virtual Póliza Express

Esta API proporciona endpoints para consultar la elegibilidad de personas para Póliza Express utilizando un sistema de agentes inteligentes basado en LangGraph y LangChain.

## 📋 Características

- **Procesamiento Automático**: Extrae información de documentos (cédulas, certificados de defunción)
- **Análisis Integral**: Consulta registraduría, saldos y fechas de defunción
- **Evaluación de Elegibilidad**: Determina automáticamente si una persona aplica a Póliza Express
- **API RESTful**: Endpoints bien documentados con FastAPI
- **Gestión de Sesiones**: Tracking de consultas y resultados

## 🛠️ Instalación

1. **Instalar dependencias**:
```bash
pip install -e .
```

2. **Configurar variables de entorno**:
Crea un archivo `.env` basado en el ejemplo:
```bash
# Configuración del servidor
HOST=0.0.0.0
PORT=8000
RELOAD=false
WORKERS=1
LOG_LEVEL=info

# Tu configuración existente
PROJECT_ID=tu-project-id-gcp
```

3. **Verificar archivos necesarios**:
- Credenciales de GCP: `src/creds/credentials.json`
- Documentos de prueba en: `src/doc_pruebas/`
  - `Cedula_seb.pdf`
  - `CER_DEFUNCION.pdf`
  - `data_saldos.csv`

## 🚀 Ejecución

### Método 1: Script de arranque
```bash
python run_api.py
```

### Método 2: Directamente con uvicorn
```bash
uvicorn src.react_agent.api:app --host 0.0.0.0 --port 8000
```

### Método 3: Con recarga automática (desarrollo)
```bash
uvicorn src.react_agent.api:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 Documentación de la API

Una vez ejecutando el servidor, puedes acceder a:

- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc
- **Estado de salud**: http://localhost:8000/health

## 🔗 Endpoints Principales

### 1. Consulta General
```http
POST /consulta
Content-Type: application/json

{
    "mensaje": "Necesito consultar si una persona aplica para Póliza Express",
    "session_id": "opcional-session-id"
}
```

### 2. Consulta Específica Póliza Express
```http
POST /consulta-poliza-express
```
Este endpoint ejecuta automáticamente todo el flujo de análisis.

### 3. Gestión de Sesiones
```http
# Obtener sesión específica
GET /sesion/{session_id}

# Listar todas las sesiones
GET /sesiones

# Eliminar sesión
DELETE /sesion/{session_id}
```

## 📊 Ejemplos de Uso

### Ejemplo con curl

```bash
# Consulta básica
curl -X POST "http://localhost:8000/consulta" \
     -H "Content-Type: application/json" \
     -d '{"mensaje": "Consultar elegibilidad Póliza Express"}'

# Consulta automática
curl -X POST "http://localhost:8000/consulta-poliza-express"

# Verificar estado
curl "http://localhost:8000/health"
```

### Ejemplo con Python

```python
import requests

# Consulta básica
response = requests.post(
    "http://localhost:8000/consulta",
    json={"mensaje": "Consultar elegibilidad para Póliza Express"}
)

result = response.json()
print(f"Respuesta: {result['respuesta']}")
print(f"Sesión: {result['session_id']}")
```

### Ejemplo con JavaScript

```javascript
// Consulta automática
fetch('http://localhost:8000/consulta-poliza-express', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    }
})
.then(response => response.json())
.then(data => {
    console.log('Resultado:', data.respuesta);
    console.log('Sesión:', data.session_id);
});
```

## 🔄 Flujo de Procesamiento

El asistente ejecuta automáticamente estos pasos:

1. **Extracción de Cédula**: Lee el documento PDF y extrae el número de identificación
2. **Consulta Registraduría**: Verifica el estado de la persona (fallecido/vivo)
3. **Fecha de Defunción**: Extrae la fecha del certificado de defunción
4. **Análisis de Saldo**: Consulta productos financieros y saldos
5. **Evaluación**: Determina elegibilidad según reglas de negocio

## ⚙️ Reglas de Elegibilidad

### Regla 1: Tarjeta de Crédito
- ✅ Producto: TARJETA DE CRÉDITO
- ✅ Saldo ≤ 200.000.000

### Regla 2: Créditos Específicos
- ✅ Producto: CRÉDITO
- ✅ Plan: Móvil Consumo Fijo/Libranza/Vehículo Particular
- ✅ Diferencia fecha siniestro - desembolso > 60 días
- ✅ Monto desembolsado < 50.000.000

### Regla 3: Otros Productos
- ✅ Producto: No TARJETA DE CRÉDITO ni planes específicos
- ✅ Diferencia fecha siniestro - desembolso > 730 días (2 años)
- ✅ Saldo < 50.000.000

**Requisito común**: La fecha de siniestro debe estar dentro de la vigencia del crédito.

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `HOST` | IP del servidor | `0.0.0.0` |
| `PORT` | Puerto del servidor | `8000` |
| `RELOAD` | Recarga automática | `false` |
| `WORKERS` | Número de workers | `1` |
| `LOG_LEVEL` | Nivel de logging | `info` |

### Logging

Los logs incluyen:
- Información de procesamiento de consultas
- Errores y excepciones
- Métricas de sesiones
- Estado de archivos y credenciales

## 🐛 Resolución de Problemas

### Error: Credenciales no encontradas
```
Archivo de credenciales no encontrado en: /path/to/credentials.json
```
**Solución**: Verifica que el archivo `credentials.json` esté en `src/creds/`

### Error: Documentos no encontrados
```
Directorio de documentos de prueba no encontrado: /path/to/docs
```
**Solución**: Asegúrate de que los PDFs estén en `src/doc_pruebas/`

### Error: Dependencias
```
Error de importación: No module named 'fastapi'
```
**Solución**: Instala las dependencias con `pip install -e .`

## 📈 Monitoreo

La API proporciona métricas básicas a través de:
- Logs estructurados
- Endpoints de salud
- Tracking de sesiones
- Tiempo de respuesta en logs

## 🔒 Consideraciones de Seguridad

- Las credenciales están en archivos locales (no recomendado para producción)
- El almacenamiento de sesiones es en memoria (usar Redis/DB para producción)
- No hay autenticación implementada (agregar según necesidades)

## 🚦 Estados de Respuesta

| Código | Descripción |
|--------|-------------|
| 200 | Consulta procesada correctamente |
| 404 | Sesión no encontrada |
| 500 | Error interno del servidor |

## 📝 Estructura de Respuesta

```json
{
    "respuesta": "Resultado del análisis...",
    "session_id": "uuid-de-la-sesion",
    "timestamp": "2024-01-15T10:30:00",
    "estado": "completado",
    "detalles": {
        "numero_mensajes": 8,
        "tipo_consulta": "poliza_express_automatica"
    }
}
```

---

¡Tu API está lista para procesar consultas de Póliza Express de manera automática e inteligente! 🎉 