# SL-UNLA-LAB-2025-GRUPO-9
Trabajo practico grupal del seminario grupo 9.
Integrantes:
Kevin Lesama Soto
Nahuel Garcia
Orion Quimey Jaime Adell
Agustin Nicolas Mancini

arc
app.py
databse.bd
database.py
models.py
requierements.txt

comandos utiles de git:
git init = Sirve para iniciar un git. No lo usen ya esta hecho.
git add = Sirve para añadir los archivos que se incluiran en los commits. Tambien ya esta hecho asi que no lo usen.
git commit -m "nombreDeCommit sin comillas" = Crea el commit y le asignas el nombre.
git remote add origin "url del repo sin las comillas"= Linkeea un proyecto con su repositorio de github. No lo usen ya lo hicimos.
git push -u = Sirve para subir tu commit a github.
git pull = Sirve para bajarse todos los cambios que hicimos en nuestro proyecto. Si yo agrego algo ustedes usan git pull para bajarse lo que hice yo.

Si les sale un error al activar el entorno virtual que dice que la ejecucion de scripts esta deshabilitada tienen 2 opciones, habilitarla temporalmente o permanente.

Para temporal buscan en windows "powershell" y lo abren como administrador.
Pegan este comando: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
le dan a si a todo
Con esto lo habilitan una vez, cuando cierren la terminal de powershell se les va a deshabilitar.

Para hacerlo permanente, hacen lo mismo pero en vez de ese comando pongan este:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
le dan a si a todo y listo.

Para activar el entorno deben ir a la carpeta de .venv PERO DESDE LA CONSOLA.
escriban en la consola "cd .\.venv\Scripts" le dan enter y despues ponen ".\activate"
RECUERDEN QUE TIENEN QUE SALIR DESPUES NO SE OLVIDEN O LOS MATO.
Para volver a la carpeta raiz del proyecto hacen asi "cd ..\..\"
no rompan nada porfavor 🙏🏻🙏🏻