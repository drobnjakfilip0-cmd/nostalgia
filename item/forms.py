from django import forms
from .models import Item, ItemSize

INPUT_CLASSES = (
    "w-full px-4 py-3 rounded-xl border border-black/10 bg-white text-black "
    "placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#c2410c] "
    "focus:border-[#c2410c] transition"
)

SIZE_CHOICES = [
    ("XS", "XS"), ("S", "S"), ("M", "M"),
    ("L", "L"), ("XL", "XL"), ("XXL", "XXL"),
]


class NewItemForm(forms.ModelForm):

    sizes = forms.MultipleChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model  = Item
        fields = ('category', 'name', 'description', 'price', 'image')
        widgets = {
            'category':    forms.Select(attrs={'class': INPUT_CLASSES}),
            'name':        forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES}),
            'price':       forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'image':       forms.FileInput(attrs={'class': INPUT_CLASSES}),
        }

    def save(self, commit=True):
        item  = super().save(commit)
        sizes = self.cleaned_data.get('sizes')

        if sizes:
            ItemSize.objects.bulk_create([
                ItemSize(item=item, size=s, stock=1) for s in sizes
            ])

        return item


class EditItemForm(forms.ModelForm):
    class Meta:
        model  = Item
        fields = ('category', 'name', 'description', 'price', 'image', 'is_sold')
        widgets = {
            'category':    forms.Select(attrs={'class': INPUT_CLASSES}),
            'name':        forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES}),
            'price':       forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'image':       forms.FileInput(attrs={'class': INPUT_CLASSES}),
            'is_sold':     forms.CheckboxInput(attrs={'class': INPUT_CLASSES}),
        }
        labels = {
            'image':       'Glavna slika',
            'description': 'Opis',
            'category':    'Kategorija',
            'name':        'Ime',
            'price':       'Cena',
        }
