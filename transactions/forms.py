from django import forms
from .models import Request, Report
from listings.models import Listing

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['message', 'offered_listing']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add a note to the student (e.g. proposed campus meeting spot, timing, questions)...',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            }),
            'offered_listing': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only user's own available listings can be offered for exchange
            self.fields['offered_listing'].queryset = Listing.objects.filter(owner=user, status='Available')
            self.fields['offered_listing'].required = False
            self.fields['offered_listing'].empty_label = "-- Select an item you own to offer (optional) --"


class ReviewForm(forms.Form):
    RATING_CHOICES = (
        (5, '★★★★★ (5 - Excellent)'),
        (4, '★★★★☆ (4 - Good)'),
        (3, '★★★☆☆ (3 - Average)'),
        (2, '★★☆☆☆ (2 - Fair)'),
        (1, '★☆☆☆☆ (1 - Poor)'),
    )
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
        }),
        label="Rating"
    )
    review_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Share your experience with this student (promptness, item condition, communication)...',
            'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-primary-green transition'
        }),
        label="Feedback / Review (Optional)"
    )


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please specify why this listing is inappropriate, fraudulent, or violates campus rules...',
                'class': 'w-full px-4 py-3 rounded-xl border border-border bg-input-bg text-main-text focus:outline-none focus:ring-2 focus:ring-error transition'
            })
        }
