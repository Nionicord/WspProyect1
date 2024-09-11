import pywhatkit as kit

# Solicitar al usuario el número de teléfono, mensaje, hora y minuto
numero_telefono = input("Introduce el número de teléfono en formato internacional (ej. +1234567890): ")
mensaje = input("Escribe el mensaje que quieres enviar: ")

# Solicitar la hora y el minuto de envío
try:
    hora_envio = int(input("Introduce la hora de envío (formato 24 horas, ej. 14 para 2 PM): "))
    minuto_envio = int(input("Introduce el minuto de envío (ej. 30): "))

    # Enviar el mensaje de WhatsApp en la hora especificada
    kit.sendwhatmsg(numero_telefono, mensaje, hora_envio, minuto_envio)
    print(f"Mensaje programado para las {hora_envio}:{minuto_envio} horas.")
except ValueError:
    print("Por favor, introduce números válidos para la hora y los minutos.")
