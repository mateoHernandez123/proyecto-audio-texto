# Proyecto de Transcripción de Audio con Faster-Whisper

Este proyecto implementa un sistema automático de transcripción de voz a texto utilizando `faster-whisper` y n8n. El servicio está diseñado para ser altamente preciso y fácil de integrar con otros sistemas.

## Módulos del Sistema

### 1. Módulo de Grabación de Audio en Vivo
Este módulo permite grabar audio directamente desde el micrófono y enviarlo automáticamente al servicio de transcripción.

#### Requisitos Previos
- Python 3.9 o superior
- FFmpeg instalado en el sistema
- Un micrófono funcional

#### Instalación de FFmpeg en Windows
1. Descarga FFmpeg desde https://www.gyan.dev/ffmpeg/builds/
2. Extrae el archivo descargado
3. Copia la carpeta `bin` a `C:\ffmpeg\`
4. Añade `C:\ffmpeg\bin` al PATH del sistema:
   - Abre "Variables de entorno del sistema" (busca en el menú inicio)
   - En "Variables del sistema", selecciona "Path"
   - Click en "Editar" y añade una nueva entrada con `C:\ffmpeg\bin`
   - Acepta todos los cambios

#### Instalación de Dependencias Python
```bash
pip install sounddevice numpy pydub requests
```

#### Uso del Módulo de Grabación
1. Ejecuta el script de grabación:
```bash
python record_audio.py
```
2. El script:
   - Mostrará los dispositivos de audio disponibles
   - Esperará a que presiones Enter para comenzar la grabación
   - Grabará durante 5 segundos
   - Convertirá automáticamente el audio a MP3
   - Enviará el archivo al webhook para su transcripción

### 2. Módulo de Carga de Archivos
Este módulo permite cargar archivos de audio existentes para su transcripción.

Para usar la interfaz web de carga de archivos:
1. Abre el archivo `Audio To Text.html` en tu navegador
2. Selecciona un archivo de audio
3. Haz clic en "Enviar para Transcribir"

## Diagrama del Sistema

![Diagrama del Sistema de Transcripción](diagrama.png)

Este diagrama muestra el flujo completo del sistema:

1. El cliente puede:
   - Grabar audio en vivo usando el módulo de grabación
   - Subir un archivo de audio existente usando la interfaz web
2. El audio es procesado y enviado al servicio de transcripción mediante HTTP Request
3. El servicio, ejecutándose en un contenedor Docker, procesa el audio usando Faster-Whisper
4. El modelo ML genera el texto
5. La respuesta JSON es devuelta al cliente a través de n8n

[El resto del README.md continúa igual...]