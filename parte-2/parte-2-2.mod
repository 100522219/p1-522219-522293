/*parte-2-2.mod*/


/*Conjuntos*/

/*Conjunto de autobuses*/
set Autobus;
/*Conjunto de franjas*/
set Franja;
/*Conjunto de talleres*/
set Taller;


/*Parámetros*/

/*Pasajeros en común entre pares de autobuses*/
param pasajeros_coincidentes {a in Autobus, b in Autobus} >= 0;

/*Disponibilidad de cada franja en cada taller*/
param disponible {i in Franja, j in Taller} binary;


/*Variables de decisión*/

/*Asignación de un autobús a a la franja i del taller j*/
var asignacion {a in Autobus, i in Franja, j in Taller} binary;

/*Asignación del autobús a y b a la franja i independientemente del taller*/
var coincide {a in Autobus, b in Autobus, i in Franja} binary;


/*Función objetivo*/

/*Minimizar el número de pasajeros afectados por coincidencia de autobuses en la misma franja*/
minimize Impacto_Total:
    sum {a in Autobus, b in Autobus: a < b}
        pasajeros_coincidentes[a,b] *
        sum {i in Franja} coincide[a,b,i];


/*Restricciones */

/*Cada autobús tiene que estar asignado a una franja en algún taller*/
s.t. Asignacion_Unica {a in Autobus}:
    sum {i in Franja, j in Taller} asignacion[a,i,j] = 1;

/*Cada franja i en un taller j solo puede ser ocupada por un autobús como máximo y solo si dicha franja está disponible*/
s.t. Capacidad_y_Disponibilidad {i in Franja, j in Taller}:
    sum {a in Autobus} asignacion[a,i,j] <= disponible[i,j];


/*Cota superior: Si el autobús a no usa la franja i, la coincidencia no puede ser 1*/
s.t. Coincide_Cota_A {a in Autobus, b in Autobus, i in Franja}:
    coincide[a,b,i] <= sum {j in Taller} asignacion[a,i,j];

/*Cota superior: Si el autobús b no usa la franja i, tampoco puede haber coincidencia*/
s.t. Coincide_Cota_B {a in Autobus, b in Autobus, i in Franja}:
    coincide[a,b,i] <= sum {j in Taller} asignacion[b,i,j];

/*Cota inferior: Si los dos usan la franja i, obliga a coincide[a,b,i] = 1*/
s.t. Coincide_Cota_Inferior {a in Autobus, b in Autobus, i in Franja}:
    coincide[a,b,i] >=
        sum {j in Taller} asignacion[a,i,j]
      + sum {j in Taller} asignacion[b,i,j]
      - 1;

end;