from enum import Enum


class Messages(str, Enum):
    # Excepciones genéricas
    EXCEPTION_BAD_REQUEST = (
        "La solicitud no se puede completar debido a errores de validación."
    )
    EXCEPTION_UNAUTHORIZED = "Usuario no autorizado."
    EXCEPTION_FORBIDDEN = (
        "No tienes permiso para realizar la acción sobre el recurso solicitado."
    )
    EXCEPTION_NOT_FOUND = "Recurso no encontrado."
    EXCEPTION_PRECONDITION_FAILED = "La solicitud no cumple con una condición previa."
    EXCEPTION_DEFAULT = "Ocurrió un error desconocido."

    THROTTLER_EXCEPTION = "Límite de solicitudes superado. Intente más tarde por favor."

    # Mensajes de éxito
    SUCCESS_OPERATION = "Operación completada exitosamente."
    SUCCESS_CREATED = "Recurso creado exitosamente."
    SUCCESS_UPDATED = "Recurso actualizado exitosamente."
    SUCCESS_DELETED = "Recurso eliminado exitosamente."
    SUCCESS_RETRIEVED = "Recurso obtenido exitosamente."

    # Mensajes de imágenes
    IMAGE_UPLOAD_SUCCESS = "Imagen subida correctamente."
    IMAGE_UPLOAD_ERROR = "Error al guardar la imagen."
    IMAGE_UPLOAD_BATCH_SUCCESS = "Procesamiento de lote completado."
    IMAGE_NOT_FOUND = "Imagen no encontrada."
    IMAGE_INVALID_FORMAT = "Tipo de archivo no permitido."
    IMAGE_TOO_LARGE = "Archivo demasiado grande."
    IMAGE_INVALID_NAME = "Nombre de archivo inválido."

    # Mensajes de validación
    VALIDATION_REQUIRED_FIELD = "Este campo es requerido."
    VALIDATION_INVALID_EMAIL = "El formato del email es inválido."
    VALIDATION_INVALID_UUID = "El formato del UUID es inválido."
    VALIDATION_FILE_REQUIRED = "Se requiere un archivo."

    @classmethod
    def get_message(cls, key: str, default: str = None) -> str:
        """Obtener mensaje por clave con valor por defecto"""
        return (
            getattr(cls, key, default)
            if default
            else getattr(cls, key, cls.EXCEPTION_DEFAULT)
        )
