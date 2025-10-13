## Pruebas unitarias al servicio sire

Crear un archivo credentials.py dentro de la carpeta test ,contenido (ejemplo):
```
RUC = "204564562211"
USER = "76456654"
PASSWORD = "clavesol"
```
Para ejecutar todos los test:
```
python3 -m unittest discover service/test/
```
Para ejecutar cada test (archivo) individualmente , ejemplo:
```
python3 -m unittest service/test/test_sire.py 
```
*