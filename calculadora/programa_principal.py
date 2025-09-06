

from calculadora.suma import add
from calculadora.resta import subtract
from calculadora.multiplicacion import multiply
from calculadora.division import divide

def main():
    print("=== Calculadora en Python ===")
    print("Operaciones disponibles:")
    print("1. Suma")
    print("2. Resta")
    print("3. Multiplicación")
    print("4. División")

    opcion = input("Elige una operación (1-4): ")

    a = float(input("Ingresa el primer número: "))
    b = float(input("Ingresa el segundo número: "))

    if opcion == "1":
        print(f"Resultado: {add(a, b)}")
    elif opcion == "2":
        print(f"Resultado: {subtract(a, b)}")
    elif opcion == "3":
        print(f"Resultado: {multiply(a, b)}")
    elif opcion == "4":
        try:
            print(f"Resultado: {divide(a, b)}")
        except ValueError as e:
            print(e)
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()
