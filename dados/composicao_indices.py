import pandas as pd
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
import os

class ComposicaoIndices:
    IBOV = "IBOV"
    SMLL = "SMLL"
    IFIX = "IFIX"
    
    def __init__(self):
        pass
    
    def __web_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--verbose")
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1920, 1200")
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        return driver

    @staticmethod
    def conserta_setores(setor):
        if setor == 'Cons N  Básico' or setor == 'Cons N Ciclico': return 'Consumo Não-Cíclico'
        if setor == 'Financ e Outros' or setor == 'Financeiro e Outros': return 'Financeiro'
        else: return setor

    def buscar_carteira_teorica(self, indice, espera=8):
        # Listar todos os arquivos na pasta atual
        arquivos_na_pasta = os.listdir()

        # Encontrar o primeiro arquivo .csv na pasta
        csv_encontrado = None
        for arquivo in arquivos_na_pasta:
            if arquivo.startswith(indice) and arquivo.endswith('.csv'):
                csv_encontrado = arquivo
                break

        if not csv_encontrado:
            url = f'https://sistemaswebb3-listados.b3.com.br/indexPage/day/{indice.upper()}?language=pt-br'
            wd = self.__web_driver()
            wd.get(url)
            wd.find_element(By.ID, 'segment').send_keys("Setor de Atuação")
            sleep(espera)
            wd.find_element(By.LINK_TEXT, "Download").click()
            sleep(espera)

        csv_encontrado = None
        for arquivo in arquivos_na_pasta:
            if arquivo.startswith(indice) and arquivo.endswith('.csv'):
                csv_encontrado = arquivo
                break

        # Verificar se um arquivo CSV foi encontrado
        if csv_encontrado:
            # Ler o arquivo CSV em um DataFrame Pandas
            df = pd.read_csv(csv_encontrado, sep=';', encoding='ISO-8859-1', skipfooter=2, engine="python", thousands='.', decimal=',', header=1, index_col=False)
            df["Subsetor"] = df['Setor'].apply(lambda s: s[s.rfind("/")+1:].strip())
            df['Setor'] = df['Setor'].apply(lambda s: s[:s.rfind("/")].strip())
            df['Setor'] = df['Setor'].apply(ComposicaoIndices.conserta_setores)
            # Remover o arquivo CSV
            # os.remove(csv_encontrado)

            # Exibir o DataFrame
            print("DataFrame criado a partir de", csv_encontrado)
            return df
        else:
            print("Nenhum arquivo CSV encontrado na pasta atual.")


# ct = ComposicaoIndices()
# df = ct.buscar_carteira_teorica(ct.IBOV)
# df2 = ct.buscar_carteira_teorica(ct.IFIX)
# print(df.head())
# print(df2.head())