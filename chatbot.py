import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configurar la API de Google
genai.configure(api_key=api_key)

# Base de datos de usuarios simulada
usuarios = {
    "1234567890": {
        "nombre": "Marcelo Rodriguez",
        "fecha_nacimiento": "22/10/1990",
        "correo": "marcelo@gmail.com",
        "celular": "0934567891",
        "saldo": 1000.0  # Saldo inicial en la cuenta de ahorros
    },
    "0987654321": {
        "nombre": "Ana Perez",
        "fecha_nacimiento": "15/06/1985",
        "correo": "ana@gmail.com",
        "celular": "0938765432",
        "saldo": 1500.0  # Saldo inicial en la cuenta de ahorros
    }
}

# Crear el modelo generativo
model = genai.GenerativeModel(model_name="gemini-pro")


# Función para interactuar con Chip
def chat_chip(user_input, usuario):
    # Crear un prompt personalizado para Chip, el asistente bancario
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
    while True:
        cedula = input("Por favor, ingrese su número de cédula: ")
        if cedula in usuarios:
            print(f"Bienvenido, {usuarios[cedula]['nombre']}!")
            return cedula
        else:
            print("Número de cédula no encontrado. Intente nuevamente.")


# Bucle principal de interacción
def main():
    cedula = autenticar_usuario()
    usuario = usuarios[cedula]

    while True:
        # Mostrar las opciones solo si el usuario no hace una consulta natural
        print("\nOpciones disponibles:")
        print("1. Abrir una cuenta de ahorros")
        print("2. Realizar una transferencia")
        print("3. Hacer una inversión")
        print("4. Solicitar una tarjeta de crédito")
        print("5. Salir")

        # Recibir entrada del usuario
        user_input = input("Por favor, seleccione una opción o escriba su consulta: ").strip().lower()

        # Manejar opciones numéricas o texto natural
        if user_input == "1" or "abrir una cuenta de ahorros" in user_input:
            response = chat_chip("Quiero abrir una cuenta de ahorros.", usuario)
            print("Chip:", response)

        elif user_input == "2" or "transferencia" in user_input:
            receptor_cedula = input("Ingrese el número de cédula del receptor: ")
            if receptor_cedula in usuarios:
                monto = float(input("Ingrese el monto a transferir: "))
                if monto > usuario['saldo']:
                    print("Fondos insuficientes para realizar la transferencia.")
                else:
                    usuario['saldo'] -= monto
                    usuarios[receptor_cedula]['saldo'] += monto
                    print(f"Transferencia realizada con éxito. Su nuevo saldo es: {usuario['saldo']:.2f}")
            else:
                print("El número de cédula del receptor no fue encontrado.")

        elif user_input == "3" or "inversión" in user_input or "invertir" in user_input:
            monto = float(input("Ingrese el monto a invertir: "))
            if monto > usuario['saldo']:
                print("Fondos insuficientes para realizar la inversión.")
            else:
                usuario['saldo'] -= monto
                response = chat_chip(f"Quiero hacer una inversión de {monto} dólares.", usuario)
                print("Chip:", response)

        elif user_input == "4" or "tarjeta de crédito" in user_input:
            response = chat_chip("Quiero solicitar una tarjeta de crédito.", usuario)
            print("Chip:", response)

        elif user_input == "5" or "salir" in user_input:
            print("Gracias por usar el asistente de Banco Internacional. ¡Hasta luego!")
            break

        elif "saldo" in user_input or "cuánto dinero tengo" in user_input:
            print(f"Chip: Tu saldo actual es de {usuario['saldo']:.2f} dólares.")

        else:
            # Si la entrada no es válida, también generará una respuesta generativa del chatbot.
            response = chat_chip(user_input, usuario)
            print("Chip:", response)


# Ejecutar el chatbot
if __name__ == "__main__":
    main()
