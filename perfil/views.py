from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import Conta, Categoria
from .forms import ContaForm, CategoriaForm
from .utils import calcula_total, calcula_equilibrio_financeiro, totalPagarMes
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from extrato.models import Valores
from datetime import datetime
from contas.models import ContaPagar , ContaPaga

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()

    for categoria in categorias:
        valores = Valores.objects.filter(categoria=categoria).aggregate(Sum('valor'))['valor__sum']
        dados[categoria.categoria] =  valores if valores is not None else 0 

    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})

def home(request):
    contas = Conta.objects.all()
    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()
    categorias = Categoria.objects.all()
    presupuesto = calcula_total(categorias, "valor_planejado")
    total_pagar_mes = totalPagarMes()

    contas_pagar = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=datetime.now().month).values('conta')
    contas_vencidas = len(contas_pagar.filter(dia_pagamento__lt=datetime.now().day).exclude(id__in=contas_pagas))
    contas_proximas_vencimento = len(contas_pagar.filter(dia_pagamento__lte = datetime.now().day + 5).filter(dia_pagamento__gte=datetime.now().day).exclude(id__in=contas_pagas))
    
    
    
    context = {
        "contas_proximas_vencimento":contas_proximas_vencimento,
        "contas_vencidas":contas_vencidas,
        "contas": contas,
        "presupuesto": presupuesto,
        "libre": presupuesto - total_pagar_mes,
        "percentual_gastos_essenciais": int(percentual_gastos_essenciais),
        "percentual_gastos_nao_essenciais": int(percentual_gastos_nao_essenciais),
        "calcula_total": calcula_total(contas, "valor"),
        "total_entradas" : calcula_total(entradas, 'valor'),
        "total_saidas" : calcula_total(saidas, 'valor'),
        "total_pagar_mes": total_pagar_mes,
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
    