

def extract_file_info(file_name: str):
    extensions_list = []
    base_name = file_name
    s = file_name.split('.')
    with open('file_extensions_complete.txt', 'r') as f:
        extensions = [line.strip() for line in f.readlines()]
        for i in s:
            # print("s:", s, "\n")
            i = "." + i
            for k in extensions:
                if i == k:
                    # print("i:", i, "\n", "k:", k)
                    extensions_list.append(i)
                    break
    for value in extensions_list:
        base_name = base_name.replace(value, "")
    extensions_str = ''
    for j in extensions_list:
        extensions_str = extensions_str + j
    if extensions_str == '':
        extensions_str = None
    return base_name, extensions_str


file_name = "PrismLauncher-Windows-MSVC-Setup-8.3.exe"
base_name, ex = extract_file_info(file_name)
print("base_name:", base_name)
print("extensions:", ex, str(type(ex)))

# 2. Функция должна работать так: справа налево она читает название. Если она видит точку, то читает всё что было СПРАВА от точки до конца строки ИЛИ до первой точки на своем пути. если то что она прочитала будет цифрой/числом - отправлять это в переменную названия. Если это символы(не цифры) (ЕСЛИ В ТОМ ЧТО ПРОЧИТАЛА ФУНКЦИЯ ЕСТЬ БУКВЫ ИЛИ СПЕЦИАЛЬНЫЕ СИМВОЛЫ, НО ЕСТЬ СРЕДИ НИХ ЦИФРА - ЭТО ВСЁ РАВНО РАСШИРЕНИЕ.) отправлять это в переменную расширения
