import os
import asyncio
from playwright.async_api import async_playwright
import requests

# 1. Configuración desde los Secrets de GitHub (Seguridad)
URL_LOGIN = "https://www.oxaam.com/login.php"
USER = os.environ.get("WEB_USER")
PASSWORD = os.environ.get("WEB_PASSWORD")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(texto):
    """Envía el texto extraído a su chat de Telegram"""
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
        # Lanzamos Chromium en modo headless
        browser = await p.chromium.launch(headless=True)
        # Añadimos un user_agent común para evitar bloqueos por parecer un bot básico
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Abriendo la web de Oxaam...")
        await page.goto(URL_LOGIN)
        await page.wait_for_load_state("networkidle")
        
        # --- INICIO DE SESIÓN ---
        print("Introduciendo credenciales...")
        # El input de usuario en Oxaam utiliza el atributo name="email"
        await page.fill("input[name='email']", USER)
        # El input de contraseña utiliza el atributo name='password'
        await page.fill("input[name='password']", PASSWORD)
        
        print("Pulsando el botón de iniciar sesión...")
        # Hacemos clic en el botón de entrar
        await page.click("button[type='submit']")
        
        # Esperamos a que la navegación termine tras el login y cargue el panel principal
        await page.wait_for_load_state("networkidle")
        
        # --- EXTRACCIÓN DEL TEXTO EN EL DASHBOARD ---
        print("Extrayendo información...")
        
        # NOTA: Como no sé exactamente qué texto quiere extraer de su panel privado,
        # aquí usamos page.locator().inner_text() apuntando al elemento concreto.
        # De momento, el bot extraerá todo el texto visible del cuerpo de la página tras loguearse.
        # Puede cambiar 'body' por el selector específico (ej: '.clase-del-texto' o '#id-del-texto') cuando lo sepa.
        elemento_texto = await page.locator("body").inner_text()
        
        # Filtramos o formateamos el texto para enviarlo limpio
        texto_recortado = elemento_texto.strip()[:1000] # Limitamos a los primeros 1000 caracteres por seguridad de espacio
        texto_final = f"**Informe Diario de Oxaam:**\n\n{texto_recortado}"
        
        # --- ENVÍO ---
        enviar_telegram(texto_final)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
