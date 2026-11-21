import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.conf import settings
from listings.models import Listing

class Command(BaseCommand):
    help = 'Generates realistic, high-quality illustrative product images for all campus marketplace listings.'

    def handle(self, *args, **options):
        media_listings = Path(settings.MEDIA_ROOT) / 'listings'
        media_listings.mkdir(parents=True, exist_ok=True)
        self.stdout.write("Generating high-quality product images in media/listings/...")

        # 1. Anker USB-C Hub
        self.generate_usbc_hub(media_listings / 'usb-c_hub.jpg')
        # 2. Casio Scientific Calculator
        self.generate_calculator(media_listings / 'casio_calculator.jpg')
        # 3. Stewart Calculus Textbook
        self.generate_calculus_book(media_listings / 'calculus_book.jpg')
        # 4. Campus Bicycle
        self.generate_bicycle(media_listings / 'campus_bicycle.jpg')
        # 5. Badminton Rackets & Shuttles
        self.generate_badminton(media_listings / 'badminton_set.jpg')
        # 6. Study Desk & Lamp
        self.generate_study_desk(media_listings / 'study_desk_set.jpg')
        # 7. Laundry Hamper & Steam Iron
        self.generate_hostel_essentials(media_listings / 'hostel_essentials.jpg')
        # 8. Molecular Model Kit
        self.generate_molecular_kit(media_listings / 'molecular_model_kit.jpg')

        # Update database listings to ensure they point to these files
        image_mapping = {
            'Anker USB-C 7-in-1 Hub': 'listings/usb-c_hub.jpg',
            'Casio fx-991EX': 'listings/casio_calculator.jpg',
            'Stewart Calculus': 'listings/calculus_book.jpg',
            'Giant Boulder Mountain Bike': 'listings/campus_bicycle.jpg',
            'Yonex Nanoray Badminton': 'listings/badminton_set.jpg',
            'Foldable Study Desk': 'listings/study_desk_set.jpg',
            'Collapsible Laundry Hamper': 'listings/hostel_essentials.jpg',
            'Organic Chemistry Molecular': 'listings/molecular_model_kit.jpg',
        }

        updated = 0
        for listing in Listing.objects.all():
            for key, filename in image_mapping.items():
                if key.lower() in listing.title.lower():
                    listing.image.name = filename
                    listing.save(update_fields=['image'])
                    updated += 1
                    break

        self.stdout.write(self.style.SUCCESS(f"Successfully generated 8 realistic product images and synced {updated} listings!"))

    def create_gradient_bg(self, w, h, top_color, bottom_color):
        base = Image.new('RGB', (w, h), top_color)
        draw = ImageDraw.Draw(base)
        for y in range(h):
            ratio = y / h
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        return base

    def generate_usbc_hub(self, out_path):
        w, h = 800, 600
        img = self.create_gradient_bg(w, h, (30, 36, 44), (18, 22, 28))
        draw = ImageDraw.Draw(img)

        # Hub Body (Space Gray Metallic Aluminum)
        bx, by, bw, bh = 220, 240, 360, 150
        # Shadow
        draw.rounded_rectangle([bx + 8, by + 12, bx + bw + 8, by + bh + 12], radius=20, fill=(10, 12, 16))
        # Aluminum Body
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=20, fill=(70, 78, 88), outline=(110, 120, 132), width=2)
        # Inner metallic highlight
        draw.rounded_rectangle([bx + 4, by + 4, bx + bw - 4, by + 30], radius=16, fill=(85, 95, 106))

        # Brand text
        draw.text((bx + 30, by + 25), "ANKER", fill=(180, 190, 202))
        draw.text((bx + 30, by + 48), "7-in-1 USB-C Hub  |  100W PD & 4K HDMI", fill=(130, 142, 155))

        # LED Indicator
        draw.ellipse([bx + bw - 35, by + 30, bx + bw - 25, by + 40], fill=(46, 204, 113), outline=(100, 255, 150))

        # Front Ports (USB 3.0 Blue Ports)
        for i, px in enumerate([bx + 35, bx + 115, bx + 195]):
            # Port cutout
            draw.rectangle([px, by + 85, px + 60, by + 125], fill=(25, 28, 33), outline=(90, 100, 112))
            # USB 3.0 Blue Tongue
            draw.rectangle([px + 8, by + 90, px + 52, by + 102], fill=(0, 122, 255))
            # Pins
            for pin in range(4):
                draw.line([(px + 14 + pin * 10, by + 92), (px + 18 + pin * 10, by + 92)], fill=(255, 215, 0), width=2)

        # SD / TF Slots
        draw.rectangle([bx + 280, by + 88, bx + 335, by + 98], fill=(20, 22, 26), outline=(90, 100, 112))
        draw.rectangle([bx + 280, by + 110, bx + 325, by + 118], fill=(20, 22, 26), outline=(90, 100, 112))
        draw.text((bx + 285, by + 125), "SD / TF", fill=(140, 150, 165))

        # Integrated Braided Cable
        cable_points = [(bx, by + 75), (bx - 50, by + 75), (bx - 90, by + 120), (bx - 80, by + 190), (bx - 40, by + 230)]
        draw.line(cable_points, fill=(45, 50, 58), width=16)
        draw.line(cable_points, fill=(65, 72, 82), width=10)

        # USB-C Connector head
        cx, cy = bx - 40, by + 230
        draw.rounded_rectangle([cx - 15, cy - 8, cx + 55, cy + 24], radius=6, fill=(75, 83, 94), outline=(120, 130, 145), width=2)
        # USB-C Type-C tip
        draw.rounded_rectangle([cx + 55, cy - 4, cx + 80, cy + 20], radius=8, fill=(160, 170, 182), outline=(210, 220, 230))

        # Title Card Footer Badge
        draw.rounded_rectangle([50, 50, 280, 95], radius=12, fill=(40, 48, 58, 200), outline=(70, 80, 95))
        draw.text((65, 65), "ELECTRONICS", fill=(46, 204, 113))
        img.save(out_path, format='JPEG', quality=92)

    def generate_calculator(self, out_path):
        w, h = 800, 600
        img = self.create_gradient_bg(w, h, (38, 48, 42), (20, 28, 24))
        draw = ImageDraw.Draw(img)

        # Calculator Case
        cx, cy, cw, ch = 260, 80, 280, 450
        # Shadow
        draw.rounded_rectangle([cx + 10, cy + 14, cx + cw + 10, cy + ch + 14], radius=24, fill=(12, 16, 14))
        # Body
        draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=24, fill=(35, 40, 45), outline=(75, 85, 95), width=2)

        # Brand header
        draw.text((cx + 25, cy + 22), "CASIO", fill=(230, 235, 240))
        draw.text((cx + 25, cy + 40), "fx-991EX  CLASSWIZ", fill=(140, 155, 170))

        # Solar Panel
        draw.rectangle([cx + cw - 95, cy + 22, cx + cw - 25, cy + 48], fill=(60, 30, 30), outline=(90, 70, 70), width=1)
        for sx in range(cx + cw - 90, cx + cw - 25, 16):
            draw.line([(sx, cy + 22), (sx, cy + 48)], fill=(90, 50, 50))

        # LCD Display Screen
        sx, sy, sw, sh = cx + 20, cy + 60, cw - 40, 85
        draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=8, fill=(185, 205, 195), outline=(50, 60, 65), width=2)
        # Math calculation displayed
        draw.text((sx + 15, sy + 15), "int(sin(x), 0, pi)", fill=(20, 30, 25))
        draw.text((sx + sw - 60, sy + 45), "= 2.000", fill=(10, 20, 15))

        # Function Keys (Silver & Grey)
        rows_fn = 3
        cols_fn = 6
        for r in range(rows_fn):
            for c in range(cols_fn):
                kx = cx + 22 + c * 40
                ky = cy + 165 + r * 28
                draw.rounded_rectangle([kx, ky, kx + 32, ky + 20], radius=4, fill=(55, 62, 70), outline=(85, 95, 105))

        # Number Keypad
        num_keys = [
            ["7", "8", "9", "DEL", "AC"],
            ["4", "5", "6", "x", "/"],
            ["1", "2", "3", "+", "-"],
            ["0", ".", "x10", "ANS", "="]
        ]
        for r, row in enumerate(num_keys):
            for c, key in enumerate(row):
                kx = cx + 22 + c * 48
                ky = cy + 265 + r * 40
                kcol = (210, 80, 60) if key in ["DEL", "AC"] else ((70, 120, 190) if key == "=" else (240, 245, 250))
                tcol = (255, 255, 255) if key in ["DEL", "AC", "="] else (30, 35, 40)
                draw.rounded_rectangle([kx, ky, kx + 40, ky + 30], radius=6, fill=kcol, outline=(100, 110, 120))
                draw.text((kx + 12, ky + 8), key, fill=tcol)

        # Category Badge
        draw.rounded_rectangle([50, 50, 280, 95], radius=12, fill=(28, 40, 32, 200), outline=(46, 120, 70))
        draw.text((65, 65), "ENGINEERING MATH", fill=(46, 204, 113))
        img.save(out_path, format='JPEG', quality=92)

    def generate_calculus_book(self, out_path):
        w, h = 800, 600
        img = self.create_gradient_bg(w, h, (25, 45, 35), (15, 25, 20))
        draw = ImageDraw.Draw(img)

        # Book Cover (3D Isometric Perspective)
        bx, by, bw, bh = 240, 70, 320, 460
        # Book shadow & depth
        draw.polygon([(bx + bw, by + 15), (bx + bw + 35, by + 35), (bx + bw + 35, by + bh + 35), (bx + bw, by + bh)], fill=(12, 18, 14))
        # Pages block (side)
        draw.polygon([(bx + bw, by + 20), (bx + bw + 30, by + 35), (bx + bw + 30, by + bh + 25), (bx + bw, by + bh)], fill=(230, 225, 215), outline=(180, 175, 165))
        # Hardcover spine
        draw.polygon([(bx - 20, by + 20), (bx, by), (bx, by + bh), (bx - 20, by + bh + 20)], fill=(15, 65, 38))

        # Main Front Cover (Rich Forest Green)
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(23, 107, 58), outline=(50, 160, 95), width=2)
        # Golden Frame
        draw.rectangle([bx + 15, by + 15, bx + bw - 15, by + bh - 15], outline=(218, 165, 32), width=3)

        # Header Titles
        draw.text((bx + 35, by + 45), "STEWART", fill=(255, 255, 255))
        draw.text((bx + 35, by + 75), "CALCULUS", fill=(255, 215, 0))
        draw.text((bx + 35, by + 115), "EARLY TRANSCENDENTALS", fill=(210, 235, 220))
        draw.text((bx + 35, by + 140), "8th Edition  *  Metric Version", fill=(170, 205, 185))

        # Mathematical Surface Plot Graphic
        cx, cy = bx + bw // 2, by + 270
        for radius in range(90, 10, -15):
            draw.ellipse([cx - radius, cy - radius // 2, cx + radius, cy + radius // 2], outline=(100, 220, 150), width=2)
        for a in range(-60, 70, 20):
            draw.line([(cx + a, cy - 45), (cx - a, cy + 45)], fill=(180, 240, 200), width=1)

        # Author tag
        draw.rectangle([bx + 30, by + bh - 80, bx + bw - 30, by + bh - 35], fill=(16, 75, 40))
        draw.text((bx + 45, by + bh - 65), "JAMES STEWART", fill=(255, 255, 255))

        # Category Badge
        draw.rounded_rectangle([50, 50, 260, 95], radius=12, fill=(20, 50, 35, 200), outline=(46, 120, 70))
        draw.text((65, 65), "TEXTBOOKS", fill=(46, 204, 113))
        img.save(out_path, format='JPEG', quality=92)

    def generate_bicycle(self, out_path):
        w, h = 800, 600
        img = self.create_gradient_bg(w, h, (35, 45, 60), (18, 24, 32))
        draw = ImageDraw.Draw(img)

        # Ground Shadow
        draw.ellipse([140, 480, 660, 520], fill=(12, 16, 22))

        # Wheels (Rear left, Front right)
        r_wheel = (240, 390)
        f_wheel = (560, 390)
        radius = 95

        for center in [r_wheel, f_wheel]:
            # Tire
            draw.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius], outline=(30, 32, 36), width=16)
            # Rim
            draw.ellipse([center[0] - radius + 10, center[1] - radius + 10, center[0] + radius - 10, center[1] + radius - 10], outline=(190, 195, 205), width=4)
            # Hub
            draw.ellipse([center[0] - 12, center[1] - 12, center[0] + 12, center[1] + 12], fill=(150, 155, 165))
            # Spokes
            for deg in range(0, 360, 30):
                import math
                rad = math.radians(deg)
                x2 = center[0] + int((radius - 12) * math.cos(rad))
                y2 = center[1] + int((radius - 12) * math.sin(rad))
                draw.line([center, (x2, y2)], fill=(160, 170, 180), width=1)

        # Diamond Bike Frame (Emerald Green & Black)
        bottom_bracket = (380, 390)
        seat_post = (340, 260)
        head_tube = (510, 240)
        handlebar = (500, 190)

        # Frame tubes
        frame_color = (33, 160, 85)
        draw.line([r_wheel, bottom_bracket], fill=frame_color, width=9)
        draw.line([r_wheel, seat_post], fill=frame_color, width=8)
        draw.line([bottom_bracket, seat_post], fill=frame_color, width=10)
        draw.line([bottom_bracket, head_tube], fill=frame_color, width=11)
        draw.line([seat_post, head_tube], fill=frame_color, width=10)
        draw.line([f_wheel, head_tube], fill=(45, 50, 58), width=10)  # Front fork

        # Handlebars & Stem
        draw.line([head_tube, handlebar], fill=(160, 165, 175), width=8)
        draw.line([handlebar, (handlebar[0] - 30, handlebar[1] - 10)], fill=(30, 32, 35), width=10)
        # Front Commuter Basket
        draw.rectangle([handlebar[0] + 5, handlebar[1] - 15, handlebar[0] + 55, handlebar[1] + 25], outline=(170, 175, 185), width=3)

        # Seat / Saddle
        draw.line([seat_post, (seat_post[0] - 10, seat_post[1] - 35)], fill=(140, 145, 155), width=7)
        draw.polygon([(seat_post[0] - 40, seat_post[1] - 35), (seat_post[0] + 20, seat_post[1] - 35), (seat_post[0] - 10, seat_post[1] - 45)], fill=(25, 28, 32))

        # Pedals & Chain Gear
        draw.ellipse([bottom_bracket[0] - 22, bottom_bracket[1] - 22, bottom_bracket[0] + 22, bottom_bracket[1] + 22], fill=(180, 185, 195), outline=(50, 55, 60))
        draw.line([bottom_bracket, (bottom_bracket[0], bottom_bracket[1] + 35)], fill=(80, 85, 95), width=5)
        draw.rectangle([bottom_bracket[0] - 12, bottom_bracket[1] + 35, bottom_bracket[0] + 12, bottom_bracket[1] + 45], fill=(30, 32, 36))

        # Badge
        draw.rounded_rectangle([50, 50, 270, 95], radius=12, fill=(25, 35, 48, 200), outline=(50, 90, 140))
        draw.text((65, 65), "CAMPUS COMMUTE", fill=(67, 133, 181))
        img.save(out_path, format='JPEG', quality=92)

    def generate_badminton(self, out_path):
        w, h = 800, 600
        img = self.create_gradient_bg(w, h, (45, 38, 28), (22, 18, 14))
        draw = ImageDraw.Draw(img)

        # Crossed Rackets
        # Racket 1 (Red/Black)
        r1_head = (290, 200)
        draw.ellipse([r1_head[0] - 80, r1_head[1] - 110, r1_head[0] + 80, r1_head[1] + 110], outline=(220, 50, 40), width=8)
        # Strings grid
        for sx in range(r1_head[0] - 70, r1_head[0] + 75, 12):
            draw.line([(sx, r1_head[1] - 95), (sx, r1_head[1] + 95)], fill=(240, 240, 240, 120), width=1)
        # Shaft & Grip
        draw.line([r1_head[0], r1_head[1] + 110, 480, 490], fill=(180, 185, 195), width=8)
        draw.line([440, 440, 480, 490], fill=(220, 50, 40), width=14)

        # Racket 2 (Blue/Black)
        r2_head = (510, 200)
        draw.ellipse([r2_head[0] - 80, r2_head[1] - 110, r2_head[0] + 80, r2_head[1] + 110], outline=(30, 130, 230), width=8)
        for sx in range(r2_head[0] - 70, r2_head[0] + 75, 12):
            draw.line([(sx, r2_head[1] - 95), (sx, r2_head[1] + 95)], fill=(240, 240, 240, 120), width=1)
        draw.line([r2_head[0], r2_head[1] + 110, 320, 490], fill=(180, 185, 195), width=8)
        draw.line([360, 440, 320, 490], fill=(30, 130, 230), width=14)

        # Shuttlecock in Center
        sh_x, sh_y = 400, 280
        # Cork Base
        draw.chord([sh_x - 18, sh_y + 15, sh_x + 18, sh_y + 45], 0, 180, fill=(240, 230, 210), outline=(210, 80, 60), width=2)
        # Feathers Cone
        draw.polygon([(sh_x - 16, sh_y + 15), (sh_x - 40, sh_y - 45), (sh_x + 40, sh_y - 45), (sh_x + 16, sh_y + 15)], fill=(250, 250, 252), outline=(200, 205, 215))
        for fx in range(sh_x - 30, sh_x + 35, 10):
            draw.line([(fx, sh_y - 45), (sh_x + fx // 5, sh_y + 15)], fill=(210, 215, 225), width=1)

        # Badge
        draw.rounded_rectangle([50, 50, 270, 95], radius=12, fill=(45, 35, 25, 200), outline=(180, 120, 40))
        draw.text((65, 65), "SPORTS & FITNESS", fill=(217, 154, 53))
        img.save(out_path, format='JPEG', quality=92)

    def generate_study_desk(self, out_path):
        w, h = 800, 600
        img = self.create_gradient_bg(w, h, (42, 38, 35), (20, 18, 16))
        draw = ImageDraw.Draw(img)

        # Desk Shadow
        draw.ellipse([160, 490, 640, 535], fill=(10, 9, 8))

        # Wooden Table Top (3D Isometric)
        # Top Surface
        table_poly = [(220, 320), (580, 320), (530, 260), (270, 260)]
        draw.polygon(table_poly, fill=(185, 140, 95), outline=(140, 100, 60), width=2)
        # Wood grain lines
        for offset in range(-40, 40, 15):
            draw.line([(250 + offset, 290), (550 + offset, 290)], fill=(165, 120, 80), width=1)
        # Front thickness edge
        draw.polygon([(220, 320), (580, 320), (580, 335), (220, 335)], fill=(150, 110, 70))

        # Black Metal Folding Legs (Hairpin style)
        for lx in [250, 550]:
            draw.line([(lx, 335), (lx - 30, 495)], fill=(35, 38, 42), width=7)
            draw.line([(lx + 20, 335), (lx - 20, 495)], fill=(35, 38, 42), width=7)
            # Crossbar
            draw.line([(lx - 15, 410), (lx - 5, 410)], fill=(50, 55, 60), width=5)

        # Modern LED Desk Lamp on Desk
        lamp_base = (320, 280)
        draw.ellipse([lamp_base[0] - 18, lamp_base[1] - 8, lamp_base[0] + 18, lamp_base[1] + 8], fill=(50, 55, 62))
        # Lamp Arm
        draw.line([lamp_base, (lamp_base[0] + 20, lamp_base[1] - 80), (lamp_base[0] + 70, lamp_base[1] - 60)], fill=(70, 75, 85), width=6)
        # Lamp Head & Light Glow
        head = (lamp_base[0] + 70, lamp_base[1] - 60)
        draw.ellipse([head[0] - 15, head[1] - 10, head[0] + 15, head[1] + 10], fill=(240, 245, 250))
        # Light cone
        draw.polygon([head, (head[0] - 40, 320), (head[0] + 60, 320)], fill=(255, 245, 200, 50))

        # Open Notebook on Desk
        draw.polygon([(390, 280), (460, 280), (450, 310), (380, 310)], fill=(245, 245, 248), outline=(200, 200, 205))

        # Badge
        draw.rounded_rectangle([50, 50, 270, 95], radius=12, fill=(45, 40, 35, 200), outline=(160, 120, 80))
        draw.text((65, 65), "HOSTEL FURNITURE", fill=(217, 154, 53))
        img.save(out_path, format='JPEG', quality=92)

    def generate_hostel_essentials(self, out_path):
        w, h = 800, 600
        img = self.create_gradient_bg(w, h, (30, 48, 42), (16, 26, 22))
        draw = ImageDraw.Draw(img)

        # Laundry Hamper (Left)
        hx, hy, hw, hh = 230, 180, 160, 280
        # Shadow
        draw.ellipse([hx, hy + hh - 15, hx + hw, hy + hh + 25], fill=(10, 16, 13))
        # Fabric Body
        draw.rounded_rectangle([hx, hy, hx + hw, hy + hh], radius=16, fill=(50, 90, 75), outline=(75, 135, 110), width=3)
        # Hamper Handles
        draw.rounded_rectangle([hx + 40, hy + 20, hx + hw - 40, hy + 38], radius=8, fill=(25, 45, 38))
        # Mesh Grid Texture
        for gy in range(hy + 50, hy + hh - 20, 25):
            draw.line([(hx + 15, gy), (hx + hw - 15, gy)], fill=(40, 75, 62), width=2)

        # Steam Iron (Right)
        ix, iy = 440, 290
        # Iron Soleplate (Base)
        draw.polygon([(ix, iy + 140), (ix + 180, iy + 140), (ix + 210, iy + 100), (ix + 20, iy + 100)], fill=(220, 225, 230), outline=(170, 175, 185))
        # Water Tank (Turquoise & White)
        draw.polygon([(ix + 20, iy + 100), (ix + 200, iy + 100), (ix + 170, iy + 45), (ix + 50, iy + 45)], fill=(32, 178, 170), outline=(50, 210, 200))
        # Handle
        draw.arc([ix + 40, iy + 10, ix + 180, iy + 80], 180, 360, fill=(245, 248, 250), width=14)
        # Dial
        draw.ellipse([ix + 95, iy + 65, ix + 125, iy + 95], fill=(25, 30, 35), outline=(200, 205, 210))

        # Badge
        draw.rounded_rectangle([50, 50, 270, 95], radius=12, fill=(25, 45, 38, 200), outline=(46, 120, 70))
        draw.text((65, 65), "HOSTEL ESSENTIALS", fill=(46, 204, 113))
        img.save(out_path, format='JPEG', quality=92)

    def generate_molecular_kit(self, out_path):
        w, h = 800, 600
        img = self.create_gradient_bg(w, h, (25, 35, 45), (14, 20, 26))
        draw = ImageDraw.Draw(img)

        # Open Organizer Case
        cx, cy, cw, ch = 200, 110, 400, 400
        draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=20, fill=(38, 45, 55), outline=(70, 85, 105), width=3)
        draw.rounded_rectangle([cx + 15, cy + 15, cx + cw - 15, cy + ch - 15], radius=12, fill=(28, 34, 42), outline=(50, 60, 72))

        # Molecular Structures (Balls and Sticks: Carbon, Hydrogen, Oxygen, Nitrogen)
        atoms = [
            # Carbon Atoms (Dark Slate)
            ((330, 220), (45, 50, 58), 24, "C"),
            ((430, 200), (45, 50, 58), 24, "C"),
            ((490, 270), (45, 50, 58), 24, "C"),
            ((450, 360), (45, 50, 58), 24, "C"),
            ((350, 380), (45, 50, 58), 24, "C"),
            ((290, 310), (45, 50, 58), 24, "C"),
            # Oxygen (Vibrant Red)
            ((560, 240), (220, 50, 50), 22, "O"),
            # Nitrogen (Royal Blue)
            ((250, 230), (40, 110, 220), 22, "N"),
            # Hydrogens (White)
            ((330, 160), (240, 245, 250), 16, "H"),
            ((440, 140), (240, 245, 250), 16, "H"),
            ((520, 390), (240, 245, 250), 16, "H"),
        ]

        bonds = [
            ((330, 220), (430, 200)),
            ((430, 200), (490, 270)),
            ((490, 270), (450, 360)),
            ((450, 360), (350, 380)),
            ((350, 380), (290, 310)),
            ((290, 310), (330, 220)),
            ((490, 270), (560, 240)),
            ((330, 220), (250, 230)),
            ((330, 220), (330, 160)),
            ((430, 200), (440, 140)),
            ((450, 360), (520, 390)),
        ]

        # Draw Bond Sticks
        for b1, b2 in bonds:
            draw.line([b1, b2], fill=(170, 175, 185), width=8)

        # Draw Atom Spheres
        for (pos, col, rad, label) in atoms:
            # 3D Highlight & Sphere
            draw.ellipse([pos[0] - rad, pos[1] - rad, pos[0] + rad, pos[1] + rad], fill=col, outline=(col[0] + 30, min(255, col[1] + 30), min(255, col[2] + 30)), width=2)
            # Specular light highlight
            draw.ellipse([pos[0] - rad // 2, pos[1] - rad // 2, pos[0] - rad // 4, pos[1] - rad // 4], fill=(255, 255, 255, 180))
            draw.text((pos[0] - 5, pos[1] - 7), label, fill=(255, 255, 255) if col[0] < 200 else (20, 25, 30))

        # Badge
        draw.rounded_rectangle([50, 50, 280, 95], radius=12, fill=(25, 40, 55, 200), outline=(50, 100, 160))
        draw.text((65, 65), "CHEMISTRY LAB KIT", fill=(67, 133, 181))
        img.save(out_path, format='JPEG', quality=92)
