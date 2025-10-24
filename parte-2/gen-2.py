#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import os
import re

#Comprueba el número de argumentos
if len(sys.argv) != 3:
    print("Debe tener dos argumentos")
    sys.exit(1)

#Fichero de entrada (primer argumento)
entrada_arg = sys.argv[1]
#Fichero de salida (segundo argumento)
salida_arg = sys.argv[2]

#Localiza la carpeta donde está gen-2.py
script_dir = os.path.dirname(os.path.abspath(__file__))

#Resolver la ruta del fichero de entrada
#Si el argumento contiene / o \ significa que se ha indicado una ruta relativa o absoluta
if '/' in entrada_arg or '\\' in entrada_arg:
    #Se convierte a una ruta absoluta
    entrada = os.path.abspath(entrada_arg)
else:
    #Si no contiene separadores solo se puso el nombre
    #Se busca dentro de la carpeta del script y se unen
    entrada = os.path.join(script_dir, entrada_arg)

#Resolver la ruta del fichero de salida
#Si el argumento contiene / o \ significa que se ha indicado una ruta relativa o absoluta
if '/' in salida_arg or '\\' in salida_arg:
    #Se convierte a una ruta absoluta
    salida = os.path.abspath(salida_arg)
else:
    #Si no contiene separadores solo se puso el nombre
    #Se busca dentro de la carpeta del script y se unen
    salida = os.path.join(script_dir, salida_arg)


#Lee el fichero de entrada
try:
    #Abre el archivo en modo lectura
    with open(entrada, "r", encoding="utf-8") as f:
        #Guardado de líneas sin espacios ni saltos
        lineas = [l.strip() for l in f if l.strip()]

    #Primera línea: número de franjas (n), autobuses (m) y talleres (u)
    n, m, u = map(int, lineas[0].split())

    #Matriz de pasajeros coincidentes c_ab (m x m)
    matriz_c = []
    for i in range(1, 1 + m):
        fila = list(map(float, lineas[i].split()))
        if len(fila) != m:
            raise ValueError
        matriz_c.append(fila)

    #Matriz de disponibilidad o_ij (n x u)
    matriz_o = []
    inicio_o = 1 + m
    for i in range(inicio_o, inicio_o + n):
        fila = list(map(int, lineas[i].split()))
        if len(fila) != u:
            raise ValueError
        matriz_o.append(fila)

#Si ocurre algún problema en la lectura o formato
except Exception:
    print("Error de formato en el fichero de entrada")
    sys.exit(1)


#Genera el fichero .dat
try:
    #Abre el archivo en modo escritura
    with open(salida, "w", encoding="utf-8") as f:
        #Escritura de conjuntos
        f.write("set Autobus := " + " ".join(f"a{i+1}" for i in range(m)) + ";\n")
        f.write("set Franja := " + " ".join(f"s{i+1}" for i in range(n)) + ";\n")
        f.write("set Taller := " + " ".join(f"t{i+1}" for i in range(u)) + ";\n\n")

        #Escritura del parámetro pasajeros_coincidentes (matriz m x m)
        f.write("param pasajeros_coincidentes : " + " ".join(f"a{j+1}" for j in range(m)) + " :=\n")
        for i in range(m):
            f.write(f"a{i+1} " + " ".join(str(matriz_c[i][j]) for j in range(m)) + "\n")
        f.write(";\n\n")

        #Escritura del parámetro disponible (matriz n x u)
        f.write("param disponible : " + " ".join(f"t{j+1}" for j in range(u)) + " :=\n")
        for i in range(n):
            f.write(f"s{i+1} " + " ".join(str(matriz_o[i][j]) for j in range(u)) + "\n")
        f.write(";\n\nend;\n")

#Si ocurre algún problema en la escritura
except Exception:
    print("No se pudo escribir en el fichero de salida")
    sys.exit(1)

#Ruta absoluta para el modelo y el fichero de resultado
modelo = os.path.join(script_dir, "parte-2-2.mod")
resultado = os.path.join(script_dir, "resultado1.txt")

#Comprueba que el modelo existe
if not os.path.exists(modelo):
    print("No se encontró 'parte-2-2.mod'")
    sys.exit(1)

#Ejecución del solver GLPK
try:
    #Ejecuta el comando glpsol en el sistema
    #check para comprobar si falla y las redirecciones a nada para que oculte el texto de GLPK
    subprocess.run(["glpsol", "-m", modelo, "-d", salida, "-o", resultado],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#Si hay error en la ejecución del solver
except Exception:
    print("Error al ejecutar GLPK")
    sys.exit(1)

#Lectura del fichero de resultados en fichero de resultados
try:
    with open(resultado, "r", encoding="utf-8") as f:
        lineas = f.readlines()
except Exception:
    print("No se pudo leer 'resultado1.txt'")
    sys.exit(1)

objetivo = None
asignaciones = []
filas = None
columnas = None

#Buscar valor del objetivo, restricciones y variables de decisión
for linea in lineas:
    if "Objective:" in linea:
        mo = re.search(r"=\s*([-+]?\d+\.?\d*)", linea)
        if mo:
            objetivo = float(mo.group(1))
    if "Rows:" in linea:
        filas = int(re.search(r"Rows:\s+(\d+)", linea).group(1))
    if "Columns:" in linea:
        columnas = int(re.search(r"Columns:\s+(\d+)", linea).group(1))

#Buscar variables asignadas con valor 1
en_columnas = False
for i, linea in enumerate(lineas):
    if linea.strip().startswith("No. Column name"):
        en_columnas = True
        continue
    if en_columnas:
        if linea.strip().startswith("Integer feasibility"):
            break
        m_var = re.search(r"asignacion\[(a\d+),(s\d+),(t\d+)\]", linea)
        if m_var:
            a, s, t = m_var.group(1), m_var.group(2), m_var.group(3)
            #Mira si el *1 está en la misma línea o en la siguiente
            if re.search(r"\*\s+1", linea) or (i + 1 < len(lineas) and re.search(r"\*\s+1", lineas[i + 1])):
                asignaciones.append((a, s, t))


#Muestra de resultados
print("\n------------RESULTADOS------------\n")

#Muestra el valor óptimo, número de variables y restricciones
print(f"Valor óptimo función objetivo: min Impacto_Total = {objetivo} | Número de variables de decisión = {columnas} | Número de restricciones = {filas}")

#Si hay asignaciones óptimas
if asignaciones:
    print("\nAsignaciones óptimas:")
    for a, s, t in asignaciones:
        print(f"  Autobús {a} → Franja {s} en Taller {t}")
#Si no hay asignaciones
else:
    print("\nNo hay asignaciones válidas encontradas.")

print("\n------------------------------------")
