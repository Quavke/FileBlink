def separate_file_name_and_extension(file_name):
    extensions_list = []
    base_name = file_name
    s = file_name.split('.')
    with open('file_extensions_complete.txt', 'r') as f:
        extensions = [line.strip() for line in f.readlines()]
        for i in s:
            # print("s:", s, "\n")
            i = "." + i
            for k in extensions:
                if i.lower() == k:
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


a, b = separate_file_name_and_extension("Circle.PnG.Tar.Gz")
print("filename:", a, "| file ext:", b)
