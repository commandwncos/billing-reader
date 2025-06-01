import re  
  
def modulo10(numero):  
    soma = 0  
    peso = 2  
    for digito in reversed(numero):  
        multiplicacao = int(digito) * peso  
        soma += multiplicacao if multiplicacao < 10 else multiplicacao - 9  
        peso = 1 if peso == 2 else 2  
    return (10 - (soma % 10)) % 10  
  
def modulo11_banco(numero):  
    soma = 0  
    peso = 2  
    for digito in reversed(numero):  
        soma += int(digito) * peso  
        peso = 2 if peso == 9 else peso + 1  
    digito = 11 - (soma % 11)  
    if digito > 9 or digito in [0, 1]:  
        return 1  
    return digito  
  
def calcula_linha(barra):  
    # Remove caracteres não numéricos  
    linha = re.sub(r'\D', '', barra)  
      
    if len(linha) != 44:  
        return None  
  
    # Utiliza regex para capturar os campos necessários com f-strings  
    campo1 = f"{linha[:4]}{linha[19]}.{linha[20:24]}"  
    campo2 = f"{linha[24:29]}.{linha[29:34]}"  
    campo3 = f"{linha[34:39]}.{linha[39:44]}"  
    campo4 = linha[4]  
    campo5 = linha[5:19]  
  
    if modulo11_banco(linha[0:4] + linha[5:44]) != int(campo4):  
        return None  
  
    linha_digitavel = f"{campo1}{modulo10(campo1.replace('.', ''))} " \
                      f"{campo2}{modulo10(campo2.replace('.', ''))} " \
                      f"{campo3}{modulo10(campo3.replace('.', ''))} " \
                      f"{campo4} {campo5}"  
      
    return linha_digitavel  
