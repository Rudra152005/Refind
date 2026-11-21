import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from listings.models import Listing
from transactions.models import Request, Report
from messaging.models import Message

User = get_user_model()

def create_placeholder_image(text, bg_color=(33, 140, 80), text_color=(255, 255, 255)):
    """Generate a placeholder product image using Pillow."""
    img = Image.new('RGB', (600, 450), color=bg_color)
    draw = ImageDraw.Draw(img)
    # Simple centered text
    bbox = draw.textbbox((0, 0), text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((600 - w) / 2, (450 - h) / 2), text, fill=text_color)
    
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return ContentFile(buf.getvalue(), name=f"{text.lower().replace(' ', '_')[:20]}.jpg")


class Command(BaseCommand):
    help = 'Populates the database with realistic campus marketplace sample data.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding ReFind campus marketplace data...")

        # 1. Admin & Students
        admin_user, _ = User.objects.get_or_create(
            email='admin@campus.edu',
            defaults={
                'full_name': 'Campus Admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_email_verified': True,
                'hostel': 'Staff Quarters'
            }
        )
        admin_user.set_password('AdminPass123!')
        admin_user.save()

        students_data = [
            ('alex.chen@campus.edu', 'Alex Chen', 'Oak Hall, Room 302', '+1 555-0101'),
            ('sarah.miller@campus.edu', 'Sarah Miller', 'Maple Tower, 4B', '+1 555-0102'),
            ('priya.sharma@campus.edu', 'Priya Sharma', 'Pine Dorm, Room 104', '+1 555-0103'),
            ('david.kim@campus.edu', 'David Kim', 'Elm Hall, Room 210', '+1 555-0104'),
        ]

        users = {}
        for email, name, hostel, phone in students_data:
            u, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': name,
                    'role': 'student',
                    'is_email_verified': True,
                    'hostel': hostel,
                    'phone': phone
                }
            )
            u.set_password('StudentPass123!')
            u.is_email_verified = True
            u.save()
            users[email] = u

        self.stdout.write(f"Created {len(users) + 1} student/admin accounts.")

        # 2. Campus Listings
        listings_data = [
            {
                'owner': users['alex.chen@campus.edu'],
                'title': 'Stewart Calculus Early Transcendentals (8th Edition)',
                'description': 'Hardcover textbook used for MATH 101/102. Clean pages, no highlighting or torn pages. Perfect condition for incoming engineering students.',
                'category': 'Books',
                'condition': 'Like New',
                'listing_type': 'Sell',
                'price': 35.00,
                'status': 'Sold',
                'img_text': 'Calculus Book',
                'bg_color': (33, 140, 80)
            },
            {
                'owner': users['alex.chen@campus.edu'],
                'title': 'Casio fx-991EX ClassWiz Advanced Scientific Calculator',
                'description': 'Essential high-resolution calculator for engineering & physics courses. Fully functional with solar battery.',
                'category': 'Electronics',
                'condition': 'Good',
                'listing_type': 'Sell',
                'price': 18.00,
                'status': 'Available',
                'img_text': 'Casio Calculator',
                'bg_color': (23, 107, 58)
            },
            {
                'owner': users['sarah.miller@campus.edu'],
                'title': 'Giant Boulder Mountain Bike (Campus Commuter)',
                'description': 'Reliable 21-speed campus bicycle. Recently tuned brakes, smooth gear shifting, includes front basket and safety bell. Ideal for getting between west and east campus.',
                'category': 'Cycles',
                'condition': 'Good',
                'listing_type': 'Sell',
                'price': 85.00,
                'status': 'Available',
                'img_text': 'Campus Bicycle',
                'bg_color': (67, 133, 181)
            },
            {
                'owner': users['sarah.miller@campus.edu'],
                'title': 'Foldable Study Desk & Ergonomic Desk Lamp',
                'description': 'Wooden foldable desk with metal frame. Saves hostel room space when not studying. Comes with an LED desk lamp.',
                'category': 'Furniture',
                'condition': 'Like New',
                'listing_type': 'Exchange',
                'price': 0.00,
                'wanted_item_text': 'Looking to barter for a Mini Fridge or electric induction cooker.',
                'status': 'Reserved',
                'img_text': 'Study Desk Set',
                'bg_color': (117, 184, 121)
            },
            {
                'owner': users['priya.sharma@campus.edu'],
                'title': 'Organic Chemistry Molecular Model Kit',
                'description': 'Complete set with 240 pieces, bonds, and removal tool. Donating for free to any 1st or 2nd year student taking CHEM 201.',
                'category': 'Books',
                'condition': 'Good',
                'listing_type': 'Donate',
                'price': 0.00,
                'status': 'Donated',
                'img_text': 'Molecular Model Kit',
                'bg_color': (33, 140, 80)
            },
            {
                'owner': users['priya.sharma@campus.edu'],
                'title': 'Yonex Nanoray Badminton Rackets Set + 6 Shuttles',
                'description': 'Pair of lightweight graphite badminton rackets with carry case and tube of feather shuttles. Great for campus gym courts.',
                'category': 'Sports',
                'condition': 'Like New',
                'listing_type': 'Sell',
                'price': 25.00,
                'status': 'Available',
                'img_text': 'Badminton Set',
                'bg_color': (217, 154, 53)
            },
            {
                'owner': users['david.kim@campus.edu'],
                'title': 'Collapsible Laundry Hamper & Steam Iron',
                'description': 'Lightly used laundry basket with handles and compact steam iron. Free donation to any new hostel resident.',
                'category': 'Hostel Essentials',
                'condition': 'Good',
                'listing_type': 'Donate',
                'price': 0.00,
                'status': 'Available',
                'img_text': 'Hostel Essentials',
                'bg_color': (33, 140, 80)
            },
            {
                'owner': users['david.kim@campus.edu'],
                'title': 'Anker USB-C 7-in-1 Hub (4K HDMI, SD Card, 100W PD)',
                'description': 'Compact dongle hub compatible with MacBooks, Dell XPS, and iPads. Tested and works perfectly.',
                'category': 'Electronics',
                'condition': 'Like New',
                'listing_type': 'Sell',
                'price': 22.00,
                'status': 'Available',
                'img_text': 'USB-C Hub',
                'bg_color': (45, 55, 72)
            },
        ]

        created_listings = []
        for l_data in listings_data:
            existing = Listing.objects.filter(title=l_data['title'], owner=l_data['owner']).first()
            if not existing:
                img_file = create_placeholder_image(l_data['img_text'], bg_color=l_data['bg_color'])
                listing = Listing(
                    owner=l_data['owner'],
                    title=l_data['title'],
                    description=l_data['description'],
                    category=l_data['category'],
                    condition=l_data['condition'],
                    listing_type=l_data['listing_type'],
                    price=l_data['price'],
                    wanted_item_text=l_data.get('wanted_item_text', ''),
                    status=l_data['status']
                )
                try:
                    listing.image.save(img_file.name, img_file, save=False)
                except Exception as img_err:
                    self.stdout.write(self.style.WARNING(f"  Note: Skipped remote image upload for '{listing.title}': {img_err}"))
                listing.save()
                created_listings.append(listing)
            else:
                created_listings.append(existing)

        self.stdout.write(f"Populated {len(created_listings)} listings across campus categories.")

        # 3. Requests & Reviews
        calc_book = next(l for l in created_listings if 'Calculus' in l.title)
        study_desk = next(l for l in created_listings if 'Desk' in l.title)
        mol_kit = next(l for l in created_listings if 'Molecular' in l.title)
        casio_calc = next(l for l in created_listings if 'Casio' in l.title)

        # Completed transaction with review
        req1, _ = Request.objects.get_or_create(
            listing=calc_book,
            requester=users['priya.sharma@campus.edu'],
            defaults={
                'message': 'Hi Alex, can we meet at the campus library lobby tomorrow around 2 PM?',
                'status': 'Completed',
                'rating': 5,
                'review_text': 'Super smooth campus meetup near main library! Book was in pristine condition, highly recommend Alex!'
            }
        )

        # Reserved exchange request
        req2, _ = Request.objects.get_or_create(
            listing=study_desk,
            requester=users['david.kim@campus.edu'],
            defaults={
                'message': 'Hi Sarah! I have a compact induction cooker from last semester I can trade for your study desk.',
                'status': 'Accepted'
            }
        )

        # Pending Buy Request
        req3, _ = Request.objects.get_or_create(
            listing=casio_calc,
            requester=users['sarah.miller@campus.edu'],
            defaults={
                'message': 'Hey Alex, is this calculator still available? I can meet you at Oak Hall cafeteria.',
                'status': 'Pending'
            }
        )

        # Completed Donation Request
        req4, _ = Request.objects.get_or_create(
            listing=mol_kit,
            requester=users['alex.chen@campus.edu'],
            defaults={
                'message': 'Hi Priya, taking CHEM 201 this semester. This kit would be immensely helpful!',
                'status': 'Completed',
                'rating': 5,
                'review_text': 'Thank you so much Priya! Giving this for free to a junior student means a lot!'
            }
        )

        self.stdout.write("Created realistic requests, transactions and peer reviews.")

        # 4. Message Conversations
        Message.objects.get_or_create(
            listing=calc_book,
            sender=users['priya.sharma@campus.edu'],
            recipient=users['alex.chen@campus.edu'],
            body='Hi Alex, is the Stewart Calculus book still available?'
        )
        Message.objects.get_or_create(
            listing=calc_book,
            sender=users['alex.chen@campus.edu'],
            recipient=users['priya.sharma@campus.edu'],
            body='Yes Priya! It is available. I can meet you tomorrow afternoon in the library lobby.'
        )
        Message.objects.get_or_create(
            listing=calc_book,
            sender=users['priya.sharma@campus.edu'],
            recipient=users['alex.chen@campus.edu'],
            body='Perfect, see you near the library front desk at 2 PM. I have exact cash.'
        )

        bike_listing = next(l for l in created_listings if 'Bike' in l.title)
        Message.objects.get_or_create(
            listing=bike_listing,
            sender=users['david.kim@campus.edu'],
            recipient=users['sarah.miller@campus.edu'],
            body='Hey Sarah, does the Giant mountain bike include a lock or helmet?'
        )
        Message.objects.get_or_create(
            listing=bike_listing,
            sender=users['sarah.miller@campus.edu'],
            recipient=users['david.kim@campus.edu'],
            body='Hi David, yes, I can include a combination cable lock with it!'
        )

        # 5. Wishlists
        users['priya.sharma@campus.edu'].saved_listings.add(bike_listing)
        users['david.kim@campus.edu'].saved_listings.add(casio_calc)

        # 6. Sample Report
        Report.objects.get_or_create(
            listing=casio_calc,
            reporter=users['david.kim@campus.edu'],
            defaults={
                'reason': 'Testing moderation flag: checking serial number authenticity.',
                'status': 'Open'
            }
        )

        self.stdout.write(self.style.SUCCESS("ReFind database successfully seeded with realistic campus data!"))
        self.stdout.write(self.style.SUCCESS("Admin account: admin@campus.edu / AdminPass123!"))
        self.stdout.write(self.style.SUCCESS("Student account: alex.chen@campus.edu / StudentPass123!"))
        self.stdout.write(self.style.SUCCESS("Student account: sarah.miller@campus.edu / StudentPass123!"))
