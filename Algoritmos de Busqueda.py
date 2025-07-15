from collections import deque
import random


# Permite definir tamaño, establecer entrada y salida, marcar posiciones con símbolos, consultar el contenido de una celda, verificar accesibilidad y agregar obstáculos
class Mapa:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.capacidad_total = filas * columnas
        self.grid = [["." for _ in range(columnas)] for _ in range(filas)]
        self.entrada = None
        self.salida = None

    def imprimir(self):
        for fila in self.grid:
            print(" ".join(fila))

    def marcar_posicion(self, fila, columna, simbolo):
        self.grid[fila][columna] = simbolo

    def consultar_posicion(self, fila, columna):
        return self.grid[fila][columna]

    def es_accesible(self, fila, columna):
        return self.consultar_posicion(fila, columna) in (".", "S")

    def agregar_obstaculo(self, fila, columna, simbolo):
        self.marcar_posicion(fila, columna, simbolo)

    def limpiar_camino(self):
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.grid[fila][columna] == "*":
                    self.grid[fila][columna] = "."


# Permite crear obstáculos aleatorios (como edificios y agua) respetando un límite máximo, agregar obstáculos manualmente con validación de coordenadas y verificar si una posición específica está ocupada por un obstáculo.
class ObstaculoManager:
    def __init__(self, mapa):
        self.mapa = mapa
        self.ocupados = set()

    def generar_aleatorios(self):
        max_obstaculos = int(self.mapa.capacidad_total * 0.3)
        cantidad_edificios = random.randint(
            int(self.mapa.capacidad_total * 0.1),
            int(self.mapa.capacidad_total * 0.2),
        )
        cantidad_agua = random.randint(
            int(self.mapa.capacidad_total * 0.1),
            int(self.mapa.capacidad_total * 0.2),
        )
        if cantidad_edificios + cantidad_agua > max_obstaculos:
            cantidad_agua = max_obstaculos - cantidad_edificios

        print(f"\nCantidad aleatoria de edificios: {cantidad_edificios}")
        print(f"Cantidad aleatoria de agua: {cantidad_agua}")

        self.generar_obstaculos(cantidad_edificios, "#")
        self.generar_obstaculos(cantidad_agua, "@")

    def generar_obstaculos(self, cantidad, simbolo):
        while cantidad > 0:
            fila = random.randint(0, self.mapa.filas - 1)
            columna = random.randint(0, self.mapa.columnas - 1)
            if (fila, columna) not in self.ocupados:
                self.ocupados.add((fila, columna))
                self.mapa.agregar_obstaculo(fila, columna, simbolo)
                cantidad -= 1

    def agregar_manual(self):
        while True:
            opcion = int(input("Agregar obstaculo: 1 - Si, 0 - No\n"))
            if opcion == 0:
                break
            fila = int(input("Fila\n"))
            columna = int(input("Columna\n"))
            if not (0 <= fila < self.mapa.filas and 0 <= columna < self.mapa.columnas):
                print("Coordenada fuera del mapa")
            elif (fila, columna) in self.ocupados:
                print("Coordenada ya ocupada")
            else:
                self.ocupados.add((fila, columna))
                self.mapa.agregar_obstaculo(fila, columna, "X")
                print("Obstaculo agregado")
                self.mapa.imprimir()

    def es_obstaculo(self, posicion):
        return posicion in self.ocupados


# Clase base abstracta que define la estructura para algoritmos de búsqueda en un mapa. Almacena referencias a la entrada y salida del mapa y obliga a que las subclases implementen el método buscar().
class AlgoritmoDeBusqueda:
    def __init__(self, mapa):
        self.mapa = mapa
        self.entrada = mapa.entrada
        self.salida = mapa.salida

    def buscar(self):
        raise NotImplementedError("Este metodo debe ser implementado por una sobclase.")


class BusquedaBFS(AlgoritmoDeBusqueda):
    def buscar(self):
        cola = deque([(self.entrada, [self.entrada])])
        visitados = set()

        while cola:
            (fila, columna), camino = cola.popleft()
            if (fila, columna) in visitados:
                continue
            visitados.add((fila, columna))

            if (fila, columna) == self.salida:
                return camino

            for desplazamiento_fila, desplazamiento_columna in [
                (0, 1),
                (0, -1),
                (1, 0),
                (-1, 0),
            ]:
                nueva_fila, nueva_columna = (
                    fila + desplazamiento_fila,
                    columna + desplazamiento_columna,
                )
                if (
                    0 <= nueva_fila < self.mapa.filas
                    and 0 <= nueva_columna < self.mapa.columnas
                ):
                    if self.mapa.es_accesible(nueva_fila, nueva_columna):
                        cola.append(
                            (
                                (nueva_fila, nueva_columna),
                                camino + [(nueva_fila, nueva_columna)],
                            )
                        )
        return None


class CalculadorDeRutas:
    def __init__(self, algoritmo: AlgoritmoDeBusqueda):
        self.algoritmo = algoritmo

    def resolver(self):
        return self.algoritmo.buscar()

    def mostrar_camino(self, camino):
        if camino:
            for fila, columna in camino[1:-1]:
                self.algoritmo.mapa.marcar_posicion(fila, columna, "*")
        else:
            print("No se encontro un camino")


class Simulador:
    def __init__(self):
        filas = int(input("Ingrese numero de filas\n"))
        columnas = int(input("Ingrese numero de columnas\n"))
        self.mapa = Mapa(filas, columnas)
        self.obstaculos = ObstaculoManager(self.mapa)

    def iniciar(self):
        self.obstaculos.generar_aleatorios()
        self.mapa.imprimir()
        self.configurar_entrada_salida()
        self.ejecutar_busqueda()

        while True:
            print("Desea agregar un nuevo obstaculo?\n")
            self.obstaculos.agregar_manual()
            self.mapa.limpiar_camino()
            self.ejecutar_busqueda()
            break

    def configurar_entrada_salida(self):
        while True:
            entrada_fila = int(input("Fila de entrada\n"))
            entrada_columna = int(input("Columna de entrada\n"))
            salida_fila = int(input("Fila de salida\n"))
            salida_columna = int(input("Columna de salida\n"))
            entrada = (entrada_fila, entrada_columna)
            salida = (salida_fila, salida_columna)

            if not self.coordenadas_validas(entrada) or not self.coordenadas_validas(
                salida
            ):
                print("Coordenada fuera del mapa")
                continue
            if self.obstaculos.es_obstaculo(entrada):
                print("La entrada esta sobre un obstaculo")
                continue
            if self.obstaculos.es_obstaculo(salida):
                print("La salida esta sobre un obstaculo")
                continue

            self.mapa.entrada = entrada
            self.mapa.salida = salida
            self.mapa.marcar_posicion(*entrada, "E")
            self.mapa.marcar_posicion(*salida, "S")
            break

    def coordenadas_validas(self, posicion):
        fila, columna = posicion
        return 0 <= fila < self.mapa.filas and 0 <= columna < self.mapa.columnas

    def ejecutar_busqueda(self):
        algoritmo = BusquedaBFS(self.mapa)
        calculadora = CalculadorDeRutas(algoritmo)
        camino = calculadora.resolver()
        print("Camino encontrado")
        calculadora.mostrar_camino(camino)
        self.mapa.imprimir()


if __name__ == "__main__":
    Simulador().iniciar()
