# diagnosticar_modelo.py
from app.models.predictor_text import run_model_prediction_text
import cv2
import numpy as np
from PIL import Image


def diagnosticar_imagen(imagen_path):
    print(f"🔍 Diagnosticando: {imagen_path}")

    # Probar con diferentes umbrales
    umbrales = [0.15, 0.1, 0.05, 0.01, 0.001]

    for conf in umbrales:
        results = run_model_prediction_text(
            imagen_path, conf_threshold=conf, iou_threshold=0.15
        )

        num_detecciones = len(results[0].boxes) if results[0].boxes else 0
        print(f"   Umbral {conf}: {num_detecciones} detecciones")

        if num_detecciones > 0:
            # Mostrar detalles de las detecciones
            for i, box in enumerate(results[0].boxes):
                cls_idx = int(box.cls.cpu().numpy())
                conf_val = float(box.conf.cpu())
                print(f"      - Detección {i+1}: Clase={cls_idx}, Conf={conf_val:.4f}")


# Probar con imágenes de entrenamiento
print("📝 PROBANDO CON IMÁGENES DE ENTRENAMIENTO:")
diagnosticar_imagen("/var/home/troy/Downloads/imagen_00411.jpg")
diagnosticar_imagen("/var/home/troy/Downloads/imagen_00408.jpg")

# Probar con imagen nueva (si tienes)
print("\n📝 PROBANDO CON IMAGEN NUEVA:")
# diagnosticar_imagen("imagen_nueva.jpg")
