from django.shortcuts import render
from perfil.models import Conta, Categoria
from .models import Valores
from .forms import ValoresForm
from django.contrib.messages import constants
from django.contrib import messages
import datetime
from django.conf import settings

from django.http import FileResponse
from django.template.loader import render_to_string 
from io import BytesIO
import os
from weasyprint import HTML

from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta






# Create your views here.
def novo_valor(request):
    context = {
        "contas": Conta.objects.all(),
        "categorias": Categoria.objects.all()
    }
    
    if request.method == "POST":
        valores = ValoresForm(request.POST)
        # caso todas as informacoes estem no formato certo
        if valores.is_valid():

            # verifica que a conta realmente exista
            if conta := Conta.objects.get(pk=int(valores.cleaned_data["conta"].id)): # valores is a form, cleaned_data["conta"] containes a conta Query object, then a get it's id
                
                # caso seja emtrada registrar
                if valores.cleaned_data["tipo"] == "E":
                    conta.valor += valores.cleaned_data["valor"] # form handles the float convertion
                    conta.save()
                    valores.save()
                    messages.add_message(request, constants.SUCCESS, "Entrada Cadastrada com Sucesso")
                
                # caso seja saida validar que exista saldo para realizar saida 
                else:
                    if conta.valor < valores.cleaned_data["valor"]:
                        messages.add_message(request, constants.WARNING, "Saldo insuficiente")
                    else:
                        conta.valor -= valores.cleaned_data["valor"]
                        conta.save()
                        valores.save()

                        messages.add_message(request, constants.SUCCESS, "Saida Cadastrada com Sucesso")  

    return render(request, "novo_valor.html", context)


def view_extrato(request): 

    valores = Valores.objects.all()

    if conta := request.GET.get('conta'):
        valores = valores.filter(conta__id=conta)

    if categoria := request.GET.get('categoria'):
        valores = valores.filter(categoria__id=categoria)

    if periodo := request.GET.get('periodo'):
        match periodo:
            case "7-dias":
                time_limit = timezone.now() - datetime.timedelta(days=7) # mostra registros em datas futuras
                valores = valores.filter(data__gte=time_limit)

            case "15-dias":
                time_limit = timezone.now() - datetime.timedelta(days=15) # mostra registros em datas futuras
                valores = valores.filter(data__gte=time_limit)

            case "mes":
                valores = valores.filter(data__month=timezone.now().month)

            case "3-mes":
                time_limit = timezone.now() - relativedelta(months=3) # mostra registros em datas futuras
                valores = valores.filter(data__gte=time_limit.replace(day=1))

            case "ano":
                valores = valores.filter(data__month=timezone.now().year)

    context = {
        "contas": Conta.objects.all(),
        "categorias": Categoria.objects.all(),
        "valores": valores,
    }
    
    return render(request, 'view_extrato.html', context)

def exportar_pdf(request):
    context = {
        "valores" : Valores.objects.filter(data__month=timezone.now().month),
        "contas" : Conta.objects.all(),
        "categorias" : Categoria.objects.all()
    }

    path_template = os.path.join(settings.PARTIALS_URL, "extrato.html")
    path_output = BytesIO()

    template_render = render_to_string(path_template, context)
    HTML(string=template_render).write_pdf(path_output)

    path_output.seek(0)
 
    return FileResponse(path_output, filename="extrato.pdf")