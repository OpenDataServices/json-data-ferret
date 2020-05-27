from django import forms


class OrganisationNewForm(forms.Form):
    title = forms.CharField()


class OrganisationImportForm(forms.Form):
    file = forms.FileField()


class OrganisationMakeDisputedForm(forms.Form):
    pass


class OrganisationMakePrivateForm(forms.Form):
    pass


class ProjectNewForm(forms.Form):
    id = forms.SlugField()
    title = forms.CharField()


class ProjectImportForm(forms.Form):
    file = forms.FileField()


class ProjectMakeDisputedForm(forms.Form):
    pass


class ProjectMakePrivateForm(forms.Form):
    pass
