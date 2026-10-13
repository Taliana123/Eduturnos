# Correo de recuperación de EDUTURNOS

## Cómo funciona para los usuarios

El usuario final solo escribe el correo que tiene registrado en EDUTURNOS. No debe conocer ni introducir:

- servidor SMTP;
- puerto;
- usuario SMTP;
- contraseña de aplicación;
- `PUBLIC_BASE_URL`;
- ninguna variable de `.env`.

EDUTURNOS busca ese correo en la tabla `usuarios`, genera un código de recuperación de 6 dígitos y envía el mensaje automáticamente a la dirección almacenada en la cuenta.

## Configuración única del servidor

En el servidor donde está publicado EDUTURNOS se configura una sola cuenta institucional de salida en `.env`:

```text
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=cuenta-institucional@ejemplo.com
MAIL_PASSWORD=CONTRASENA_DE_APLICACION
MAIL_DEFAULT_SENDER=cuenta-institucional@ejemplo.com
MAIL_USE_TLS=1
PUBLIC_BASE_URL=https://eduturnos.tudominio.edu.co
```

Estas variables son internas del servidor. Nunca se muestran al usuario final.

## Destinatarios

No existe un único correo receptor. Cada solicitud se envía al correo que pertenece a la cuenta que está recuperando acceso. Por ejemplo:

```text
estudiante@gmail.com        -> recibe su propio código
padre@correo.com            -> recibe su propio código
docente@jjfh.edu.co         -> recibe su propio código
coordinador@jjfh.edu.co    -> recibe su propio código
rector@jjfh.edu.co         -> recibe su propio código
```

El remitente institucional puede ser uno solo; los destinatarios pueden ser todos los usuarios registrados.

## Requisito inevitable

Para enviar correo real hace falta una identidad de envío autorizada por el proveedor de correo. Esa autorización se configura una sola vez en el servidor. No es un dato que cada estudiante, acudiente, docente o directivo deba proporcionar.
