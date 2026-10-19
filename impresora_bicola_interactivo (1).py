"""
Sistema de impresión compartida con BICOLA (deque) - VERSIÓN INTERACTIVA.

- Gerente  -> documento URGENTE -> se inserta al INICIO de la bicola.
- Empleado -> documento NORMAL  -> se encola al FINAL de la bicola.

Primero se registran todas las peticiones; después la impresora las
procesa tomando siempre del inicio y se miden los tiempos.
"""
import time


# ----------------------------------------------------------------------
# Bicola implementada con lista doblemente enlazada (sin collections.deque)
# ----------------------------------------------------------------------
class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.anterior = None
        self.siguiente = None


class Bicola:
    def __init__(self):
        self.frente = None
        self.final = None
        self.tamano = 0

    def esta_vacia(self):
        return self.tamano == 0

    def insertar_inicio(self, dato):          # O(1)
        nodo = Nodo(dato)
        if self.esta_vacia():
            self.frente = self.final = nodo
        else:
            nodo.siguiente = self.frente
            self.frente.anterior = nodo
            self.frente = nodo
        self.tamano += 1

    def insertar_final(self, dato):           # O(1)
        nodo = Nodo(dato)
        if self.esta_vacia():
            self.frente = self.final = nodo
        else:
            nodo.anterior = self.final
            self.final.siguiente = nodo
            self.final = nodo
        self.tamano += 1

    def eliminar_inicio(self):                # O(1)
        if self.esta_vacia():
            return None
        dato = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente:
            self.frente.anterior = None
        else:
            self.final = None
        self.tamano -= 1
        return dato

    def eliminar_final(self):                 # O(1)
        if self.esta_vacia():
            return None
        dato = self.final.dato
        self.final = self.final.anterior
        if self.final:
            self.final.siguiente = None
        else:
            self.frente = None
        self.tamano -= 1
        return dato

    def elementos(self):
        actual = self.frente
        while actual:
            yield actual.dato
            actual = actual.siguiente


# ----------------------------------------------------------------------
# Documento y petición de impresión
# ----------------------------------------------------------------------
class Documento:
    def __init__(self, nombre, usuario, rol, paginas):
        self.nombre = nombre
        self.usuario = usuario
        self.rol = rol                         # "gerente" | "empleado"
        self.paginas = paginas
        self.urgente = (rol == "gerente")
        self.t_llegada = None                  # se asigna al encolar
        self.t_inicio = None
        self.t_fin = None

    @property
    def etiqueta(self):
        return "URGENTE" if self.urgente else "NORMAL "


