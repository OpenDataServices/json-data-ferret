from django import forms


class RecordImportForm(forms.Form):
    file = forms.FileField()
    comment = forms.CharField(widget=forms.Textarea)
