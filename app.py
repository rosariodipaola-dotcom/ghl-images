import io
import requests
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Fallback Schriftart laden
try:
    # Wir nutzen eine Standardschriftart, die Linux-Server oft haben
    # Alternativ könntest du eine .ttf Datei mit hochladen
    DEFAULT_FONT = "arial.ttf" 
except:
    DEFAULT_FONT = None

@app.route('/generate')
def generate():
    # 1. Parameter aus der URL holen
    text = request.args.get('text', 'Vorschau')
    image_url = request.args.get('bg', '') # URL des Hintergrundbildes
    
    # Koordinaten & Design
    try:
        x_pos = int(request.args.get('x', 50))
        y_pos = int(request.args.get('y', 50))
        size = int(request.args.get('size', 60))
        # Farbe kommt als Hex (z.B. 000000), muss in RGB umgewandelt werden
        hex_color = request.args.get('color', '000000')
        color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except:
        # Fallback Werte falls was falsch eingegeben ist
        x_pos, y_pos, size = 50, 50, 60
        color = (0, 0, 0)

    if not image_url:
        return "Fehler: Keine Bild-URL (bg) angegeben.", 400

    try:
        # 2. Hintergrundbild von GHL (oder woanders) laden
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        img = Image.open(response.raw).convert("RGBA")
        
        draw = ImageDraw.Draw(img)
        
        # 3. Schriftart
        try:
            # Versuchen Arial zu laden, sonst Default
            font = ImageFont.truetype("DejaVuSans.ttf", size) 
        except:
            font = ImageFont.load_default()
            
        # 4. Text schreiben an der gewünschten Position
        draw.text((x_pos, y_pos), text, font=font, fill=color)

        # 5. Bild ausgeben
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return f"Fehler beim Bild generieren: {str(e)}", 500

if __name__ == '__main__':
    app.run()
