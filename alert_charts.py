import pandas as pd
import plotly.graph_objs as go

def get_indicator(indicator: str, strategy_name: str) -> str:

    formatted_startegy_name = strategy_name.casefold().strip()

    if indicator in formatted_startegy_name:
        return True
    else:
        return False
    

def split_string(input_string):
    result = []

    chunks = input_string.split("-")
    
    current_string = chunks[0]
    
    for part in chunks[1:]:
        # Verificamos si el string actual junto con el próximo fragmento, incluyendo el dash
        # tiene menos de 280 caracteres
        if len(current_string + "-" + part) < 280:
            # Si es así, agregamos el fragmento y el dash al string actual
            current_string += "-" + part
        else:
            # Si supera los 280 caracteres, agregamos el string actual a la lista de resultados
            result.append(current_string)
            # Empezamos un nuevo string con el fragmento actual
            current_string = part

    # Agregamos el último string al resultado
    result.append(current_string)
    
    return result

input_string = """
Bitcoin ATM installations hit two-year low worldwide
- Number of bitcoin ATMs dropped by 17%
- US experienced the biggest decline, now has 26,700 machines
- Europe has only 1,500 machines
- Decline attributed to controversies and criminal use
- Some operators turning off unprofitable ATMs
- Bitcoin Depot sees opportunity for market share growth through acquisitions and retail expansion.
"""
resultados = split_string(input_string)
print(resultados)
