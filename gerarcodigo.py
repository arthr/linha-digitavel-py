from datetime import datetime

def modulo_10(num):
    soma = 0
    multiplicador = 2
    for n in reversed(num):
        produto = int(n) * multiplicador
        soma += sum(map(int, str(produto)))
        multiplicador = 1 if multiplicador == 2 else 2
    resto = soma % 10
    return 0 if resto == 0 else 10 - resto

def modulo_11(num):
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = 0
    for i, n in enumerate(reversed(num)):
        peso = pesos[i % len(pesos)]
        soma += int(n) * peso
    resto = soma % 11
    dac = 11 - resto
    return 1 if dac in [0, 1, 10, 11] else dac

def gerar_linha_digitavel(vencimento, valor, carteira, nosso_numero, agencia, conta, dac_nosso_numero, dac_conta):
    banco = '341'
    moeda = '9'

    # Fator de vencimento: Base 03/07/2000 (fator 1000)
    venc_dt = datetime.strptime(vencimento, '%d/%m/%Y')
    base = datetime(2000, 7, 3)
    dias_decorridos = (venc_dt - base).days
    fator = str(dias_decorridos + 1000).zfill(4)
    fator_venc = fator if int(fator) <= 9999 else str(1000 + (int(fator) - 10000))

    # Valor formatado com 10 dígitos (sem vírgula ou ponto)
    valor_formatado = str(int(float(valor) * 100)).zfill(10)

    # Campo livre: Carteira (3) + Nosso Número (8) + DAC Nosso Número (1) +
    # Agência (4) + Conta (5) + DAC Conta (1) + "000"
    campo_livre = f"{carteira}{nosso_numero}{dac_nosso_numero}{agencia.zfill(4)}{conta.zfill(5)}{dac_conta}000"

    # Monta o código de barras sem o DAC (posição 5)
    # O formato é: Banco (3) + Moeda (1) + [DAC] + Fator de Vencimento (4) + Valor (10) + Campo Livre (25)
    # Colocamos temporariamente um marcador "X" no lugar do DAC
    codigo_barras = banco + moeda + 'X' + fator_venc + valor_formatado + campo_livre
    # 341 9 X 1049 0000187024 109 00001719 7 1704 26957 8 000
    
    dac_barras = str(modulo_11(codigo_barras.replace('X', '')))
    
    codigo_barras = codigo_barras.replace('X', dac_barras)

    # Montagem da linha digitável:
    # Campo 1: Posições 1-4 + Posições 20-24 (código de barras) e seu DAC (módulo 10)
    campo1 = codigo_barras[0:4] + codigo_barras[19:24]
    dac1 = str(modulo_10(campo1))
    campo1 = f"{campo1[:5]}.{campo1[5:]}{dac1}"

    # Campo 2: Posições 25-34 do código de barras e seu DAC (módulo 10)
    campo2 = codigo_barras[24:34]
    dac2 = str(modulo_10(campo2))
    campo2 = f"{campo2[:5]}.{campo2[5:]}{dac2}"

    # Campo 3: Posições 35-44 do código de barras e seu DAC (módulo 10)
    campo3 = codigo_barras[34:44]
    dac3 = str(modulo_10(campo3))
    campo3 = f"{campo3[:5]}.{campo3[5:]}{dac3}"

    # Campo 4: DAC do código de barras (já calculado)
    campo4 = dac_barras

    # Campo 5: Fator de vencimento + valor
    campo5 = fator_venc + valor_formatado

    return f"{campo1} {campo2} {campo3} {campo4} {campo5}"

# Teste básico
if __name__ == '__main__':
    vencimento = input("Data de vencimento (dd/mm/yyyy): ")
    valor = input("Valor do título (ex: 123.45): ")
    carteira = input("Carteira (3 dígitos): ")
    nosso_numero = input("Nosso Número (8 dígitos): ")
    dac_nosso_numero = input("DAC Nosso Número (1 dígito): ")
    agencia = input("Agência (até 4 dígitos): ")
    conta = input("Conta Corrente (até 5 dígitos): ")
    dac_conta = input("DAC Conta Corrente (1 dígito): ")

    linha = gerar_linha_digitavel(vencimento, valor, carteira, nosso_numero, agencia, conta, dac_nosso_numero, dac_conta)
    print("\nLinha Digitável:")
    print(linha)
