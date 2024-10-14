import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

# Cargar las variables de entorno desde .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configurar la API de Google
genai.configure(api_key=api_key)

# Archivo JSON que actúa como base de datos de usuarios
DATABASE_FILE = 'usuarios.json'

# Funciones para manejar el archivo JSON
def cargar_usuarios():
    with open(DATABASE_FILE, 'r') as file:
        return json.load(file)

def guardar_usuarios(usuarios):
    with open(DATABASE_FILE, 'w') as file:
        json.dump(usuarios, file, indent=4)

def agregar_transaccion(cedula, tipo, monto, destinatario=None):
    usuarios = cargar_usuarios()
    transaccion = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": tipo,
        "monto": monto,
    }
    if destinatario:
        transaccion["destinatario"] = destinatario

    usuarios[cedula]["transacciones"].append(transaccion)
    guardar_usuarios(usuarios)

# Crear el modelo generativo
model = genai.GenerativeModel(model_name="gemini-pro")

# Función para interactuar con Chip
def chat_chip(user_input, usuario):
    prompt = f"""
    Eres Chip, el asistente virtual del Banco Internacional. Tu objetivo es ayudar a {usuario['nombre']} con operaciones bancarias como consultar datos como el saldo disponible, contactos a los que pueda hacer una transferencia, abrir cuentas de ahorros, realizar transferencias, gestionar inversiones y solicitar tarjetas de crédito. 
    Responde de manera clara, profesional y amigable. Recuerda que también puedes responder preguntas generales como el saldo disponible. Aquí está la consulta del usuario:

    Usuario: {user_input}

    Chip:
    """
    response = model.generate_content(prompt)
    return response.text

# Función para autenticar al usuario
def autenticar_usuario():
    usuarios = cargar_usuarios()
    while True:
        cedula = input("Por favor, ingrese su número de cédula: ")
        if cedula in usuarios:
            clave = input("Por favor, ingrese su clave bancaria: ")
            if usuarios[cedula]["clave_bancaria"] == clave:
                print(f"Hola soy Chip 🐶, tu Asesor virtual de Banco Internacional. Bienvenido, {usuarios[cedula]['nombre']}!")
                return cedula
            else:
                print("Clave incorrecta. Intente nuevamente.")
        else:
            print("Número de cédula no encontrado. Intente nuevamente.")

