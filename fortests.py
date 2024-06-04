
import re


def jopa(string):
    # Шаблон для скобок с числом и двумя минусами в конце строки
    pattern = r'\(\d+--\)$'
    return re.sub(pattern, '', string)


# Пример использования
ss = "mc_launcher(7214124--)"
s = jopa(ss)
print(s)  # Выведет "mc_launcher"
