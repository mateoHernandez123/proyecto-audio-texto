from fastapi import FastAPI, UploadFile, File, Request
from faster_whisper import WhisperModel
import logging
import uvicorn
from fastapi.responses import JSONResponse

# Configuración del logging
logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

app = FastAPI()

# Cargar el modelo al iniciar la aplicación
model_size = "large-v3"
# Opciones: "cuda", "cpu"
device_type = "cpu"
# Opciones para CPU: "int8"
# Opciones para GPU: "float16", "int8_float16"
compute_type_device = "int8"

model = WhisperModel(model_size, device=device_type, compute_type=compute_type_device)

@app.post("/transcribe")
async def transcribe_audio(request: Request):
    """
    Endpoint para transcribir un archivo de audio.
    Acepta tanto form-data como datos binarios directos.
    """
    try:
        content_type = request.headers.get("content-type", "")
        logging.info(f"Content-Type recibido: {content_type}")

        if "multipart/form-data" in content_type:
            form = await request.form()
            if "audio_file" not in form:
                return JSONResponse(
                    status_code=400,
                    content={"error": "No se encontró el campo 'audio_file' en el form-data"}
                )
            file = form["audio_file"]
            content = await file.read()
        else:
            # Si no es multipart/form-data, intentamos leer el cuerpo directamente
            content = await request.body()
            logging.info(f"Recibidos {len(content)} bytes de datos binarios directos")

    except Exception as e:
        logging.error(f"Error procesando la solicitud: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": f"Error procesando la solicitud: {str(e)}"}
        )

    # Guardar el audio en un archivo temporal
    temp_audio_path = "temp_audio_file"
    with open(temp_audio_path, "wb") as temp_audio:
        temp_audio.write(content)

    try:
        segments, info = model.transcribe(temp_audio_path, beam_size=5)

        logging.info("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
            logging.info("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        
        return {"transcription": transcription.strip()}
    finally:
        # Limpiar el archivo temporal
        import os
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
