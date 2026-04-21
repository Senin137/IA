import random

def mostrar_matriz(matriz):
    for r in range(3):
        print(f" {matriz[r][0] or ' '} | {matriz[r][1] or ' '} | {matriz[r][2] or ' '}")
        if r < 2: print("---|---|---")
    
def verificar_ganador(matriz):
    for i in range(3):
        if matriz[i][0] == matriz[i][1] == matriz[i][2] != "":
            return matriz[i][0]
        if matriz[0][i] == matriz[1][i] == matriz[2][i] != "":
            return matriz[0][i]
    
    if matriz[0][0] == matriz[1][1] == matriz[2][2] != "":
        return matriz[0][0]
    if matriz[0][2] == matriz[1][1] == matriz[2][0] != "":
        return matriz[0][2]
    
    return None

matriz = [["","",""],["","",""],["","",""]]
mostrar_matriz(matriz)

for i in range(0,9):
    if i % 2 == 0:
        print("Jugador X: !Es tu turno!")
        row = int(input("Ingresa la fila (0, 1, 2): "))
        col = int(input("Ingresa la columna (0, 1, 2): "))

        while matriz[row][col] != "":
            print("¡Esa posición ya está ocupada! Intenta de nuevo.")
            row = int(input("Ingresa la fila (0, 1, 2): "))
            col = int(input("Ingresa la columna (0, 1, 2): "))

        matriz[row][col] = "X"
        

    else:
        print("Jugador O: ¡Es tu turno!")
        row = random.randint(0, 2)
        col = random.randint(0, 2)

        while matriz[row][col] != "":
            print("¡Esa posición ya está ocupada! Intenta de nuevo.")
            row = random.randint(0, 2)
            col = random.randint(0, 2)

        matriz[row][col] = "O"
        mostrar_matriz(matriz)
        
        ganador = verificar_ganador(matriz)
        if ganador:
            print("¡El ganador es: " + ganador + "!")
            break
        else:
            print("¡Es un empate!")