import os
import asyncio
from playwright.async_api import async_playwright
import requests

# Configuración desde los Secrets de GitHub
URL_LOGIN = "https://www.oxaam.com/login.php"
USER = os.environ.get("WEB_USER")
PASSWORD = os.environ.get("WEB_PASSWORD")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(texto):
    """Envía las credenciales extraídas a su chat de Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("¡Mensaje enviado a Telegram correctamente!")
        else:
            print(f"Error al enviar a Telegram: {response.text}")
    except Exception as e:
        print(f"Error en la petición de Telegram: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("1. Abriendo la web de Oxaam...")
        await page.goto(URL_LOGIN)
        await page.wait_for_load_state("networkidle")
        
        print("2. Introduciendo credenciales de acceso...")
        await page.fill("input[name='email']", USER)
        await page.fill("input[name='password']", PASSWORD)
        
        print("3. Pulsando el botón de iniciar sesión...")
        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")
        
        # --- INICIO DE LA RUTA DE CLICS ---
        
        print("4. Buscando y pulsando en 'Browse Free Services'...")
        # Busca cualquier elemento que contenga exactamente ese texto y hace clic
        await page.get_by_text("Browse Free Services", exact=False).first.click()
        await page.wait_for_load_state("networkidle")
        
        print("5. Buscando y pulsando en 'Click here for more free services'...")
        await page.get_by_text("Click here for more free services", exact=False).first.click()
        await page.wait_for_load_state("networkidle")
        
        print("6. Buscando y pulsando en 'Apliv Music'...")
        await page.get_by_text("Apliv Music", exact=False).first.click()
        await page.wait_for_load_state("networkidle")
        
        # --- EXTRACCIÓN DE LOS DATOS ---
        print("7. Extrayendo las credenciales de Apliv Music...")
        
        # Esperamos un momento breve para asegurar que carguen los datos en pantalla
        await page.wait_for_timeout(2000)
        
        # Copiamos el texto de la zona final. Como no conocemos las etiquetas exactas todavía,
        # leemos el texto general de la sección activa para buscar el correo y contraseña.
        texto_pantalla = await page.locator("body").inner_text()
        
        # Preparamos el mensaje para Telegram
        # (Si la pantalla tiene mucho texto sobrante, luego podemos recortarlo, pero así nos aseguramos de capturarlo)
        mensaje_telegram = f"**🔑 Credenciales Diarias de Apliv Music:**\n\n{texto_pantalla.strip()[:1500]}"
        
        # --- ENVÍO ---
        enviar_telegram(mensaje_telegram)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
