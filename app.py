import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import requests
from PIL import Image
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="YouTube Filtros Avançados",
    page_icon="🎥",
    layout="wide"
)

# Configuração da API
API_KEY = "AIzaSyAUYjDb23f1tD2XMR1wWDtupNpK427WHyY"
youtube = build('youtube', 'v3', developerKey=API_KEY)

# CSS customizado para interface estilo YouTube
st.markdown("""
<style>
.main-header {
    font-size: 2rem;
    color: #FF0000;
    text-align: center;
    margin-bottom: 2rem;
}

.channel-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    background-color: #f9f9f9;
}

.channel-title {
    font-size: 1.2rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 5px;
}

.channel-stats {
    color: #666;
    font-size: 0.9rem;
}

.filter-section {
    background-color: #f0f0f0;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

def format_number(num):
    """Formatar números grandes (1M, 1K, etc.)"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def get_channel_details(channel_id):
    """Obter detalhes completos de um canal"""
    try:
        request = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            id=channel_id
        )
        response = request.execute()
        
        if response['items']:
            channel = response['items'][0]
            return {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'][:200] + '...' if len(channel['snippet']['description']) > 200 else channel['snippet']['description'],
                'thumbnail': channel['snippet']['thumbnails']['high']['url'],
                'published_at': channel['snippet']['publishedAt'],
                'subscribers': int(channel['statistics'].get('subscriberCount', 0)),
                'total_views': int(channel['statistics'].get('viewCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'url': f"https://www.youtube.com/channel/{channel['id']}"
            }
    except:
        return None

def search_channels(query, max_results=50, order='relevance'):
    """Buscar canais no YouTube"""
    try:
        request = youtube.search().list(
            part='snippet',
            q=query,
            type='channel',
            maxResults=max_results,
            order=order
        )
        response = request.execute()
        
        channels = []
        for item in response['items']:
            channel_details = get_channel_details(item['snippet']['channelId'])
            if channel_details:
                channels.append(channel_details)
        
        return channels
    except Exception as e:
        st.error(f"Erro na busca: {str(e)}")
        return []

def filter_channels(channels, filters):
    """Aplicar filtros aos canais"""
    filtered = channels.copy()
    
    # Filtro por data de criação
    if filters['date_filter'] != 'Todos':
        now = datetime.now()
        if filters['date_filter'] == 'Última semana':
            cutoff = now - timedelta(days=7)
        elif filters['date_filter'] == 'Último mês':
            cutoff = now - timedelta(days=30)
        elif filters['date_filter'] == 'Últimos 3 meses':
            cutoff = now - timedelta(days=90)
        elif filters['date_filter'] == 'Último ano':
            cutoff = now - timedelta(days=365)
        else:
            cutoff = now - timedelta(days=365*2)
        
        filtered = [ch for ch in filtered if datetime.fromisoformat(ch['published_at'].replace('Z', '+00:00')).replace(tzinfo=None) >= cutoff]
    
    # Filtro por inscritos
    filtered = [ch for ch in filtered if filters['min_subscribers'] <= ch['subscribers'] <= filters['max_subscribers']]
    
    # Filtro por visualizações
    filtered = [ch for ch in filtered if filters['min_views'] <= ch['total_views'] <= filters['max_views']]
    
    # Filtro por número de vídeos
    filtered = [ch for ch in filtered if filters['min_videos'] <= ch['video_count'] <= filters['max_videos']]
    
    return filtered

def sort_channels(channels, sort_by):
    """Ordenar canais"""
    if sort_by == 'Mais recentes':
        return sorted(channels, key=lambda x: x['published_at'], reverse=True)
    elif sort_by == 'Mais antigos':
        return sorted(channels, key=lambda x: x['published_at'])
    elif sort_by == 'Mais inscritos':
        return sorted(channels, key=lambda x: x['subscribers'], reverse=True)
    elif sort_by == 'Menos inscritos':
        return sorted(channels, key=lambda x: x['subscribers'])
    elif sort_by == 'Mais visualizações':
        return sorted(channels, key=lambda x: x['total_views'], reverse=True)
    elif sort_by == 'Mais vídeos':
        return sorted(channels, key=lambda x: x['video_count'], reverse=True)
    else:
        return channels

def display_channel_card(channel):
    """Exibir card do canal estilo YouTube"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Thumbnail
        try:
            response = requests.get(channel['thumbnail'])
            img = Image.open(BytesIO(response.content))
            st.image(img, width=150)
        except:
            st.image("https://via.placeholder.com/150x150?text=No+Image", width=150)
    
    with col2:
        # Informações do canal
        st.markdown(f"""
        <div class="channel-card">
            <div class="channel-title">{channel['title']}</div>
            <div class="channel-stats">
                📺 {format_number(channel['subscribers'])} inscritos | 
                👁️ {format_number(channel['total_views'])} visualizações | 
                🎬 {channel['video_count']} vídeos
            </div>
            <div class="channel-stats">
                📅 Criado em: {datetime.fromisoformat(channel['published_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y')}
            </div>
            <p style="color: #666; font-size: 0.85rem; margin-top: 8px;">
                {channel['description']}
            </p>
            <a href="{channel['url']}" target="_blank" style="color: #FF0000; text-decoration: none;">
                🔗 Visitar Canal
            </a>
        </div>
        """, unsafe_allow_html=True)

# Interface principal
st.markdown('<h1 class="main-header">🎥 YouTube Filtros Avançados</h1>', unsafe_allow_html=True)

# Sidebar com filtros
st.sidebar.markdown("## 🔍 Filtros Avançados")

# Busca básica
search_query = st.sidebar.text_input("🔎 Buscar por:", placeholder="Ex: tecnologia, culinária, música...")

# Filtros de data
date_filter = st.sidebar.selectbox(
    "📅 Canais criados:",
    ['Todos', 'Última semana', 'Último mês', 'Últimos 3 meses', 'Último ano', 'Mais de 2 anos']
)

# Filtros numéricos
st.sidebar.markdown("### 👥 Número de Inscritos")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_subscribers = st.number_input("Mínimo", min_value=0, value=0, step=1000)
with col2:
    max_subscribers = st.number_input("Máximo", min_value=0, value=10000000, step=1000)

st.sidebar.markdown("### 👁️ Visualizações Totais")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_views = st.number_input("Mínimo ", min_value=0, value=0, step=10000)
with col2:
    max_views = st.number_input("Máximo ", min_value=0, value=1000000000, step=10000)

st.sidebar.markdown("### 🎬 Número de Vídeos")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_videos = st.number_input("Mín vídeos", min_value=0, value=0, step=10)
with col2:
    max_videos = st.number_input("Máx vídeos", min_value=0, value=10000, step=10)

# Ordenação
sort_by = st.sidebar.selectbox(
    "📊 Ordenar por:",
    ['Relevância', 'Mais recentes', 'Mais antigos', 'Mais inscritos', 'Menos inscritos', 'Mais visualizações', 'Mais vídeos']
)

# Botão de busca
search_button = st.sidebar.button("🚀 BUSCAR CANAIS", type="primary")

# Área principal
if search_button and search_query:
    with st.spinner('🔍 Buscando canais...'):
        # Realizar busca
        raw_channels = search_channels(search_query, max_results=50)
        
        if raw_channels:
            # Aplicar filtros
            filters = {
                'date_filter': date_filter,
                'min_subscribers': min_subscribers,
                'max_subscribers': max_subscribers,
                'min_views': min_views,
                'max_views': max_views,
                'min_videos': min_videos,
                'max_videos': max_videos
            }
            
            filtered_channels = filter_channels(raw_channels, filters)
            
            if filtered_channels:
                # Ordenar resultados
                sorted_channels = sort_channels(filtered_channels, sort_by)
                
                # Mostrar estatísticas
                st.markdown(f"### 📊 Encontrados: {len(sorted_channels)} canais")
                
                # Botão de export
                if st.button("📥 Exportar Resultados (CSV)"):
                    df = pd.DataFrame(sorted_channels)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"canais_youtube_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Exibir resultados
                st.markdown("---")
                for channel in sorted_channels:
                    display_channel_card(channel)
                    st.markdown("---")
            else:
                st.warning("❌ Nenhum canal encontrado com esses filtros. Tente critérios menos restritivos.")
        else:
            st.error("❌ Nenhum canal encontrado. Tente uma busca diferente.")

elif search_button and not search_query:
    st.warning("⚠️ Digite algo para buscar!")

else:
    # Tela inicial
    st.markdown("""
    ## 🎯 Como usar:
    
    1. **Digite sua busca** na barra lateral (ex: "tecnologia", "culinária")
    2. **Configure os filtros avançados** que não existem no YouTube:
       - Data de criação do canal
       - Faixa de inscritos
       - Número de visualizações
       - Quantidade de vídeos
    3. **Escolha a ordenação** (mais recentes, mais antigos, etc.)
    4. **Clique em BUSCAR** para ver os resultados
    5. **Exporte** os dados em CSV se quiser
    
    ### 🚀 Funcionalidades exclusivas:
    - ✅ Filtrar por data exata de criação do canal
    - ✅ Combinar múltiplos critérios simultaneamente
    - ✅ Ordenações que o YouTube não oferece
    - ✅ Interface visual com thumbnails e estatísticas
    - ✅ Export de dados para análise
    
    **Comece digitando sua busca na barra lateral! 👈**
    """)
