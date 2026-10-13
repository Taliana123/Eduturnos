# Autenticación segura de EDUTURNOS

## Regla institucional para personal

Docentes, Coordinadores y Rectoría deben usar un correo que termine exactamente en `@jjfh.edu.co`.
Además, su cuenta queda ligada a:

- persona registrada institucionalmente;
- sede asignada;
- código institucional individual asignado por el colegio.

El código se almacena como hash, nunca como texto plano.

## Inicio de sesión

El usuario no selecciona un rol. EDUTURNOS busca la cuenta en MySQL y obtiene el rol real desde `usuarios -> roles`.

Para personal, el acceso exige correo institucional + contraseña + código institucional + sede correcta.
Para estudiantes y acudientes, el acceso usa sus credenciales de cuenta y el rol almacenado en MySQL.

## Asignación inicial de códigos de personal

La asignación la hace el colegio una sola vez por persona con:

```powershell
python tools/migrations/preparar_codigo_personal.py
```

El script busca al docente o directivo existente, asocia la sede y guarda un hash del código.
Después, el usuario puede registrarse e iniciar sesión sin que alguien tenga que aprobarlo manualmente cada vez.
