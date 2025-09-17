from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import urllib.parse

app = Flask(__name__)

# Configurazione del tuo bot Telegram
TELEGRAM_BOT_TOKEN = "8021416887:AAEHXKzUCMKIcNV4GVy9IK03neIDzvaPuhw"
TELEGRAM_CHAT_ID = "5920021133"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

@app.route('/', methods=['GET'])
def home():
    """Pagina home del webhook intermedio"""
    return f"""
    <h1>🚀 TradingView → Telegram Webhook Intermedio</h1>
    <p><strong>Status:</strong> Attivo</p>
    <p><strong>Bot Telegram:</strong> @ema_signals_Daniel_bot</p>
    <p><strong>Chat ID:</strong> {TELEGRAM_CHAT_ID}</p>
    <p><strong>Endpoint TradingView:</strong> /tradingview-alert</p>
    <p><strong>Test Endpoint:</strong> /test</p>
    <p><strong>Ultimo aggiornamento:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>📋 Come Usare:</h2>
    <p>Nel tuo alert TradingView, usa questo URL come webhook:</p>
    <code>https://[URL-DEL-TUO-WEBHOOK]/tradingview-alert</code>
    
    <h3>Messaggio di esempio per TradingView:</h3>
    <pre>{{{"ticker"}}}: {{{"strategy.order.action"}}}<br>Prezzo: {{{"close"}}}<br>Data: {{{"time"}}}</pre>
    """

@app.route('/tradingview-alert', methods=['POST'])
def handle_tradingview_alert():
    """
    Riceve l'alert da TradingView e lo invia a Telegram in formato JSON
    """
    try:
        # Log della richiesta ricevuta
        print(f"🔔 Alert ricevuto da TradingView: {datetime.now()}")
        
        # Ottieni i dati dall'alert
        if request.is_json:
            alert_data = request.get_json()
            message_text = alert_data.get('text', 'Alert da TradingView')
        else:
            # TradingView invia i dati come form-data o query parameters
            message_text = request.form.get('text') or request.args.get('text') or 'Alert da TradingView'
        
        print(f"📝 Messaggio ricevuto: {message_text}")
        
        # Formatta il messaggio per Telegram con Markdown
        formatted_message = f"""*🚨 TradingView Alert 🚨*

{message_text}

_Orario: {datetime.now().strftime('%H:%M:%S')}_"""
        
        # Prepara i dati JSON per Telegram
        telegram_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": formatted_message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        # Invia il messaggio a Telegram usando il formato JSON
        response = requests.post(
            TELEGRAM_API_URL,
            json=telegram_payload,  # Invia come JSON
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Messaggio inviato con successo a Telegram")
            return jsonify({
                "status": "success",
                "message": "Alert inviato a Telegram",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            print(f"❌ Errore Telegram API: {response.status_code} - {response.text}")
            return jsonify({
                "status": "error",
                "message": f"Errore Telegram: {response.status_code}",
                "details": response.text
            }), 500
            
    except Exception as e:
        print(f"❌ Errore nel processare l'alert: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Errore interno del server",
            "details": str(e)
        }), 500

@app.route('/test', methods=['GET', 'POST'])
def test_webhook():
    """
    Endpoint per testare il funzionamento del webhook
    """
    try:
        test_message = f"""*🧪 TEST WEBHOOK INTERMEDIO*

✅ Webhook funzionante
✅ Connessione Telegram OK
✅ Formato JSON supportato
⏰ Test: {datetime.now().strftime('%H:%M:%S')}

🎯 Il sistema è pronto per ricevere alert da TradingView!"""
        
        # Invia messaggio di test
        telegram_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": test_message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(
            TELEGRAM_API_URL,
            json=telegram_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "message": "Test completato! Controlla Telegram.",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Errore nel test",
                "telegram_response": response.text
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check per il monitoraggio"""
    return jsonify({
        "status": "healthy",
        "service": "TradingView-Telegram Webhook",
        "timestamp": datetime.now().isoformat(),
        "telegram_bot": "@ema_signals_Daniel_bot",
        "chat_id": TELEGRAM_CHAT_ID
    }), 200

# Gestione errori
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint non trovato"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Errore interno del server"}), 500

if __name__ == '__main__':
    print("🚀 Avvio Webhook Intermedio TradingView → Telegram")
    print(f"🤖 Bot: @ema_signals_Daniel_bot")
    print(f"📨 Chat destinazione: {TELEGRAM_CHAT_ID}")
    print(f"🔗 Endpoint principale: /tradingview-alert")
    print(f"🧪 Endpoint test: /test")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
