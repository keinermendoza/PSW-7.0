from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import Conta, Categoria
from .forms import ContaForm, CategoriaForm
from .utils import calcula_total
from django.contrib import messages
from django.contrib.messages import constants
# from django.db.models import Sum

# Create your views here.
def home(request):
    contas = Conta.objects.all()
    context = {
        "contas": contas,
        "calcula_total": calcula_total(contas, "valor")
    }
    return render(request,"home.html", context)

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    context = {
        "contas":contas,
        "categorias": categorias,
        "total_contas": sum([conta.valor for conta in contas]) # total_contas = contas.aggregate(Sum("valor"))["valor__sum"]
    }
    return render(request, "gerenciar.html", context)

def cadastrar_banco(request):
    conta = ContaForm(request.POST, request.FILES)

    if conta.is_valid():
        messages.add_message(request, constants.SUCCESS, "Conta Cadastrada com Sucesso")
        conta.save()
    else:
        for campo, listadeErrosPorCampo in conta.errors.items():
            for eachError in listadeErrosPorCampo:
                error = f"Error en {campo}: {eachError}"
                break # for take just the first error

        # also it's possible show every error in one separate message repleacing "error" by "messages.add..."" etc
        messages.add_message(request, constants.WARNING, error)
    return redirect(reverse("gerenciar"))

def deletar_banco(request, conta_id):
    if conta := Conta.objects.get(pk=conta_id):
        conta.delete()
        messages.add_message(request, constants.INFO, "Conta deletada com Successo")
    else:
        messages.add_message(request, constants.ERROR, "Conta Nao Valida")
    return redirect(reverse("gerenciar"))

def cadastrar_categoria(request):
    categoria = CategoriaForm(request.POST)
    if categoria.is_valid(): # pra fazer isso e preciso agregar a propiedade blank=False, veja models.py linha 7
        categoria.save()
        messages.add_message(request, constants.SUCCESS, f"Categoria {(categoria.cleaned_data['categoria']).capitalize()} Cadastrada com Sucesso")
    else:
        campo, listaErrosCampo = list(categoria.errors.items())[0] # um jeito mais curto
        messages.add_message(request, constants.ERROR, f"Erro em {campo}: {listaErrosCampo[0]}")
    return redirect(reverse("gerenciar"))

def update_categoria(request, categoria_id):
    if categoria := Categoria.objects.get(pk=categoria_id):
        categoria.essencial = not categoria.essencial
        categoria.save()
    return redirect(reverse("gerenciar"))
    