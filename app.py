import io
import requests
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# --- SCHRIFTARTEN BIBLIOTHEK ---
FONTS = {
    "arial": "default",
    "roboto_bold": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf",
    "roboto_reg": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
    "open_bold": "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Bold.ttf",
    "open_reg": "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf",
    "marker": "https://github.com/google/fonts/raw/main/apache/permanentmarker/PermanentMarker-Regular.ttf",
    "handwriting": "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat-Bold.ttf",
    "elegant": "https://github.com/google/fonts/raw/main/ofl/greatvibes/GreatVibes-Regular.ttf",
    "impact": "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald-Bold.ttf"
}

def get_font(font_name, size):
    if font_name not in FONTS or FONTS[font_name] == "default":
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
            
    font_url = FONTS[font_name]
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(font_url, headers=headers)
        response.raise_for_status()
        return ImageFont.truetype(io.BytesIO(response.content), size)
    except Exception as e:
        print(f"Font Error: {e}")
        return ImageFont.load_default()

@app.route('/generate')
def generate():
    raw_text = request.args.get('text', 'Vorschau')
    image_url = request.args.get('bg', '')
    font_name = request.args.get('font', 'roboto_bold')
    casing = request.args.get('case', 'title')

    # Text-Formatierung
    if casing == 'upper':
        text = raw_text.upper()
    elif casing == 'lower':
        text = raw_text.lower()
    elif casing == 'title':
        text = raw_text.title()
    else:
        text = raw_text

    try:
        # Design Parameter
        x_pos = int(request.args.get('x', 50))
        y_pos = int(request.args.get('y', 50))
        size = int(request.args.get('size', 60))
        hex_color = request.args.get('color', '000000')
        color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Neue Parameter für die Box
        show_box = request.args.get('box', 'false').lower() == 'true'
        box_hex_color = request.args.get('box_color', 'ffffff')
        box_color = tuple(int(box_hex_color[i:i+2], 16) for i in (0, 2, 4))
        box_padding = int(request.args.get('box_padding', 10)) # Polsterung um den Text
        
    except Exception as e:
        print(f"Parameter parse error: {e}")
        x_pos, y_pos, size = 50, 50, 60
        color = (0, 0, 0)
        show_box = False
        box_color = (255, 255, 255)
        box_padding = 10

    if not image_url:
        return "Fehler: Keine Bild-URL (bg) angegeben.", 400

    try:
        # Bild laden
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        img = Image.open(response.raw).convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        # Schriftart laden
        font = get_font(font_name, size)
            
        # Textgröße messen für die Box
        # textbbox liefert (left, top, right, bottom)
        bbox = draw.textbbox((x_pos, y_pos), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Box zeichnen, wenn aktiviert
        if show_box:
            box_x0 = x_pos - box_padding
            box_y0 = y_pos - box_padding
            box_x1 = x_pos + text_width + box_padding
            box_y1 = y_pos + text_height + box_padding
            
            draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=box_color)

        # Text schreiben
        draw.text((x_pos, y_pos), text, font=font, fill=color)

        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return f"Error generating image: {str(e)}", 500

if __name__ == '__main__':
    app.run()
