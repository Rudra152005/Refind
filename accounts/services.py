from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

import secrets

def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return f"{secrets.randbelow(900000) + 100000}"


def generate_verification_url(request, user):
    """Generate email verification link for student."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    protocol = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    return f"{protocol}://{host}/accounts/verify-email/{uid}/{token}/"


def send_verification_email(request, user):
    """Send verification email containing a 6-digit code and secure token URL."""
    # Generate and store 6-digit verification code
    code = generate_verification_code()
    user.verification_code = code
    user.save(update_fields=['verification_code'])

    verification_url = generate_verification_url(request, user)
    subject = f"Your ReFind Campus Verification Code: {code}"
    
    context = {
        'user': user,
        'verification_code': code,
        'verification_url': verification_url,
    }
    
    html_content = render_to_string('emails/verify_email.html', context)
    text_content = (
        f"Hi {user.full_name},\n\n"
        f"Welcome to ReFind - Campus Pre-Owned Goods Marketplace.\n\n"
        f"Your 6-Digit Verification Code is:\n"
        f"    {code}\n\n"
        f"Or verify directly using this secure link:\n"
        f"    {verification_url}\n\n"
        f"Thank you,\nReFind Campus Community"
    )

    # Print to console prominently for local development clarity
    print("\n" + "="*65)
    print(f" [ReFind EMAIL VERIFICATION]")
    print(f" Recipient: {user.email}")
    print(f" 6-Digit Code: {code}")
    print(f" Direct Link:  {verification_url}")
    print("="*65 + "\n")

    # Send asynchronously in a background thread so slow SMTP servers or network latency
    # never block the HTTP response or cause worker timeouts on production platforms
    import threading
    import logging

    def _deliver_email_task():
        try:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=True,
            )
        except Exception as exc:
            logging.getLogger(__name__).warning("Verification email delivery issue for %s: %s", user.email, exc)

    email_thread = threading.Thread(target=_deliver_email_task, daemon=True)
    email_thread.start()

    return True, verification_url, code


def verify_email_token(uidb64, token):
    """Verify the token and activate student status."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    if default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.verification_code = None
        user.save(update_fields=['is_email_verified', 'verification_code'])
        return user
    return None