# Bucle principal de interacción
def main():
    cedula = autenticar_usuario()
    usuarios = cargar_usuarios()
    usuario = usuarios[cedula]

    en_proceso_creacion = False

    while True:
        if not en_proceso_creacion:
            print("\nOpciones disponibles:")
            print("1. Abrir una cuenta de ahorros")
            print("2. Realizar una transferencia")
            print("3. Hacer una inversión")
            print("4. Solicitar una tarjeta de crédito")
            print("5. Servicios asistenciales")
            print("6. Salir")

        user_input = input("Por favor, seleccione una opción o escriba su consulta: ").strip().lower()

        if user_input == "1" or "abrir una cuenta de ahorros" in user_input:
            en_proceso_creacion = True
            print(f"Antes de continuar, confírmanos {usuario['nombre']} que tu información esté correcta.")
            print(f"Correo electrónico: {usuario['correo'][:3]}xxxxxxxx{usuario['correo'][-7:]}")
            print(f"Celular: {usuario['celular'][:3]}XXXXX{usuario['celular'][-2:]}")
            confirmacion = input("¿Tus datos son correctos? (sí/no): ").strip().lower()
            if confirmacion == "sí" or confirmacion == "si":
                print("📄 Ver contrato de cuenta de ahorros ➡️ (http://bit.ly/3HzN27w)")
                acepta = input("¿Aceptas los términos y condiciones del contrato? (sí/no): ").strip().lower()
                if acepta == "sí" or acepta == "si":
                    print("Chip: Tu cuenta de ahorros ha sido creada con éxito.")
                    agregar_transaccion(cedula, "apertura cuenta de ahorros", 0)
                else:
                    print("Chip: No se ha creado la cuenta de ahorros.")
            else:
                print("Chip: Por favor, actualiza tus datos antes de continuar.")
            en_proceso_creacion = False

        elif user_input == "2" or "transferencia" in user_input:
            receptor_cedula = input("Ingrese el número de cédula del receptor: ")
            if receptor_cedula in usuarios:
                monto = float(input("Ingrese el monto a transferir: "))
                if monto > usuario['saldo']:
                    print("Fondos insuficientes para realizar la transferencia.")
                else:
                    usuarios[cedula]['saldo'] -= monto
                    usuarios[receptor_cedula]['saldo'] += monto
                    agregar_transaccion(cedula, "transferencia", monto, receptor_cedula)
                    agregar_transaccion(receptor_cedula, "recepción", monto, cedula)
                    guardar_usuarios(usuarios)
                    print(f"Transferencia realizada con éxito. Su nuevo saldo es: {usuarios[cedula]['saldo']:.2f}")
            else:
                print("El número de cédula del receptor no fue encontrado.")

        elif user_input == "3" or "inversión" in user_input or "invertir" in user_input:
            print("¡Claro, con gusto te ayudaré! Vamos a simular tu inversión paso a paso. Para empezar, debes ingresar el monto exacto de tu inversión, asegurándote de que no uses puntos ni comas en los valores que ingreses. Recuerda que el mínimo es $500 y el máximo permitido es $500,000.")
            print("Aquí te doy un ejemplo de cómo puedes responder:")
            print("**Ejemplo:** \"Quiero invertir 20000 para un plazo de 12 meses.\"")
            monto = float(input("Ingrese el monto a invertir: "))
            if monto < 500 or monto > 500000:
                print("El monto ingresado no está dentro del rango permitido (500 - 500,000 dólares).")
            elif monto > usuario['saldo']:
                print("Fondos insuficientes para realizar la inversión.")
            else:
                plazo = input("Ingrese el plazo de la inversión en meses: ")
                try:
                    plazo_dias = int(plazo) * 30  # Aproximar los meses a días
                    if plazo_dias > 361:
                        plazo_dias = 361
                        print("El plazo máximo permitido para nuestras inversiones es de 361 días. Ajustaremos el plazo automáticamente.")
                    tasa_nominal = 7.0
                    interes_generado = monto * (tasa_nominal / 100) * (plazo_dias / 365)
                    retencion = 35 if interes_generado > 500 else 0
                    total_acumulado = monto + interes_generado - retencion
                    fecha_vencimiento = (datetime.now() + timedelta(days=plazo_dias)).strftime("%d-%m-%Y")
                    print("¡Gracias por tu interés en invertir con nosotros! Aquí tienes toda la información para que puedas tomar una decisión informada:")
                    print(f"1. **Monto de la inversión**: ${monto:.2f}")
                    print(f"2. **Plazo solicitado**: {plazo} meses ({plazo_dias} días)")
                    print(f"3. **Tasa nominal**: {tasa_nominal}%")
                    print(f"4. **Interés generado**: ${interes_generado:.2f}")
                    print(f"5. **Retención por impuestos**: ${retencion:.2f}")
                    print(f"6. **Total acumulado**: ${total_acumulado:.2f}")
                    print(f"7. **Fecha de vencimiento**: {fecha_vencimiento}")
                    usuario['saldo'] -= monto
                    agregar_transaccion(cedula, "inversión", monto)
                    guardar_usuarios(usuarios)
                    print(f"Inversión realizada con éxito. Su nuevo saldo es: {usuario['saldo']:.2f}")
                except ValueError:
                    print("El plazo ingresado no es válido. Por favor, ingresa un número de meses.")

        elif user_input == "4" or "tarjeta de crédito" in user_input:
            print(
                "Chip: ¡Hola! Actualmente el proceso de solicitud de tarjeta de crédito no está implementado en el chatbot. Puedes dirigirte al siguiente enlace para más información: https://www.bancointernacional.com.ec/personas/tarjetas-de-credito/")
            break

        elif user_input == "5" or "servicios asistenciales" in user_input or "asistenciales" in user_input or "asistencia" in user_input:
            print("Hola, soy la sección de Chip experto en finanzas. Hazme cualquier pregunta de asesoramiento financiero.")
            while True:
                consulta_financiera = input("Usuario: ").strip()
                if consulta_financiera.lower() in ["salir", "terminar", "volver"]:
                    break
                response = model.generate_content(f"Eres un asesor financiero experto. Responde la siguiente consulta de manera clara y precisa:\nUsuario: {consulta_financiera}\nAsesor:")
                print("Asesor:", response.text)

        elif user_input == "6" or "salir" in user_input or "out" in user_input:
            print("Gracias por usar el CHIP, el asistente de Banco Internacional. ¡Hasta luego!")
            break
        elif "saldo" in user_input or "cuánto dinero tengo" in user_input:
            print(f"Chip: Tu saldo actual es de {usuario['saldo']:.2f} dólares.")

        else:
            response = chat_chip(user_input, usuario)
            print("Chip:", response)

# Ejecutar el chatbot
if __name__ == "__main__":
    main()