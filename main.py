import streamlit as st
import logging
from dados.fundamentos.fundamentos import Fundamentos

log = logging.getLogger('main')
log.setLevel(logging.DEBUG)

st.set_page_config(layout="wide")

from dados.composicao_indices import ComposicaoIndices

ci = ComposicaoIndices()
ibov = ci.buscar_carteira_teorica(ci.IBOV).head(5)
ifix = ci.buscar_carteira_teorica(ci.IFIX).head(5)
smll = ci.buscar_carteira_teorica(ci.SMLL).head(5)

st.write("Composição IBOV")
st.write(ibov)
st.write("Composição IFIX")
st.write(ifix)
st.write("Composição SMLL")
st.write(smll)

st.write("Dados fundamentalistas de SMLL")
fund = Fundamentos()
dados_fundamentalistas_smll = fund.get_detalhes_lista_acoes(list(smll["Código"]))
st.write(dados_fundamentalistas_smll)


st.write("Dados fundamentalistas de IFIX")
dados_fundamentalistas_ifix = fund.get_detalhes_lista_fiis(list(ifix["Código"]))
st.write(dados_fundamentalistas_ifix)