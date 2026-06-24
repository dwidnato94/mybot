import os
import asyncio
from playwright.async_api import async_playwright
import requests

URL_LOGIN = "https://www.oxaam.com/login.php"
USER = os.environ.get("WEB_USER") or ""
PASSWORD = os.environ.get("WEB_PASSWORD") or ""
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

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
        await page.locator("input[type='email'], input[name='email'], input[name='username'], input[type='text']").first.fill(USER)
        await page.locator("input[type='password'], input[name='password']").first.fill(PASSWORD)
        
        print("3. Pulsando el botón de iniciar sesión...")
        await page.locator("button[type='submit'], input[type='submit'], button:has-text('Login')").first.click()
        await page.wait_for_load_state("networkidle")
        
        print("4. Buscando y pulsando en 'Browse Free Services'...")
        await page.get_by_text("Browse Free Services", exact=False).first.click()
        await page.wait_for_load_state("networkidle")
        
        print("5. Buscando y pulsando en 'Click here for more free services'...")
        await page.get_by_text("Click here for more free services", exact=False).first.click()
        await page.wait_for_load_state("networkidle")
        
        print("6. Buscando y pulsando en 'Apliv Music'...")
        # Hace clic en el título que se ve en su captura
        await page.get_by_text("Apliv Music", exact=False).first.click()
        await page.wait_for_load_state("networkidle")
        
        print("7. Extrayendo las credenciales...")
        # Esperamos 3 segundos para dar tiempo a que aparezca la caja gris
        await page.wait_for_timeout(3000)
        
        # Leemos todo el texto de la web
        texto_pantalla = await page.locator("body").inner_text()
        
        # Filtramos mágicamente solo las líneas que nos interesan
        lineas = texto_pantalla.split('\n')
        credenciales = []
        for linea in lineas:
            if "Email ->" in linea or "Password ->" in linea:
                credenciales.append(linea.strip())
        
        # Construimos el mensaje final limpio para Telegram
        if credenciales:
            texto_limpio = "\n".join(credenciales)
            mensaje_telegram = f"**🔑 Credenciales Diarias de Apliv Music:**\n\n`{texto_limpio}`"
        else:
            mensaje_telegram = "⚠️ **Error:** El bot llegó a la página final, pero no encontró las palabras 'Email ->' o 'Password ->'."
        
        print("8. Enviando mensaje a Telegram...")
        enviar_telegram(mensaje_telegram)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
