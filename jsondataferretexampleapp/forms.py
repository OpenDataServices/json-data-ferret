from django import forms

COMMENT_LABEL = "Comment for history"


class OrganisationNewForm(forms.Form):
    id = forms.SlugField()
    title = forms.CharField()
    comment = forms.CharField(widget=forms.Textarea, label=COMMENT_LABEL)


class ModelImportForm(forms.Form):
    file = forms.FileField()
    comment = forms.CharField(widget=forms.Textarea, label=COMMENT_LABEL)


class ProjectNewForm(forms.Form):
    id = forms.SlugField()
    title = forms.CharField()
    comment = forms.CharField(widget=forms.Textarea, label=COMMENT_LABEL)
