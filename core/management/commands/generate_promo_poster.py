import importlib.util
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

if importlib.util.find_spec('PIL') is not None:
    import importlib
    Image = importlib.import_module('PIL.Image')
    ImageDraw = importlib.import_module('PIL.ImageDraw')
    ImageFont = importlib.import_module('PIL.ImageFont')
else:
    Image = ImageDraw = ImageFont = None

class Command(BaseCommand):
    help = 'Generates 4 distinct, high-definition cinematic scene frames and a master poster for the ReFind video player.'

    def handle(self, *args, **options):
        img_dir = Path(settings.BASE_DIR) / 'static' / 'images'
        img_dir.mkdir(parents=True, exist_ok=True)

        w, h = 1280, 720
        self.generate_scene_1(img_dir / 'promo-scene-1.jpg', w, h)
        self.generate_scene_2(img_dir / 'promo-scene-2.jpg', w, h)
        self.generate_scene_3(img_dir / 'promo-scene-3.jpg', w, h)
        self.generate_scene_4(img_dir / 'promo-scene-4.jpg', w, h)
        self.generate_master_poster(img_dir / 'refind-promo-poster.jpg', 1920, 1080)

        self.stdout.write(self.style.SUCCESS("Successfully generated all 4 promo scene frames and master poster!"))

    def create_gradient(self, w, h, c1, c2):
        base = Image.new('RGB', (w, h), c1)
        draw = ImageDraw.Draw(base)
        for y in range(h):
            r = y / h
            col = (
                int(c1[0] * (1 - r) + c2[0] * r),
                int(c1[1] * (1 - r) + c2[1] * r),
                int(c1[2] * (1 - r) + c2[2] * r),
            )
            draw.line([(0, y), (w, y)], fill=col)
        return base

    def generate_scene_1(self, out_path, w, h):
        # Scene 1: Modern University Hostel Room with Unused Essentials
        img = self.create_gradient(w, h, (24, 38, 30), (12, 20, 16))
        draw = ImageDraw.Draw(img)

        # Window with morning sunlight glow
        draw.rounded_rectangle([w - 480, 60, w - 80, 420], radius=16, fill=(230, 245, 235), outline=(180, 205, 190), width=4)
        draw.line([(w - 280, 60), (w - 280, 420)], fill=(180, 205, 190), width=4)
        draw.line([(w - 480, 240), (w - 80, 240)], fill=(180, 205, 190), width=4)
        # Sunlight cone
        draw.polygon([(w - 280, 240), (200, h), (800, h)], fill=(255, 250, 220, 30))

        # Study Desk
        draw.polygon([(120, 520), (w - 120, 520), (w - 60, 430), (180, 430)], fill=(185, 140, 95), outline=(140, 100, 60), width=2)
        draw.rectangle([120, 520, w - 120, 545], fill=(150, 110, 70))

        # Unused Items on Desk: Stack of Textbooks
        draw.rounded_rectangle([220, 370, 420, 420], radius=6, fill=(33, 140, 80))
        draw.rounded_rectangle([210, 320, 430, 365], radius=6, fill=(67, 133, 181))
        draw.rounded_rectangle([230, 275, 410, 315], radius=6, fill=(217, 154, 53))
        draw.text((245, 285), "CALCULUS & PHYSICS", fill=(255, 255, 255))

        # Open Laptop & Headphones
        draw.polygon([(480, 420), (660, 420), (640, 330), (500, 330)], fill=(200, 205, 215))
        draw.polygon([(460, 425), (680, 425), (660, 420), (480, 420)], fill=(160, 165, 175))
        draw.arc([720, 350, 820, 440], 180, 360, fill=(220, 225, 230), width=8)

        # Student Silhouette Looking at items
        draw.ellipse([860, 220, 960, 320], fill=(230, 195, 165))
        draw.polygon([(820, 330), (1000, 330), (1030, 560), (790, 560)], fill=(40, 70, 55))

        # Scene Tag Overlay
        draw.rounded_rectangle([40, 40, 360, 85], radius=12, fill=(15, 28, 20, 220), outline=(46, 204, 113))
        draw.text((60, 52), "SCENE 1: HOSTEL ROOM (0-5s)", fill=(46, 204, 113))
        img.save(out_path, format='JPEG', quality=92)

    def generate_scene_2(self, out_path, w, h):
        # Scene 2: Smartphone Marketplace Browsing
        img = self.create_gradient(w, h, (18, 32, 26), (10, 18, 14))
        draw = ImageDraw.Draw(img)

        # Phone mockup in center
        px, py, pw, ph = w // 2 - 150, 60, 300, 600
        draw.rounded_rectangle([px + 10, py + 15, px + pw + 10, py + ph + 15], radius=36, fill=(5, 10, 8, 200))
        draw.rounded_rectangle([px, py, px + pw, py + ph], radius=36, fill=(30, 36, 42), outline=(70, 80, 92), width=3)
        draw.rounded_rectangle([px + 12, py + 14, px + pw - 12, py + ph - 14], radius=26, fill=(248, 250, 247))

        # App Header
        draw.rectangle([px + 12, py + 14, px + pw - 12, py + 75], fill=(33, 140, 80))
        draw.text((px + 30, py + 35), "ReFind Marketplace", fill=(255, 255, 255))

        # Search Bar
        draw.rounded_rectangle([px + 24, py + 88, px + pw - 24, py + 128], radius=10, fill=(255, 255, 255), outline=(220, 230, 222))
        draw.text((px + 40, py + 100), "Search campus listings...", fill=(140, 150, 145))

        # Product Card 1
        draw.rounded_rectangle([px + 24, py + 142, px + pw - 24, py + 265], radius=14, fill=(255, 255, 255), outline=(228, 235, 227))
        draw.rounded_rectangle([px + 32, py + 150, px + 115, py + 215], radius=8, fill=(33, 140, 80))
        draw.text((px + 125, py + 155), "Calculus 8th Ed.", fill=(36, 51, 41))
        draw.text((px + 125, py + 180), "$35.00  |  Like New", fill=(33, 140, 80))

        # Product Card 2
        draw.rounded_rectangle([px + 24, py + 280, px + pw - 24, py + 403], radius=14, fill=(255, 255, 255), outline=(228, 235, 227))
        draw.rounded_rectangle([px + 32, py + 288, px + 115, py + 353], radius=8, fill=(45, 55, 72))
        draw.text((px + 125, py + 293), "Casio fx-991EX", fill=(36, 51, 41))
        draw.text((px + 125, py + 318), "$18.00  |  Good", fill=(33, 140, 80))

        # Product Card 3: Free Donation
        draw.rounded_rectangle([px + 24, py + 418, px + pw - 24, py + 541], radius=14, fill=(232, 245, 233), outline=(117, 184, 121))
        draw.text((px + 40, py + 438), "Campus Free Donation", fill=(23, 107, 58))
        draw.text((px + 40, py + 465), "Steam Iron & Laundry Hamper", fill=(33, 140, 80))

        # Finger interaction indicator
        draw.ellipse([px + 180, py + 230, px + 220, py + 270], outline=(46, 204, 113), width=3)

        # Scene Tag Overlay
        draw.rounded_rectangle([40, 40, 420, 85], radius=12, fill=(15, 28, 20, 220), outline=(46, 204, 113))
        draw.text((60, 52), "SCENE 2: SMARTPHONE BROWSE (5-10s)", fill=(46, 204, 113))
        img.save(out_path, format='JPEG', quality=92)

    def generate_scene_3(self, out_path, w, h):
        # Scene 3: Two Students Exchanging on College Campus Quad
        img = self.create_gradient(w, h, (20, 40, 30), (12, 24, 18))
        draw = ImageDraw.Draw(img)

        # Campus Quad Trees & Lawn
        draw.polygon([(0, 480), (w, 480), (w, h), (0, h)], fill=(18, 38, 26))
        # Distant Campus Clocktower
        draw.rectangle([w // 2 - 40, 200, w // 2 + 40, 480], fill=(28, 52, 38))
        draw.polygon([(w // 2 - 50, 200), (w // 2, 130), (w // 2 + 50, 200)], fill=(36, 68, 50))
        draw.ellipse([w // 2 - 15, 225, w // 2 + 15, 255], fill=(255, 245, 210))

        # Student 1 (Seller / Giver)
        s1_x = w // 2 - 220
        draw.ellipse([s1_x + 30, 260, s1_x + 95, 325], fill=(235, 195, 165))  # Head
        draw.polygon([(s1_x + 15, 330), (s1_x + 110, 330), (s1_x + 130, 520), (s1_x, 520)], fill=(33, 140, 80))  # Green Hoodie

        # Student 2 (Buyer / Receiver)
        s2_x = w // 2 + 100
        draw.ellipse([s2_x + 25, 260, s2_x + 90, 325], fill=(230, 190, 160))  # Head
        draw.polygon([(s2_x + 10, 330), (s2_x + 105, 330), (s2_x + 120, 520), (s2_x - 5, 520)], fill=(67, 133, 181))  # Blue Jacket

        # Exchanged Textbook & Gadget Between Hands
        draw.rounded_rectangle([w // 2 - 60, 370, w // 2 + 50, 435], radius=8, fill=(217, 154, 53), outline=(255, 240, 200), width=2)
        draw.text((w // 2 - 35, 395), "REUSE", fill=(255, 255, 255))

        # Verified Handover Checkmark Badge
        draw.ellipse([w // 2 - 25, 310, w // 2 + 25, 360], fill=(46, 204, 113), outline=(255, 255, 255), width=2)
        draw.line([(w // 2 - 10, 335), (w // 2 - 2, 345), (w // 2 + 12, 325)], fill=(255, 255, 255), width=4)

        # Scene Tag Overlay
        draw.rounded_rectangle([40, 40, 430, 85], radius=12, fill=(15, 28, 20, 220), outline=(46, 204, 113))
        draw.text((60, 52), "SCENE 3: CAMPUS HANDOVER (10-15s)", fill=(46, 204, 113))
        img.save(out_path, format='JPEG', quality=92)

    def generate_scene_4(self, out_path, w, h):
        # Scene 4: ReFind Brand Reveal & Tagline
        img = self.create_gradient(w, h, (10, 22, 16), (22, 48, 34))
        draw = ImageDraw.Draw(img)

        # Central Glowing Shield Logo
        cx, cy = w // 2, h // 2 - 60
        draw.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(33, 140, 80, 40))
        draw.rounded_rectangle([cx - 65, cy - 65, cx + 65, cy + 65], radius=24, fill=(33, 140, 80), outline=(46, 204, 113), width=3)
        # Circular arrows symbol in logo
        draw.arc([cx - 35, cy - 35, cx + 35, cy + 35], 45, 315, fill=(255, 255, 255), width=8)

        # ReFind Title
        draw.text((cx - 150, cy + 90), "ReFind", fill=(255, 255, 255))

        # Tagline
        draw.text((cx - 250, cy + 180), '"Find it again. Give it a new beginning."', fill=(46, 204, 113))
        draw.text((cx - 210, cy + 225), "University-Exclusive Pre-Owned Goods Marketplace", fill=(180, 205, 190))

        # Scene Tag Overlay
        draw.rounded_rectangle([40, 40, 410, 85], radius=12, fill=(15, 28, 20, 220), outline=(46, 204, 113))
        draw.text((60, 52), "SCENE 4: BRAND REVEAL (15-20s)", fill=(46, 204, 113))
        img.save(out_path, format='JPEG', quality=92)

    def generate_master_poster(self, out_path, w, h):
        # 1080p Master Showcase Poster
        img = self.create_gradient(w, h, (14, 28, 22), (24, 48, 36))
        draw = ImageDraw.Draw(img)

        # Ambient Glows
        draw.ellipse([w // 2 - 400, -100, w // 2 + 400, 600], fill=(33, 140, 80, 50))
        draw.ellipse([200, 200, 800, 800], fill=(23, 107, 58, 40))

        # Center Brand Emblem
        draw.rounded_rectangle([w // 2 - 280, 180, w // 2 + 280, 320], radius=24, fill=(18, 36, 28, 220), outline=(46, 204, 113), width=2)
        draw.text((w // 2 - 120, 200), "ReFind", fill=(255, 255, 255))
        draw.text((w // 2 - 240, 270), '"Find it again. Give it a new beginning."', fill=(46, 204, 113))

        # 4 Interactive Scene Cards across the middle
        scene_info = [
            ("01. HOSTEL ESSENTIALS", "Unused books & tech", (33, 140, 80)),
            ("02. MOBILE MARKETPLACE", "Affordable student deals", (67, 133, 181)),
            ("03. CAMPUS HANDOVER", "Safe peer exchange", (217, 154, 53)),
            ("04. ZERO-WASTE REUSE", "Circular student economy", (46, 204, 113)),
        ]
        card_w, card_h = 360, 240
        start_x = (w - (4 * card_w + 3 * 30)) // 2
        for i, (title, sub, col) in enumerate(scene_info):
            cx = start_x + i * (card_w + 30)
            cy = 460
            draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=16, fill=(22, 42, 32, 230), outline=col, width=2)
            draw.rounded_rectangle([cx + 20, cy + 20, cx + 60, cy + 60], radius=10, fill=col)
            draw.text((cx + 34, cy + 30), str(i + 1), fill=(255, 255, 255))
            draw.text((cx + 75, cy + 32), f"SCENE {i+1}", fill=col)
            draw.text((cx + 20, cy + 90), title, fill=(240, 245, 242))
            draw.text((cx + 20, cy + 130), sub, fill=(160, 180, 170))
            draw.rounded_rectangle([cx + 20, cy + 180, cx + card_w - 20, cy + 215], radius=8, fill=(30, 56, 44))
            draw.text((cx + 35, cy + 190), f"Play Scene {i+1} (5s)", fill=(46, 204, 113))

        # Bottom Bar
        draw.text((w // 2 - 250, h - 80), "ReFind - Official 20-Second Cinematic Promotional Video", fill=(160, 185, 170))
        img.save(out_path, format='JPEG', quality=95)
