from io import StringIO
from typing import List
from bs4 import BeautifulSoup
import pandas as pd
import requests
from .utils import perc_to_float
import fundamentus as fd

import logging
log = logging.getLogger('Fundamentos')
log.setLevel(logging.DEBUG)

class Fundamentos:
    """
    Classe que implementa melhorias na biblioteca Fundamentus.
    """

    hdr = {
        "User-agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201",
        "Accept": "text/html, text/plain, text/css, text/sgml, */*;q=0.01",
        "Accept-Encoding": "gzip, deflate",
    }

    def get_df_setores(self) -> pd.DataFrame:
        url = "https://www.fundamentus.com.br/buscaavancada.php"
        response = requests.get(url, headers=self.hdr)
        soup = BeautifulSoup(response.text, "html.parser")
        select = soup.find("select", {"name": "setor"})
        options = select.find_all("option")

        options_list = []
        for option in options:
            option_value = option.get("value")
            option_text = option.text
            if option_value and option_text:
                options_list.append(option_value + " - " + option_text)

        df = pd.DataFrame(options_list, columns=["Setor"])
        return df

    def get_df_acoes_do_setor(self, id_setor) -> pd.DataFrame:
        """
        Retorna uma lista de ações de um determinado setor. 
        """
        
        df = fd.list_papel_setor(id_setor)
        return df

    def get_df_fiis(self) -> pd.DataFrame:
        """
        Retorna uma DataFrame de dados fundamentalistas de FII. 
        """
                
        url = "https://www.fundamentus.com.br/fii_resultado.php"
        content = requests.get(url, headers=self.hdr)
        df = pd.read_html(
            StringIO(content.text), decimal=",", thousands=".", attrs={"id": "tabelaResultado"}
        )[0]

        df["Dividend Yield"] = perc_to_float(df["Dividend Yield"])
        df["FFO Yield"] = perc_to_float(df["FFO Yield"])
        df["Cap Rate"] = perc_to_float(df["Cap Rate"])
        df["Vacância Média"] = perc_to_float(df["Vacância Média"])

        return df

    def get_df_acoes(self) -> pd.DataFrame:
        """
        Retorna uma DataFrame de dados fundamentalistas de Ações. 
        """
        
        url = "https://www.fundamentus.com.br/resultado.php"
        content = requests.get(url, headers=self.hdr)
        df = pd.read_html(
            StringIO(content.text), decimal=",", thousands=".", attrs={"id": "resultado"}
        )[0]

        df["Div.Yield"] = perc_to_float(df["Div.Yield"])
        df["Mrg Ebit"] = perc_to_float(df["Mrg Ebit"])
        df["Mrg. Líq."] = perc_to_float(df["Mrg. Líq."])
        df["ROIC"] = perc_to_float(df["ROIC"])
        df["ROE"] = perc_to_float(df["ROE"])
        df["Cresc. Rec.5a"] = perc_to_float(df["Cresc. Rec.5a"])

        return df

    def get_df_detalhes_acao(self, ticker: str) -> pd.DataFrame | None:
        """
        Retorna uma DataFrame de dados (mais completo) fundamentalistas de uma determinada Ação. 
        """
        
        ticker = ticker.upper()
        logging.debug(f"Buscando dados de {ticker}")
                       
        url = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker}"
        try:
            content = requests.get(url, headers=self.hdr)
            html = pd.read_html(
                StringIO(content.text), decimal=",", thousands=".", attrs={"class": "w728"}
            )
            
            df1 = html[0]
            temp1 = df1[[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp2 = df1[[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            df1 = pd.concat([temp1, temp2], ignore_index=True) 

            df2 = html[1]
            temp1 = df2[[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp2 = df2[[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            df2 = pd.concat([temp1, temp2], ignore_index=True) 
            
            df3 = html[2]
            temp1 = df3.iloc[1:][[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp1["Chave"] = "Oscilações " + temp1["Chave"] 
            temp2 = df3.iloc[1:][[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            temp3 = df3.iloc[1:][[4, 5]].copy()
            temp3.columns = ['Chave', 'Valor']
            df3 = pd.concat([temp1, temp2, temp3], ignore_index=True) 
            
            df4 = html[3]
            temp1 = df4.iloc[1:][[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp2 = df4.iloc[1:][[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            df4 = pd.concat([temp1, temp2], ignore_index=True) 
            
            df5 = html[4]
            temp1 = df5.iloc[1:][[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp1["Chave"] = "Últimos 12 meses " + temp1["Chave"] 
        
            temp2 = df5.iloc[1:][[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            temp2["Chave"] = "Últimos 3 meses " + temp2["Chave"] 
            df5 = pd.concat([temp1, temp2], ignore_index=True)     
            
            df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)
            df["Chave"] = df["Chave"].str.replace("?", "")
            df = df.set_index('Chave')

            df.dropna(inplace=True)
            
            df = df.T
            df = df.set_index('Papel')
            return df
        except Exception:
            logging.warn(f"Erro ao buscar dados de {ticker}")
            return None

    def get_detalhes_fii(self, ticker: str) -> pd.DataFrame | None :
        """
        Retorna uma DataFrame de dados (mais completo) fundamentalistas de um determinado FII. 
        """

        ticker = ticker.upper()
        logging.debug(f"Buscando dados de {ticker}")
                
        ticker = ticker.upper()
        url = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker}"
        
        try:
            content = requests.get(url, headers=self.hdr)
            html = pd.read_html(
                StringIO(content.text), decimal=",", thousands=".", attrs={"class": "w728"}
            )
            
            df1 = html[0]
            temp1 = df1[[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp2 = df1[[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            df1 = pd.concat([temp1, temp2], ignore_index=True) 
            
            df2 = html[1]
            temp1 = df2[[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp2 = df2[[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            df2 = pd.concat([temp1, temp2], ignore_index=True)     
            
            df3 = html[2]
            temp1 = df3.iloc[1:][[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp1["Chave"] = "Oscilações " + temp1["Chave"] 

            temp2 = df3.iloc[1:4][[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            
            temp3 = df3.iloc[1:4][[4, 5]].copy()
            temp3.columns = ['Chave', 'Valor']
            
            temp4 = df3.iloc[6:9][[2, 3]].copy()
            temp4.columns = ['Chave', 'Valor']
            temp4["Chave"] = "Últimos 12 meses " + temp4["Chave"]     
            
            temp5 = df3.iloc[6:9][[4, 5]].copy()
            temp5.columns = ['Chave', 'Valor']
            temp5["Chave"] = "Últimos 3 meses " + temp5["Chave"]     
            
            temp6 = df3.iloc[11:][[2, 3]].copy()
            temp6.columns = ['Chave', 'Valor']
            
            temp7 = df3.iloc[11:][[4, 5]].copy()
            temp7.columns = ['Chave', 'Valor']
            
            df3 = pd.concat([temp1, temp2, temp3, temp4, temp5, temp6, temp7], ignore_index=True) 

            df4 = html[4]
            temp1 = df4.iloc[1:][[0, 1]].copy()
            temp1.columns = ['Chave', 'Valor']
            temp2 = df4.iloc[1:][[2, 3]].copy()
            temp2.columns = ['Chave', 'Valor']
            df4 = pd.concat([temp1, temp2], ignore_index=True)     
            
            df = pd.concat([df1, df2, df3, df4], ignore_index=True)
            df["Chave"] = df["Chave"].str.replace("?", "")
            df = df.set_index('Chave')

            df.dropna(inplace=True)
            
            df = df.T
            df = df.set_index('FII')
            return df
        except Exception:
            logging.warn(f"Erro ao buscar dados de {ticker}")    
            return None        

    def get_detalhes_lista_acoes(self, lista_tickers: list[str]) -> pd.DataFrame:
        """
        Retorna uma DataFrame de dados (mais completo) fundamentalistas de uma lista de Ações. 
        """
                
        resultado = []
        for t in lista_tickers:
            r = self.get_df_detalhes_acao(t)
            if r is not None:
                resultado.append(r.reset_index())
        
        df = pd.concat(resultado, ignore_index=True)
        df = df.set_index('Papel')
        df.dropna(inplace=True)
        return df

    def get_detalhes_lista_fiis(self, lista_tickers: list[str]) -> pd.DataFrame:
        """
        Retorna uma DataFrame de dados (mais completo) fundamentalistas de uma lista de FIIs. 
        """
        
        resultado = []
        for t in lista_tickers:
            r = self.get_detalhes_fii(t)
            if r is not None:
                resultado.append(r.reset_index())
        
        df = pd.concat(resultado, ignore_index=True)
        df = df.set_index('FII')
        df.dropna(inplace=True)
        return df