import tkinter as tk
from tkinter import messagebox, scrolledtext
import pywhatkit as kit
from datetime import datetime, timedelta
import threading
import time

# Variables globales para la cuenta regresiva y control de cancelación
cancelar_envio = False
ventana_cuenta_regresiva = None

# Función para calcular el tiempo restante
def calcular_tiempo_restante(hora, minuto):
    ahora = datetime.now()
    envio = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)

    # Si la hora de envío ya pasó hoy, se ajusta al día siguiente
    if envio < ahora:
        envio += timedelta(days=1)
    
    tiempo_restante = envio - ahora
    return envio, tiempo_restante

# Función para mostrar la ventana emergente con la cuenta regresiva
def mostrar_cuenta_regresiva(hora, minuto):
    global ventana_cuenta_regresiva, cancelar_envio
    
    # Crear la ventana emergente
    ventana_cuenta_regresiva = tk.Toplevel(ventana)
    ventana_cuenta_regresiva.title("Cuenta Regresiva")
    ventana_cuenta_regresiva.geometry("300x200")

    # Etiqueta de la cuenta regresiva
    label_tiempo_restante = tk.Label(ventana_cuenta_regresiva, text="", font=("Arial", 12))
    label_tiempo_restante.pack(pady=20)

    # Botón para cancelar el envío
    boton_cancelar = tk.Button(
        ventana_cuenta_regresiva, text="Cancelar Envío", 
        command=cancelar_envio_mensaje, bg="#f44336", 
        fg="white", font=("Arial", 12, "bold")
    )
    boton_cancelar.pack(pady=20)

    # Iniciar la actualización de la cuenta regresiva en un hilo separado
    threading.Thread(target=actualizar_cuenta_regresiva, args=(label_tiempo_restante, hora, minuto)).start()

# Función para actualizar la cuenta regresiva
def actualizar_cuenta_regresiva(label, hora, minuto):
    global cancelar_envio
    envio, tiempo_restante = calcular_tiempo_restante(hora, minuto)

    # Loop de actualización de la cuenta regresiva
    while tiempo_restante.total_seconds() > 0 and not cancelar_envio:
        dias_restantes = tiempo_restante.days
        horas_restantes, resto = divmod(tiempo_restante.seconds, 3600)
        minutos_restantes = resto // 60
        segundos_restantes = resto % 60

        # Actualiza la etiqueta de la cuenta regresiva
        cuenta = f"Faltan {dias_restantes} días, {horas_restantes} horas, {minutos_restantes} minutos, y {segundos_restantes} segundos."
        label.config(text=cuenta)

        # Actualiza cada segundo
        ventana_cuenta_regresiva.update()
        time.sleep(1)
        tiempo_restante = calcular_tiempo_restante(hora, minuto)[1]

    # Acciones al finalizar la cuenta regresiva
    if not cancelar_envio:
        enviar_mensaje_confirmado()
    else:
        label.config(text="Envío cancelado.")

# Función para enviar el mensaje después de la cuenta regresiva
def enviar_mensaje_confirmado():
    global ventana_cuenta_regresiva
    try:
        numero_telefono = entry_numero.get().strip()
        mensaje = entry_mensaje.get("1.0", tk.END).strip()
        hora_envio = int(entry_hora.get())
        minuto_envio = int(entry_minuto.get())

        # Enviar mensaje usando pywhatkit
        kit.sendwhatmsg(numero_telefono, mensaje, hora_envio, minuto_envio, wait_time=20)
        messagebox.showinfo("Éxito", f"Mensaje programado para las {hora_envio}:{minuto_envio} horas.")
        # Guardar en el historial
        guardar_en_historial(numero_telefono, mensaje)
        cargar_historial()  # Actualizar el área de historial
    except Exception as e:
        messagebox.showerror("Error", f"Algo salió mal: {str(e)}")
    finally:
        # Cerrar la ventana emergente después de enviar o si hay un error
        if ventana_cuenta_regresiva is not None:
            ventana_cuenta_regresiva.destroy()

