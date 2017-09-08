from django import forms

from .base import BaseFilter
from .ffmpeg import get_codecs


class Codec(BaseFilter):
    codec = forms.ChoiceField(choices=[(c['name'], c['name']) for c in get_codecs()], required=False)
    copy = forms.BooleanField(initial=False, required=False)
    before_input = forms.BooleanField(initial=False, required=False)

    def clean(self):
        if not self.cleaned_data['copy'] and not self.cleaned_data['codec']:
            raise forms.ValidationError("Codec is not defined.")

        return super(Codec, self).clean()

    def generate(self, as_str: bool = False):
        self.validate()
        stream = self.cleaned_data['stream']
        self.args = ["-c:" + str(stream) if stream else "-c"]
        if self.cleaned_data['copy']:
            self.args.append("copy")
        else:
            self.args.append(self.cleaned_data['codec'])
        return " ".join(self.args) if as_str else self.args
