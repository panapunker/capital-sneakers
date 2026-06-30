IA_CONTINUIDAD.md
CAPITAL SNEAKERS ERP
PROPÓSITO

Este proyecto desarrolla un ERP comercial completo para la empresa Capital Sneakers utilizando Django.

El proyecto será construido por diferentes modelos de IA (Claude, ChatGPT y otros), por lo tanto todas las modificaciones deben mantener compatibilidad total entre bloques.

Nunca debe asumirse que el proyecto comienza desde cero.

Siempre debe continuarse la arquitectura existente.

REGLAS OBLIGATORIAS

Nunca cambiar:

nombres de carpetas
nombres de apps
nombres de modelos
nombres de vistas
nombres de funciones
nombres de urls
nombres de templates
nombres de archivos

No eliminar código existente.

No reemplazar archivos completos si basta con agregar código.

Cuando un archivo necesite cambios, indicar exactamente qué agregar o modificar.

Todo debe integrarse con el proyecto existente.

FRAMEWORK

Python

Django

Bootstrap 5

JavaScript Vanilla

SQLite durante desarrollo

PostgreSQL en Render

Cloudflare R2 para imágenes.

ESTRUCTURA DEL PROYECTO
capital_sneakers/

accounts/

clientes/

catalogo/

inventario/

pedidos/

dashboard/

carrito/

config/

templates/

static/

Esta estructura nunca debe modificarse.

APPS
accounts

Responsable de:

Login administrador
Login cliente
Logout
Roles
Usuarios
dashboard

Responsable de:

Dashboard administrador.

Dashboard cliente.

Métricas.

Accesos rápidos.

Notificaciones.

catalogo

Responsable de:

Productos

Categorías

Marcas

Géneros

Variantes

Imágenes

inventario

Responsable de:

Entradas

Salidas

Ajustes

Existencias

Movimientos

pedidos

Responsable de:

Pedidos

Detalle pedidos

Estados

Historial

carrito

Responsable de:

Carrito

Confirmación

Proceso de compra

clientes

Responsable de:

Información del cliente

Historial

Datos comerciales

config

Responsable de:

Configuraciones futuras.

No contiene lógica del negocio.

PRODUCTOS

Los productos NO tendrán una tabla independiente para tallas.

Las tallas dependerán del género seleccionado.

Al crear un producto solo existirán estos campos:

Nombre

Marca

Referencia

Precio compra

Precio venta

Género

Imagen

GÉNEROS

Dama

Caballero

Niño

Ambos

TALLAS

Si se selecciona:

Dama

mostrar:

36

37

38

39

Caballero

mostrar:

40

41

42

43

44

45

Niño

mostrar:

28

30

32

33

34

35

Ambos

mostrar:

36

37

38

39

40

41

42

43

44

45

STOCK

Al crear un producto aparecerán automáticamente las tallas correspondientes.

Cada talla tendrá una casilla para ingresar la cantidad.

Ejemplo:

36 → 5

37 → 8

38 → 12

39 → 4

Abajo deberá calcularse automáticamente:

Stock total:

29 unidades

El usuario nunca escribirá el stock total.

Siempre será calculado automáticamente.

PERMISOS

Administrador

Acceso completo.

Cliente

Solo:

Catálogo

Carrito

Pedidos propios

Dashboard propio

Perfil

DISEÑO

Toda la interfaz debe ser moderna.

No utilizar la apariencia clásica de Django Admin.

Diseño tipo dashboard moderno.

Sidebar izquierdo.

Header superior.

Tarjetas.

Tablas modernas.

Colores neutros.

Bootstrap 5.

Responsive.

DESPLIEGUE

Desarrollo:

SQLite

Producción:

Render

PostgreSQL

Cloudflare R2

WhiteNoise

MIGRACIONES

No solicitar ejecutar:

makemigrations

migrate

runserver

hasta finalizar completamente el bloque solicitado.

CONTINUIDAD

Cada bloque desarrollado debe quedar preparado para que otra IA continúe inmediatamente.

Nunca asumir que el proyecto termina en el bloque actual.

Debe mantenerse compatibilidad absoluta con bloques futuros.

ORDEN DE DESARROLLO

Actualmente el proyecto se desarrolla en el siguiente orden:

✅ Proyecto Django

✅ Accounts

✅ Dashboard

⬜ Catálogo

⬜ Inventario

⬜ Clientes

⬜ Pedidos

⬜ Carrito

⬜ Reportes

⬜ Notificaciones

⬜ Contabilidad

⬜ Devoluciones

⬜ Código de barras

⬜ Cloudflare R2

⬜ Render

REGLA FINAL

Si existe alguna duda entre crear algo nuevo o reutilizar la arquitectura existente, siempre debe reutilizarse la arquitectura existente.

El objetivo es obtener un único proyecto integrado y coherente.