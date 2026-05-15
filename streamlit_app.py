import streamlit as st
from datetime import datetime, date
from pathlib import Path
import json

# Configuração da página
st.set_page_config(
    page_title="Repositório de Links por Adversário",
    page_icon="📁",
    layout="wide"
)

DATA_FILE = Path(__file__).resolve().parent / "adversarios.json"


def carregar_adversarios_do_json(caminho_json):
    """Carrega os adversários a partir de um arquivo JSON."""
    try:
        with open(caminho_json, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        st.error(f"Arquivo de dados não encontrado: {caminho_json}")
        return []
    except json.JSONDecodeError:
        st.error(f"Erro ao decodificar o JSON em: {caminho_json}")
        return []


adversarios_data = carregar_adversarios_do_json(DATA_FILE)

def converter_data_string_para_date(data_string):
    """Converte string de data (YYYY-MM-DD ou DD/MM/YYYY) para objeto date"""
    try:
        if '-' in data_string:
            return datetime.strptime(data_string, "%Y-%m-%d").date()
        else:
            return datetime.strptime(data_string, "%d/%m/%Y").date()
    except ValueError:
        return None

def formatar_data_para_exibicao(data_obj):
    """Formata objeto date para string DD/MM/YYYY"""
    return data_obj.strftime("%d/%m/%Y")

def encontrar_proximo_adversario(adversarios):
    """
    Encontra o próximo adversário baseado na data atual.
    Retorna o índice do adversário ou 0 se não houver jogos futuros.
    """
    data_atual = date.today()

    # Converte datas e adiciona ao dicionário
    for i, adversario in enumerate(adversarios):
        adversario['data_obj'] = converter_data_string_para_date(adversario['data_jogo'])

    # Ordena por data crescente
    adversarios_ordenados = sorted(adversarios, key=lambda x: x['data_obj'])

    # Encontra o primeiro jogo futuro ou igual à data atual
    for i, adversario in enumerate(adversarios_ordenados):
        if adversario['data_obj'] >= data_atual:
            return adversarios_ordenados, i

    # Se não há jogos futuros, retorna o último jogo
    return adversarios_ordenados, len(adversarios_ordenados) - 1

def inicializar_session_state(adversarios_ordenados, indice_inicial):
    """Inicializa o session state com os dados necessários"""
    if 'adversarios' not in st.session_state:
        st.session_state.adversarios = adversarios_ordenados
    if 'indice_atual' not in st.session_state:
        st.session_state.indice_atual = indice_inicial
    if 'total_adversarios' not in st.session_state:
        st.session_state.total_adversarios = len(adversarios_ordenados)

def navegar_anterior():
    """Navega para o adversário anterior"""
    if st.session_state.indice_atual > 0:
        st.session_state.indice_atual -= 1

def navegar_proximo():
    """Navega para o próximo adversário"""
    if st.session_state.indice_atual < st.session_state.total_adversarios - 1:
        st.session_state.indice_atual += 1

def exibir_adversario(adversario):
    """Exibe as informações do adversário atual"""
    data_formatada = formatar_data_para_exibicao(adversario['data_obj'])
    data_atual = date.today()

    # Determina se o jogo já aconteceu ou vai acontecer
    status_jogo = "🔴 Jogo realizado" if adversario['data_obj'] < data_atual else "🟢 Próximo jogo"

    # Card principal do adversário
    st.markdown(f"""
    <div style="
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
        margin: 10px 0;
    ">
        <h2 style="margin: 0; color: #1f1f1f;">⚽ {adversario['nome']}</h2>
        <p style="margin: 5px 0; color: #666;"><strong>Data:</strong> {data_formatada} | {status_jogo}</p>
        <p style="margin: 5px 0; color: #666;"><strong>Campeonato:</strong> {adversario['campeonato']}</p>
        <p style="margin: 5px 0; color: #666;"><strong>Local:</strong> {adversario['local_jogo']}</p>
        <p style="margin: 5px 0; color: #666;"><strong>Placar:</strong> {adversario['placar']}</p>
    </div>
    """, unsafe_allow_html=True)

def exibir_links(links):
    """Exibe os links organizados por categoria"""
    if not links:
        st.info("📝 Nenhum link disponível para este adversário.")
        return

    st.subheader("🔗 Links Organizados")

    # Agrupa links por categoria
    categorias = {}
    for link in links:
        categoria = link['categoria']
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append(link)

    # Exibe links por categoria em colunas
    for categoria, links_categoria in categorias.items():
        with st.expander(f"📂 {categoria} ({len(links_categoria)} links)", expanded=True):
            # Divide em colunas se houver muitos links
            if len(links_categoria) > 2:
                cols = st.columns(2)
                for i, link in enumerate(links_categoria):
                    with cols[i % 2]:
                        st.markdown(f"🔗 [{link['descricao']}]({link['url']})")
            else:
                for link in links_categoria:
                    st.markdown(f"🔗 [{link['descricao']}]({link['url']})")

def main():
    """Função principal do aplicativo"""

    # Título principal
    st.markdown("""
    <h1 style="text-align: center; color: #1f1f1f; margin-bottom: 30px;">
        📁 Repositório de Links por Adversário
    </h1>
    """, unsafe_allow_html=True)

    # Informações sobre o app
    with st.expander("ℹ️ Como usar este aplicativo", expanded=False):
        st.markdown("""
        - **Navegação automática**: O app mostra automaticamente o próximo jogo baseado na data atual
        - **Botões de navegação**: Use "◀ Anterior" e "Próximo ▶" para navegar entre adversários
        - **Salto rápido**: Use o seletor abaixo para ir diretamente a um adversário específico
        - **Links organizados**: Os links são agrupados por categoria (Gols, Bola parada, Movimentações, etc.)
        """)

    # Verifica se os dados foram carregados corretamente
    if not adversarios_data:
        st.warning("Nenhum adversário foi carregado. Verifique o arquivo adversarios.json e tente novamente.")
        return

    # Processa dados e encontra próximo adversário
    adversarios_ordenados, indice_inicial = encontrar_proximo_adversario(adversarios_data.copy())

    # Inicializa session state
    inicializar_session_state(adversarios_ordenados, indice_inicial)

    # Seção de navegação
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.button(
            "◀ Anterior", 
            on_click=navegar_anterior,
            disabled=st.session_state.indice_atual == 0,
            use_container_width=True
        )

    with col2:
        # Selectbox para salto rápido
        nomes_adversarios = [f"{adv['nome']} ({formatar_data_para_exibicao(adv['data_obj'])})" 
                           for adv in st.session_state.adversarios]

        indice_selecionado = st.selectbox(
            "🎯 Saltar para adversário:",
            range(len(nomes_adversarios)),
            index=st.session_state.indice_atual,
            format_func=lambda x: nomes_adversarios[x],
            key="selectbox_adversario"
        )

        # Atualiza índice se seleção mudou
        if indice_selecionado != st.session_state.indice_atual:
            st.session_state.indice_atual = indice_selecionado

    with col3:
        st.button(
            "Próximo ▶", 
            on_click=navegar_proximo,
            disabled=st.session_state.indice_atual == st.session_state.total_adversarios - 1,
            use_container_width=True
        )

    # Indicador de posição
    st.markdown(f"""
    <div style="text-align: center; margin: 10px 0; color: #666;">
        Adversário {st.session_state.indice_atual + 1} de {st.session_state.total_adversarios}
    </div>
    """, unsafe_allow_html=True)

    # Exibe adversário atual
    adversario_atual = st.session_state.adversarios[st.session_state.indice_atual]

    # Divide em duas colunas: informações do adversário e links
    col_info, col_links = st.columns([1, 1])

    with col_info:
        exibir_adversario(adversario_atual)

    with col_links:
        exibir_links(adversario_atual['links'])

    # Rodapé com informações adicionais
    st.markdown("---")
    data_atual = date.today().strftime("%d/%m/%Y")
    st.markdown(f"📅 **Data atual:** {data_atual}")

    # Estatísticas rápidas
    jogos_futuros = sum(1 for adv in st.session_state.adversarios if adv['data_obj'] >= date.today())
    jogos_passados = st.session_state.total_adversarios - jogos_futuros

    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("🟢 Jogos Futuros", jogos_futuros)
    with col_stats2:
        st.metric("🔴 Jogos Passados", jogos_passados)
    with col_stats3:
        st.metric("📊 Total de Adversários", st.session_state.total_adversarios)

if __name__ == "__main__":
    main()