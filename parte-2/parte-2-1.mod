/*parte-2-1.mod*/

/*Conjuntos*/

/*Conjunto de autobuses*/
set Autobus;
/*Conjunto de franjas del taller*/
set Franja;

/*Parámetros*/

/*Distancia del autobús i al taller*/
param distancia {i in Autobus};
/*Pasajeros del autobús i*/
param pasajeros {i in Autobus};
/*Coste por kilómetro si el autobús se asigna a franja*/
param coste_asignacion;
/*Penalización por pasajero si no se asigna a franja*/
param penalizacion_no_asignacion;
/*Asignación máxima de autobuses*/
param max_asignaciones_autobus;
/*Autobuses máximos por franja*/
param max_autobuses_franja;


/*Variables de decisión*/
var asignacion{i in Autobus, j in Franja} binary;

/*Función objetivo*/

/*Coste por asignación + penalización por no asignación*/
minimize Perdida: sum{i in Autobus, j in Franja} coste_asignacion * distancia[i] * asignacion[i,j] + sum{i in Autobus} penalizacion_no_asignacion * pasajeros[i] * (1 - sum{j in Franja} asignacion[i,j]);

/*Restricciones*/

/*Cada autobús se asigna a lo sumo a una franja*/
s.t. Asignacion_Autobus{i in Autobus}:  sum{j in Franja} asignacion[i,j] <= max_asignaciones_autobus;

/*Cada franja puede atender como máximo a un autobús*/
s.t. Capacidad_Franja{j in Franja}:  sum{i in Autobus} asignacion[i,j] <= max_autobuses_franja;

end;
