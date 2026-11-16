from django import forms

from .models import ROLE_TYPE_CHOICES, STAGE_CHOICES, Profile


class ProfileForm(forms.ModelForm):
    preferred_role_types = forms.MultipleChoiceField(
        choices=ROLE_TYPE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple, label="Preferred role types"
    )
    preferred_stages = forms.MultipleChoiceField(
        choices=STAGE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple, label="Preferred company stages"
    )

    class Meta:
        model = Profile
        fields = ["background", "skills", "preferred_role_types", "preferred_locations", "preferred_stages"]
        widgets = {
            "background": forms.Textarea(attrs={"rows": 4}),
            "skills": forms.Textarea(attrs={"rows": 3}),
        }
