from django import forms
from django.core.exceptions import ValidationError
from .models import Listing

class ListingForm(forms.ModelForm):
    # Checkbox to remove secondary images on update
    clear_image2 = forms.BooleanField(required=False, label="Remove 2nd image")
    clear_image3 = forms.BooleanField(required=False, label="Remove 3rd image")

    class Meta:
        model = Listing
        fields = [
            'title', 'category', 'condition', 'listing_type',
            'price', 'wanted_item_text', 'description',
            'image', 'image2', 'image3'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Engineering Mechanics Textbook (8th Edition)',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            }),
            'condition': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            }),
            'listing_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition',
                'id': 'id_listing_type'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition',
                'id': 'id_price'
            }),
            'wanted_item_text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe what you would like in exchange (e.g., Looking for a Scientific Calculator or Lab Coat)...',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition',
                'id': 'id_wanted_item_text'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Provide detailed information about product condition, accessories included, and campus pickup location...',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full text-sm text-secondary-text file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-light-green file:text-primary-green hover:file:bg-accent-green hover:file:text-white transition'
            }),
            'image2': forms.FileInput(attrs={
                'class': 'w-full text-sm text-secondary-text file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-light-green file:text-primary-green hover:file:bg-accent-green hover:file:text-white transition'
            }),
            'image3': forms.FileInput(attrs={
                'class': 'w-full text-sm text-secondary-text file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-light-green file:text-primary-green hover:file:bg-accent-green hover:file:text-white transition'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image and not self.instance.pk:
            raise ValidationError("Primary product image is required.")
        if image and hasattr(image, 'size') and image.size > 5 * 1024 * 1024:
            raise ValidationError("Image file size must not exceed 5MB.")
        return image

    def clean_image2(self):
        img = self.cleaned_data.get('image2')
        if img and hasattr(img, 'size') and img.size > 5 * 1024 * 1024:
            raise ValidationError("Second image size must not exceed 5MB.")
        return img

    def clean_image3(self):
        img = self.cleaned_data.get('image3')
        if img and hasattr(img, 'size') and img.size > 5 * 1024 * 1024:
            raise ValidationError("Third image size must not exceed 5MB.")
        return img

    def clean(self):
        cleaned_data = super().clean()
        listing_type = cleaned_data.get('listing_type')
        price = cleaned_data.get('price')
        wanted_item = cleaned_data.get('wanted_item_text')

        if listing_type == 'Sell':
            if price is None or price <= 0:
                self.add_error('price', "Please specify a valid selling price greater than 0.")
        elif listing_type == 'Exchange':
            cleaned_data['price'] = 0.00
            if not wanted_item or not wanted_item.strip():
                self.add_error('wanted_item_text', "Please describe what item you would like to receive in exchange.")
        elif listing_type == 'Donate':
            cleaned_data['price'] = 0.00

        return cleaned_data
