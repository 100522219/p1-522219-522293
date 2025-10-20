#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import re
import os

#Comprueba el número de argumentos
if len(sys.argv) != 3:
    print("Debe tener dos argumentos")
    sys.exit(1)

#Fichero de entrada (primer argumento)
entrada_arg = sys.argv[1]
#Fichero de salida (segundo argumento)
salida_arg = sys.argv[2]

#Localiza la carpeta donde está gen-1.py
script_dir = os.path.dirname(os.path.abspath(__file__))

#Resolver la ruta del fichero de entrada
#Si el argumento contiene / o \ significa que se ha indicado una ruta relativa o absoluta
if '/' in entrada_arg or '\\' in entrada_arg:
    #Se convierte a una ruta absoluta
    entrada = os.path.abspath(entrada_arg)
else:
    #Si no contiene separadores solo se puso el nombre
    #Se busca dentro de la carpeta de gen-1 y se unen
    entrada = os.path.join(script_dir, entrada_arg)


#Resolver la ruta del fichero de salida
#Si el argumento contiene / o \ significa que se ha indicado una ruta relativa o absoluta
if '/' in salida_arg or '\\' in salida_arg:
    #Se convierte a una ruta absoluta
    salida = os.path.abspath(salida_arg)
else:
    #Si no contiene separadores solo se puso el nombre
    #Se busca dentro de la carpeta de gen-1 y se unen
    salida = os.path.join(script_dir, salida_arg)

#Lee el fichero de entrada
try:
    #Abre el archivo en modo lectura
    with open(entrada, "r", encoding="utf-8") as f:
        #Guardado de líneas
        lineas= []
        #Se recorre el archivo línea a línea
        for l in f:
            #Se quitan los espacios
            l = l.strip()
            #Si no está vacía se añade
            if l:
                lineas.append(l)

    #Número de franjas y autobuses
    n, m = map(int, lineas[0].split())
    #Coste asignación y penalización
    kd, kp = map(float, lineas[1].split())
    #Lista de distancias
    distancias = list(map(float, lineas[2].split()))
    #Lista de pasajeros
    pasajeros = list(map(float, lineas[3].split()))

#Si ocurre algún problema en la lectura
except Exception:
    print("Error de formato en el fichero de entrada")
    sys.exit(1)

#Si la longitud de las listas de distancias o pasajeros no coinciden con el número de buses
if len(distancias)!=m or len(pasajeros)!=m:
    print("Número de distancias o pasajeros distinto a m")
    sys.exit(1)

#Genera el fichero .dat
try:
    #Abre el archivo en modo escritura
    with open(salida, "w", encoding="utf-8") as f:
        #Escritura de sets
        f.write("set Autobus := " + " ".join(f"a{i+1}" for i in range(m)) + ";\n")
        f.write("set Franja := " + " ".join(f"s{j+1}" for j in range(n)) + ";\n\n")
        #Escritura de parámetros
        f.write(f"param coste_asignacion := {kd};\n")
        f.write(f"param penalizacion_no_asignacion := {kp};\n")
        f.write("param max_asignaciones_autobus := 1;\n")
        f.write("param max_autobuses_franja := 1;\n\n")
        f.write("param distancia :=\n")
        for i in range(m):
            f.write(f"  a{i+1} {distancias[i]}\n")
        f.write(";\n\n")
        f.write("param pasajeros :=\n")
        for i in range(m):
            f.write(f"  a{i+1} {pasajeros[i]}\n")
        f.write(";\n\nend;\n")

#Si ocurre algún problema en la escritura
except Exception:
    print(" No se pudo escribir en el fichero de salida")
    sys.exit(1)

#Ruta absoluta para modelo y resultado
modelo = os.path.join(script_dir, "parte-2-1.mod")
resultado = os.path.join(script_dir, "resultado.txt")

#Si no se encuentra el modelo
if not os.path.exists(modelo):
    print("No se encontró 'parte-2-1.mod'")
    sys.exit(1)

#Ejecución GLPK
try:
    #Ejecuta el comando glpsol en el sistema
    #check para comprobar si falla y las redirecciones a nada para que oculte el texto de GLPK
    subprocess.run(["glpsol", "-m", str(modelo), "-d", str(salida), "-o", str(resultado)],
             check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception as e:
    print("Error al ejecutar GLPK")
    sys.exit(1)


#FALTA POR COMENTAR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ---------------- LEER RESULTADO DE GLPK ----------------
# El fichero resultado.txt contiene el log completo del solver.
# Buscamos:
#   - Línea con "Objective:" → valor de la función objetivo.
#   - Variables asignacion[a?,s?] con valor '* 1' en la línea siguiente.

#Lectura de resultado GLPK
try:
    with open(resultado, "r", encoding="utf-8") as f:
        lineas = f.readlines()
except Exception:
    print("No se pudo leer 'resultado.txt'")
    sys.exit(1)

objetivo = None
asignaciones = []

# Buscar valor del objetivo
for linea in lineas:
    if "Objective:" in linea:
        mo = re.search(r"=\s*([-+]?\d+\.?\d*)", linea)
        if mo:
            objetivo = float(mo.group(1))
        break

# Buscar asignaciones activas
en_columnas = False
for i, linea in enumerate(lineas):
    if linea.strip().startswith("No. Column name"):
        en_columnas = True
        continue
    if en_columnas:
        if linea.strip().startswith("Integer feasibility"):
            break
        m_var = re.search(r"asignacion\[(a\d+),(s\d+)\]", linea)
        if m_var:
            a, s = m_var.group(1), m_var.group(2)
            if i + 1 < len(lineas) and re.search(r"\*\s+1(\D|$)", lineas[i + 1]):
                asignaciones.append((a, s))
#FALTA POR COMENTAR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!




#Muestra de resultados
print("\n------------RESULTADOS------------\n")

print(f"Valor optimo funcion objetivo: min Perdida = {objetivo} | Variables de decision = {m*n} | Restricciones = {m+n+1}")
#Si hay asignaciones de autobuses
if asignaciones:
    print("\nAsignaciones optimas:")
    for a, s in asignaciones:
        print(f"  Autobus {a} -> Franja {s}")
#Si no hay asignaciones a autobuses
else:
    print("\nNo hay asignaciones")

#Lista de todos los autobuses
todos_autobuses = [f"a{i+1}" for i in range(m)]
# --- Determinar qué autobuses están asignados y cuáles no ---

#Creación de un conjunto con los autobuses que sí aparecen asignados
asignados = set()
for a, franja in asignaciones:
    asignados.add(a)

#Lista de autobuses que no tienen ninguna franja asignada
no_asignados = []
for a in todos_autobuses:
    if a not in asignados:
        no_asignados.append(a)

#Autubuses sin asignar franja
if no_asignados:
    print("\nAutobuses sin asignar:")
    for a in no_asignados:
        print(f"  Autobus {a} sin franja")

print("------------------------------------")
