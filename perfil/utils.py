def calcula_total(obj, campo):
    total = 0
    for instance in obj:
        total += getattr(instance, campo)
    return total