# estrutura_registros.py

def obter_indices_campos():
    """
    Retorna um dicionário com os índices dos campos relevantes
    para cada tipo de registro usado na comparação SPED x XML.
    """
    return {
        '0150': {
            'cod_part': 2,
            'cnpj': 5,
        },
        'C100': {
            'cod_part': 4,
            'modelo': 5,
            'serie': 7,
            'numero': 8,
        },
        'C500': {
            'cod_part': 4,
            'modelo': 5,
            'serie': 7,
            'numero': 10,
        }
    }
