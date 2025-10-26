from django import forms
from .models import Job
from roadTripper.models import Skill

class JobForm(forms.ModelForm):
    # Allow recruiters to add new skills inline (comma-separated)
    new_skills = forms.CharField(
        required=False,
        help_text="Add new skills, comma-separated (e.g., Python, Django, REST)",
        widget=forms.TextInput(attrs={"placeholder": "e.g., Python, Django, REST"})
    )

    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "location",
            "address",
            "remote_type",
            "min_experience",
            "salary_min",
            "salary_max",
            "visa_sponsorship",
            "skills",
            # Note: new_skills is a form-only field (not in the model)
        ]

    def _parse_new_skills(self):
        raw = (self.cleaned_data.get("new_skills") or "").strip()
        if not raw:
            return []
        parts = [p.strip() for p in raw.split(',')]
        # Drop empties, normalize spacing; keep original casing for display
        return [p for p in parts if p]

    def _save_new_skills(self, instance: Job):
        names = self._parse_new_skills()
        if not names:
            return
        to_add = []
        for name in names:
            # case-insensitive reuse of existing skills
            existing = Skill.objects.filter(name__iexact=name).first()
            if existing:
                to_add.append(existing)
            else:
                s = Skill.objects.create(name=name)
                to_add.append(s)
        if to_add:
            instance.skills.add(*to_add)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            # If already saved, we can attach skills immediately
            self._save_new_skills(instance)
        else:
            # Defer until the view calls form.save_m2m()
            orig_save_m2m = self.save_m2m

            def _wrapped_save_m2m():
                orig_save_m2m()
                self._save_new_skills(instance)

            self.save_m2m = _wrapped_save_m2m
        return instance