# ----------------------------------------------------------------------
# Impresora
# ----------------------------------------------------------------------
class Impresora:
    SEG_POR_PAGINA = 1.0       # la impresora imprime 1 hoja por segundo
    UMBRAL_RETRASO = 15.0      # espera (s) a partir de la cual hay "retraso"

    def __init__(self):
        self.bicola = Bicola()
        self.historial = []
        self.total = 0.0

    def agregar_peticion(self, doc):
        doc.t_llegada = time.perf_counter()
        if doc.urgente:
            self.bicola.insertar_inicio(doc)
            destino = "INICIO"
        else:
            self.bicola.insertar_final(doc)
            destino = "FINAL "
        print(f"[+] {doc.etiqueta} {doc.nombre:<26} ({doc.usuario}, {doc.rol}, "
              f"{doc.paginas:>2} pág.) -> encolado al {destino}")

    def mostrar_cola(self):
        orden = " | ".join(f"{d.nombre} [{d.etiqueta.strip()[0]}]"
                           for d in self.bicola.elementos())
        print(f"\nOrden de impresión resultante ({self.bicola.tamano} docs):\n  {orden}\n")

    def procesar_cola(self):
        print("=" * 78)
        print("INICIO DE IMPRESIÓN")
        print("=" * 78)
        total_paginas = sum(d.paginas for d in self.bicola.elementos())
        print(f"Velocidad: {1/self.SEG_POR_PAGINA:g} hoja(s)/segundo | "
              f"{total_paginas} hojas en cola | tiempo estimado: "
              f"{total_paginas*self.SEG_POR_PAGINA:.0f}s\n")
        t0 = time.perf_counter()
        t_fin_anterior = None
        n = 0
        while not self.bicola.esta_vacia():
            doc = self.bicola.eliminar_inicio()
            n += 1
            doc.t_inicio = time.perf_counter()
            print(f">>> Imprimiendo {doc.etiqueta.strip()} '{doc.nombre}' de {doc.usuario} "
                  f"({doc.paginas} hojas)")
            for hoja in range(1, doc.paginas + 1):
                time.sleep(self.SEG_POR_PAGINA)             # 1 hoja = 1 segundo
                transcurrido = time.perf_counter() - t0
                print(f"      hoja {hoja:>2}/{doc.paginas}  (t = {transcurrido:5.1f}s)")
            doc.t_fin = time.perf_counter()

            espera = doc.t_inicio - t0
            duracion = doc.t_fin - doc.t_inicio
            intervalo = (doc.t_inicio - t_fin_anterior) if t_fin_anterior else 0.0
            t_fin_anterior = doc.t_fin
            retraso = espera > self.UMBRAL_RETRASO

            print(f"    {n:>2}. {doc.etiqueta} {doc.nombre:<26} | espera: {espera:5.2f}s | "
                  f"impresión: {duracion:5.2f}s | entre docs: {intervalo*1000:5.1f}ms"
                  f"{'  <-- RETRASO' if retraso else ''}")
            print()
            self.historial.append((doc, espera, duracion, retraso))
        self.total = time.perf_counter() - t0

    def reporte(self):
        print("\n" + "=" * 78)
        print("REPORTE DE TIEMPOS")
        print("=" * 78)
        for etiqueta, es_urg in (("URGENTES", True), ("NORMALES", False)):
            grupo = [h for h in self.historial if h[0].urgente == es_urg]
            if not grupo:
                continue
            esperas = [h[1] for h in grupo]
            retrasados = sum(1 for h in grupo if h[3])
            print(f"{etiqueta}: {len(grupo)} docs | espera promedio {sum(esperas)/len(esperas):.2f}s "
                  f"| espera máx. {max(esperas):.2f}s | con retraso (> {self.UMBRAL_RETRASO}s): {retrasados}")
        print(f"Tiempo total de impresión: {self.total:.2f}s")


# ----------------------------------------------------------------------
# Entrada de datos por consola
# ----------------------------------------------------------------------
def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("   (!) Este campo no puede estar vacío.")


def pedir_cargo():
    while True:
        print("   Cargo:  1) Gerente   2) Empleado")
        op = input("   Elige una opción (1/2): ").strip().lower()
        if op in ("1", "gerente"):
            return "gerente"
        if op in ("2", "empleado"):
            return "empleado"
        print("   (!) Opción no válida.")


def pedir_paginas():
    while True:
        valor = input("   Cantidad de páginas a imprimir: ").strip()
        if valor.isdigit() and int(valor) > 0:
            return int(valor)
        print("   (!) Ingresa un número entero mayor que 0.")


def solicitar_peticion(impresora):
    print("\n--- NUEVA PETICIÓN DE IMPRESIÓN ---")
    usuario = pedir_texto("   Tu nombre: ")
    rol = pedir_cargo()
    paginas = pedir_paginas()
    nombre_doc = pedir_texto("   Nombre con el que se registrará la impresión: ").replace(" ", "_")
    impresora.agregar_peticion(Documento(nombre_doc, usuario, rol, paginas))


def menu():
    impresora = Impresora()
    while True:
        print("\n" + "=" * 50)
        print(" IMPRESORA COMPARTIDA (BICOLA)")
        print("=" * 50)
        print(f" Documentos en cola: {impresora.bicola.tamano}")
        print(" 1) Agregar petición de impresión")
        print(" 2) Ver orden actual de la cola")
        print(" 3) Imprimir todos los documentos")
        print(" 4) Salir")
        op = input(" Opción: ").strip()

        if op == "1":
            solicitar_peticion(impresora)
        elif op == "2":
            if impresora.bicola.esta_vacia():
                print("\n La cola está vacía.")
            else:
                impresora.mostrar_cola()
        elif op == "3":
            if impresora.bicola.esta_vacia():
                print("\n No hay documentos para imprimir.")
            else:
                impresora.mostrar_cola()
                impresora.procesar_cola()
                impresora.reporte()
                impresora = Impresora()      # impresora lista para una nueva tanda
        elif op == "4":
            if not impresora.bicola.esta_vacia():
                print(f"\n Atención: quedan {impresora.bicola.tamano} documentos sin imprimir.")
                if input(" ¿Salir de todos modos? (s/n): ").strip().lower() != "s":
                    continue
            print("\n Hasta luego.")
            break
        else:
            print(" (!) Opción no válida.")


if __name__ == "__main__":
    menu()
