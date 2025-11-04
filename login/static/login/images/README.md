# Imágenes del Login

## Cómo agregar tu imagen

1. **Coloca tu imagen** en este directorio: `login/static/login/images/`

2. **Nombres sugeridos:**
   - `ilustracion-login.png`
   - `ilustracion-login.jpg`
   - `ilustracion-login.svg`

3. **Si usas otro nombre**, actualiza el template `login/templates/login/login.html`:
   ```html
   <img src="{% static 'login/images/TU_IMAGEN.png' %}" alt="Ilustración Login" class="login-image">
   ```

## Formatos soportados
- PNG (recomendado para ilustraciones)
- JPG/JPEG (para fotos)
- SVG (vectoriales)
- WebP (moderno, buena compresión)

## Tamaño recomendado
- Ancho mínimo: 600px
- Ancho ideal: 800-1200px
- Relación de aspecto: Cuadrada o vertical (1:1 o 4:3)

