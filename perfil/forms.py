from django import forms
from .models import  Conta, Categoria

class ContaForm(forms.ModelForm):
    # https://stackoverflow.com/questions/38961387/django-all-form-error-messages-as-a-single-string
    
    class Meta:
        model = Conta
        fields = "__all__"

        

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = "__all__"
