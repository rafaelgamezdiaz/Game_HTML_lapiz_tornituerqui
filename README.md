# Ejecución Local del Proyecto

Para visualizar el juego 3D en el navegador es necesario utilizar un servidor HTTP local debido a las restricciones de seguridad (CORS) que impiden cargar modelos 3D (`.glb`), texturas y scripts mediante el protocolo `file://`.

## Requisitos

- Python 3.x o Node.js instalado en el sistema.
- Navegador web moderno compatible con WebGL (Chrome, Edge, Firefox).

---

## Opciones para Iniciar el Servidor Local

### Opción 1: Usando Python (Recomendada)

1. Abrir una terminal o consola de comandos en la raíz del proyecto (`e:\Kairos\lapiz_y_tornituerqui`).
2. Ejecutar el siguiente comando (usando el puerto `8080` o `8888`):

```bash
python -m http.server 8080
```

> **Nota si aparece `PermissionError: [WinError 10013]`**:
> Este error ocurre cuando el puerto ya está ocupado por otra aplicación o bloqueado por Windows. Cambie el puerto o enlace explícitamente a `127.0.0.1`:
> ```bash
> python -m http.server 8080 --bind 127.0.0.1
> ```
> O alternativamente probar con `8888`:
> ```bash
> python -m http.server 8888 --bind 127.0.0.1
> ```

3. Abrir el navegador e ingresar a la URL correspondiente:

```
http://localhost:8080/
```

---

### Opción 2: Usando Node.js / npx

1. Abrir la terminal en la raíz del proyecto.
2. Ejecutar:

```bash
npx serve .
```

o bien:

```bash
npx http-server -p 8000
```

3. Acceder a la URL indicada en la consola (usualmente `http://localhost:3000/` o `http://localhost:8000/`).

---

### Opción 3: Extensión Live Server (VS Code / Antigravity IDE)

1. Instalar la extensión **Live Server** en el editor.
2. Hacer clic derecho sobre el archivo `index.html`.
3. Seleccionar **Open with Live Server**.
