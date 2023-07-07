from django.shortcuts import render
from perfil.models import Categoria
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from extrato.models import Valores

from perfil.utils import calcula_total
from perfil.models import Categoria

@csrf_exempt
def update_valor_categoria(request):
    
    req = json.load(request)
    try:
        novo_valor = int(req.get("novo_valor"))
        id = int(req.get("id"))
    except:
        return JsonResponse({'status': 'Failed'})

    if categoria := Categoria.objects.get(pk=id):
        categoria.valor_planejado = novo_valor
        categoria.save()

        return JsonResponse({'status': 'Sucesso', "Message":f" New Value is {novo_valor}, and {categoria.valor_planejado}"})
    
    return JsonResponse({'status': 'Failed'})

def definir_planejamento(request):
    return render(request, 'definir_planejamento.html', {"categorias": Categoria.objects.all()})

def ver_planejamento(request):
    categorias = Categoria.objects.all()
    presupuesto = calcula_total(categorias, "valor_planejado")
    
    valores = Valores.objects.filter(tipo="S").filter(data__month=datetime.now().month)
    gastos = calcula_total(valores, "valor")

    try:
        gasto_porcentual = int((gastos * 100) / presupuesto)
    except:
        gasto_porcentual = 0
        
    context = {
        "gasto_porcentual": gasto_porcentual,
        "gastos": gastos,
        "presupuesto": presupuesto,
        'categorias': Categoria.objects.all()
    }

    return render(request, 'ver_planejamento.html', context)