# Función para iniciar el envío con confirmación y mostrar la cuenta regresiva
def enviar_mensaje():
    global cancelar_envio
    cancelar_envio = False

    try:
        numero_telefono = entry_numero.get().strip()
        mensaje = entry_mensaje.get("1.0", tk.END).strip()
        hora_envio = int(entry_hora.get())
        minuto_envio = int(entry_minuto.get())

        # Validación básica de los campos
        if not numero_telefono or not mensaje:
            messagebox.showwarning("Advertencia", "Por favor, llena todos los campos.")
            return

        # Calcula la fecha y tiempo restante para confirmar
        fecha_envio, tiempo_restante = calcular_tiempo_restante(hora_envio, minuto_envio)

        # Confirmar envío con la fecha y tiempo restante
        confirmacion = messagebox.askyesno(
            "Confirmar Envío",
            f"El mensaje se enviará el {fecha_envio.strftime('%d/%m/%Y a las %H:%M')}.\n"
            f"¿Deseas proceder?"
        )

        if confirmacion:
            # Mostrar la ventana de cuenta regresiva
            mostrar_cuenta_regresiva(hora_envio, minuto_envio)
        else:
            messagebox.showinfo("Cancelado", "El envío del mensaje ha sido cancelado.")
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce números válidos para la hora y los minutos.")
    except Exception as e:
        messagebox.showerror("Error", f"Algo salió mal: {str(e)}")

# Función para cancelar el envío
def cancelar_envio_mensaje():
    global cancelar_envio
    cancelar_envio = True
    if ventana_cuenta_regresiva is not None:
        ventana_cuenta_regresiva.destroy()

# Función para guardar en el historial
def guardar_en_historial(numero, mensaje):
    with open("historial.txt", "a") as file:
        file.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        file.write(f"Teléfono: {numero}\n")
        file.write(f"Mensaje: {mensaje}\n")
        file.write("-" * 40 + "\n")

# Función para cargar el historial desde el archivo
def cargar_historial():
    try:
        with open("historial.txt", "r") as file:
            historial = file.read()
            area_historial.config(state=tk.NORMAL)
            area_historial.delete(1.0, tk.END)
            area_historial.insert(tk.END, historial)
            area_historial.config(state=tk.DISABLED)  # Desactivar edición
    except FileNotFoundError:
        area_historial.config(state=tk.NORMAL)
        area_historial.delete(1.0, tk.END)
        area_historial.insert(tk.END, "No hay historial disponible.")
        area_historial.config(state=tk.DISABLED)

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Programador de Mensajes de WhatsApp")
ventana.geometry("500x600")

# Etiquetas y entradas de texto
tk.Label(ventana, text="Número de Teléfono (ej. +1234567890):").pack(pady=5)
entry_numero = tk.Entry(ventana, width=30)
entry_numero.pack()

tk.Label(ventana, text="Mensaje:").pack(pady=5)
entry_mensaje = tk.Text(ventana, height=5, width=40)
entry_mensaje.pack()

tk.Label(ventana, text="Hora de Envío (24 horas):").pack(pady=5)
entry_hora = tk.Entry(ventana, width=5)
entry_hora.pack()

tk.Label(ventana, text="Minuto de Envío:").pack(pady=5)
entry_minuto = tk.Entry(ventana, width=5)
entry_minuto.pack()

# Botón para enviar el mensaje
boton_enviar = tk.Button(
    ventana, text="Enviar Mensaje", command=enviar_mensaje, 
    bg="#4CAF50", fg="white", font=("Arial", 12, "bold")
)
boton_enviar.pack(pady=20)

# Área de historial
tk.Label(ventana, text="Historial de Mensajes:").pack(pady=5)
area_historial = scrolledtext.ScrolledText(ventana, width=50, height=10, state=tk.DISABLED)
area_historial.pack(pady=5)

# Botón para cargar el historial
boton_cargar_historial = tk.Button(
    ventana, text="Cargar Historial", command=cargar_historial, 
    bg="#2196F3", fg="white", font=("Arial", 12, "bold")
)
boton_cargar_historial.pack(pady=10)

# Iniciar el bucle de la interfaz gráfica
ventana.mainloop()
