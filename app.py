import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import requests
from PIL import Image
from io import BytesIO
import re

# Configuração da página
st.set_page_config(
    page_title="YouTube Explorer Pro",
    page_icon="🚀",
    layout="wide"
)

# Configuração da API
API_KEY = "AIzaSyAUYjDb23f1tD2XMR1wWDtupNpK427WHyY"
youtube = build('youtube', 'v3', developerKey=API_KEY)

# CSS customizado
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #FF0000;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.video-card {
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 15px;
    margin: 15px 0;
    background: linear-gradient(135deg, #f9f9f9 0%, #ffffff 100%);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.video-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.video-title {
    font-size: 1.3rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 8px;
    line-height: 1.3;
}

.channel-info {
    color: #666;
    font-size: 1rem;
    margin-bottom: 5px;
}

.video-stats {
    color: #0066cc;
    font-size: 0.9rem;
    font-weight: 600;
}

.trending-badge {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: 10px;
}

.new-channel-badge {
    background: linear-gradient(45deg, #A8E6CF, #88D8A3);
    color: #2d5a3d;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: 5px;
}

.filter-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}

.metric-container {
    background: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

def format_number(num):
    """Formatar números grandes"""
    if num >= 1000000000:
        return f"{num/1000000000:.1f}B"
    elif num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def parse_duration(duration):
    """Converter duração ISO 8601 para segundos"""
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
    if not match:
        return 0
    
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    
    return hours * 3600 + minutes * 60 + seconds

def format_duration(seconds):
    """Formatar duração em formato legível"""
    if seconds >= 3600:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    elif seconds >= 60:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        return f"{seconds}s"

def get_channel_age_days(channel_id):
    """Calcular idade do canal em dias"""
    try:
        request = youtube.channels().list(part='snippet', id=channel_id)
        response = request.execute()
        if response['items']:
            published_at = response['items'][0]['snippet']['publishedAt']
            created_date = datetime.fromisoformat(published_at.replace('Z', '+00:00')).replace(tzinfo=None)
            return (datetime.now() - created_date).days
    except:
        pass
    return 9999  # Valor alto para canais que não conseguimos verificar

def search_videos(query, max_results=50, published_after=None, order='relevance'):
    """Buscar vídeos no YouTube"""
    try:
        search_params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'order': order,
            'regionCode': 'BR',  # Priorizar conteúdo brasileiro
            'relevanceLanguage': 'pt'
        }
        
        if published_after:
            search_params['publishedAfter'] = published_after.isoformat() + 'Z'
        
        request = youtube.search().list(**search_params)
        response = request.execute()
        
        # Obter IDs dos vídeos para buscar estatísticas
        video_ids = [item['id']['videoId'] for item in response['items']]
        
        if not video_ids:
            return []
        
        # Buscar detalhes dos vídeos (estatísticas, duração)
        stats_request = youtube.videos().list(
            part='statistics,contentDetails',
            id=','.join(video_ids)
        )
        stats_response = stats_request.execute()
        
        # Combinar dados
        videos = []
        for i, item in enumerate(response['items']):
            video_stats = next((v for v in stats_response['items'] if v['id'] == item['id']['videoId']), None)
            
            if video_stats:
                # Calcular idade do canal
                channel_age_days = get_channel_age_days(item['snippet']['channelId'])
                
                video_data = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'channel_title': item['snippet']['channelTitle'],
                    'channel_id': item['snippet']['channelId'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'description': item['snippet']['description'][:300] + '...' if len(item['snippet']['description']) > 300 else item['snippet']['description'],
                    'views': int(video_stats['statistics'].get('viewCount', 0)),
                    'likes': int(video_stats['statistics'].get('likeCount', 0)),
                    'comments': int(video_stats['statistics'].get('commentCount', 0)),
                    'duration_seconds': parse_duration(video_stats['contentDetails']['duration']),
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    'channel_url': f"https://www.youtube.com/channel/{item['snippet']['channelId']}",
                    'channel_age_days': channel_age_days
                }
                
                # Calcular engagement rate
                if video_data['views'] > 0:
                    video_data['engagement_rate'] = ((video_data['likes'] + video_data['comments']) / video_data['views']) * 100
                else:
                    video_data['engagement_rate'] = 0
                
                videos.append(video_data)
        
        return videos
    
    except Exception as e:
        st.error(f"Erro na busca: {str(e)}")
        return []

def filter_videos(videos, filters):
    """Aplicar filtros aos vídeos"""
    filtered = videos.copy()
    
    # Filtro por visualizações
    filtered = [v for v in filtered if filters['min_views'] <= v['views'] <= filters['max_views']]
    
    # Filtro por likes
    if filters['min_likes'] > 0:
        filtered = [v for v in filtered if v['likes'] >= filters['min_likes']]
    
    # Filtro por duração
    if filters['min_duration'] > 0 or filters['max_duration'] < 7200:
        filtered = [v for v in filtered if filters['min_duration'] <= v['duration_seconds'] <= filters['max_duration']]
    
    # Filtro por idade do canal (NOVO!)
    if filters['max_channel_age_days'] < 9999:
        filtered = [v for v in filtered if v['channel_age_days'] <= filters['max_channel_age_days']]
    
    # Filtro por engagement rate
    if filters['min_engagement'] > 0:
        filtered = [v for v in filtered if v['engagement_rate'] >= filters['min_engagement']]
    
    # Filtro por data de publicação do vídeo
    if filters['video_max_age_days'] < 9999:
        cutoff_date = datetime.now() - timedelta(days=filters['video_max_age_days'])
        filtered = [v for v in filtered if datetime.fromisoformat(v['published_at'].replace('Z', '+00:00')).replace(tzinfo=None) >= cutoff_date]
    
    return filtered

def sort_videos(videos, sort_by):
    """Ordenar vídeos"""
    if sort_by == 'Mais recentes':
        return sorted(videos, key=lambda x: x['published_at'], reverse=True)
    elif sort_by == 'Mais antigos':
        return sorted(videos, key=lambda x: x['published_at'])
    elif sort_by == 'Mais visualizações':
        return sorted(videos, key=lambda x: x['views'], reverse=True)
    elif sort_by == 'Menos visualizações':
        return sorted(videos, key=lambda x: x['views'])
    elif sort_by == 'Mais likes':
        return sorted(videos, key=lambda x: x['likes'], reverse=True)
    elif sort_by == 'Maior engagement':
        return sorted(videos, key=lambda x: x['engagement_rate'], reverse=True)
    elif sort_by == 'Canais mais novos':
        return sorted(videos, key=lambda x: x['channel_age_days'])
    elif sort_by == 'Duração (menor)':
        return sorted(videos, key=lambda x: x['duration_seconds'])
    elif sort_by == 'Duração (maior)':
        return sorted(videos, key=lambda x: x['duration_seconds'], reverse=True)
    else:
        return videos

def is_trending_video(video, min_views_for_trending=10000):
    """Verificar se é um vídeo em tendência"""
    days_old = (datetime.now() - datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).replace(tzinfo=None)).days
    if days_old <= 7 and video['views'] >= min_views_for_trending:
        return True
    return False

def is_new_channel(video, max_age_days=365):
    """Verificar se é canal novo"""
    return video['channel_age_days'] <= max_age_days

def display_video_card(video, show_badges=True):
    """Exibir card do vídeo estilo YouTube melhorado"""
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        # Thumbnail do vídeo
        try:
            response = requests.get(video['thumbnail'])
            img = Image.open(BytesIO(response.content))
            st.image(img, width=200)
        except:
            st.image("https://via.placeholder.com/320x180?text=No+Thumbnail", width=200)
        
        # Duração
        st.markdown(f"**⏱️ {format_duration(video['duration_seconds'])}**")
    
    with col2:
        # Badges
        badges_html = ""
        if show_badges:
            if is_trending_video(video):
                badges_html += '<span class="trending-badge">🔥 TRENDING</span>'
            if is_new_channel(video):
                badges_html += '<span class="new-channel-badge">✨ CANAL NOVO</span>'
        
        # Informações do vídeo
        published_date = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).strftime('%d/%m/%Y')
        days_old = (datetime.now() - datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).replace(tzinfo=None)).days
        
        st.markdown(f"""
        <div class="video-card">
            <div class="video-title">{video['title']} {badges_html}</div>
            <div class="channel-info">
                📺 <strong>{video['channel_title']}</strong> 
                <span style="color: #999;">• Canal criado há {video['channel_age_days']} dias</span>
            </div>
            <div class="video-stats">
                👁️ {format_number(video['views'])} views • 
                👍 {format_number(video['likes'])} likes • 
                💬 {format_number(video['comments'])} comentários • 
                📈 {video['engagement_rate']:.2f}% engagement
            </div>
            <div style="color: #666; font-size: 0.85rem; margin: 8px 0;">
                📅 Publicado em {published_date} ({days_old} dias atrás)
            </div>
            <p style="color: #666; font-size: 0.85rem; margin-top: 8px;">
                {video['description']}
            </p>
            <div style="margin-top: 10px;">
                <a href="{video['url']}" target="_blank" style="color: #FF0000; text-decoration: none; margin-right: 15px;">
                    🎥 Assistir Vídeo
                </a>
                <a href="{video['channel_url']}" target="_blank" style="color: #0066cc; text-decoration: none;">
                    📺 Ver Canal
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Interface principal
st.markdown('<h1 class="main-header">🚀 YouTube Explorer Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Encontre vídeos em alta de canais novos - Descubra tendências antes de todo mundo!</p>', unsafe_allow_html=True)

# Sidebar com filtros avançados
st.sidebar.markdown("## 🎯 Filtros Avançados")

# Busca básica
search_query = st.sidebar.text_input("🔎 Buscar por:", placeholder="Ex: react, receitas, investimentos...")

# Seção: Filtros de Conteúdo
st.sidebar.markdown("### 🎬 Filtros de Vídeo")

# Visualizações
col1, col2 = st.sidebar.columns(2)
with col1:
    min_views = st.number_input("Views mín", min_value=0, value=1000, step=1000, help="Vídeos com pelo menos X visualizações")
with col2:
    max_views = st.number_input("Views máx", min_value=0, value=10000000, step=10000)

# Idade do vídeo
video_max_age = st.sidebar.selectbox(
    "📅 Vídeos publicados há no máximo:",
    [1, 3, 7, 15, 30, 90, 365, 9999],
    format_func=lambda x: f"{x} dias" if x < 9999 else "Qualquer idade",
    index=2  # 7 dias por padrão
)

# Duração do vídeo
st.sidebar.markdown("**⏱️ Duração do vídeo:**")
duration_range = st.sidebar.select_slider(
    "Duração",
    options=["Qualquer", "Curto (< 4min)", "Médio (4-20min)", "Longo (> 20min)"],
    value="Qualquer"
)

# Converter seleção de duração
if duration_range == "Curto (< 4min)":
    min_duration, max_duration = 0, 240
elif duration_range == "Médio (4-20min)":
    min_duration, max_duration = 240, 1200
elif duration_range == "Longo (> 20min)":
    min_duration, max_duration = 1200, 7200
else:
    min_duration, max_duration = 0, 7200

# Seção: Filtros de Canal
st.sidebar.markdown("### 🆕 Filtros de Canal")

# Idade máxima do canal
channel_age = st.sidebar.selectbox(
    "📺 Canais criados há no máximo:",
    [30, 90, 180, 365, 730, 9999],
    format_func=lambda x: f"{x} dias" if x < 9999 else "Qualquer idade",
    index=3  # 365 dias (1 ano) por padrão
)

# Seção: Filtros de Engajamento
st.sidebar.markdown("### 📈 Filtros de Performance")

min_likes = st.sidebar.number_input("Likes mínimos", min_value=0, value=10, step=10)
min_engagement = st.sidebar.slider("Engagement mínimo (%)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)

# Ordenação
st.sidebar.markdown("### 📊 Ordenação")
sort_by = st.sidebar.selectbox(
    "Ordenar por:",
    ['Mais recentes', 'Mais visualizações', 'Maior engagement', 'Canais mais novos', 'Mais likes', 'Duração (menor)', 'Duração (maior)']
)

# Quantidade de resultados
max_results = st.sidebar.selectbox("Máximo de resultados:", [10, 25, 50], index=1)

# Botão de busca
search_button = st.sidebar.button("🚀 BUSCAR VÍDEOS", type="primary")

# Área principal
if search_button and search_query:
    with st.spinner('🔍 Buscando vídeos em alta de canais novos...'):
        # Configurar filtros
        published_after = datetime.now() - timedelta(days=video_max_age) if video_max_age < 9999 else None
        
        # Realizar busca
        raw_videos = search_videos(
            search_query, 
            max_results=max_results, 
            published_after=published_after,
            order='date' if sort_by == 'Mais recentes' else 'relevance'
        )
        
        if raw_videos:
            # Aplicar filtros
            filters = {
                'min_views': min_views,
                'max_views': max_views,
                'min_likes': min_likes,
                'min_duration': min_duration,
                'max_duration': max_duration,
                'max_channel_age_days': channel_age,
                'min_engagement': min_engagement,
                'video_max_age_days': video_max_age
            }
            
            filtered_videos = filter_videos(raw_videos, filters)
            
            if filtered_videos:
                # Ordenar resultados
                sorted_videos = sort_videos(filtered_videos, sort_by)
                
                # Estatísticas
                trending_count = sum(1 for v in sorted_videos if is_trending_video(v))
                new_channels_count = sum(1 for v in sorted_videos if is_new_channel(v))
                avg_engagement = sum(v['engagement_rate'] for v in sorted_videos) / len(sorted_videos)
                
                # Métricas em destaque
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3 style="margin: 0; color: #333;">📊 {len(sorted_videos)}</h3>
                        <p style="margin: 0; color: #666;">Vídeos Encontrados</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3 style="margin: 0; color: #FF6B6B;">🔥 {trending_count}</h3>
                        <p style="margin: 0; color: #666;">Em Tendência</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3 style="margin: 0; color: #4ECDC4;">✨ {new_channels_count}</h3>
                        <p style="margin: 0; color: #666;">Canais Novos</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3 style="margin: 0; color: #45B7D1;">📈 {avg_engagement:.1f}%</h3>
                        <p style="margin: 0; color: #666;">Engagement Médio</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botão de export
                if st.button("📥 Exportar Resultados"):
                    df = pd.DataFrame(sorted_videos)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV Completo",
                        data=csv,
                        file_name=f"videos_trending_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Exibir resultados
                st.markdown("---")
                st.markdown("## 🎥 Resultados:")
                
                for video in sorted_videos:
                    display_video_card(video)
                    st.markdown("---")
                
            else:
                st.warning("❌ Nenhum vídeo encontrado com esses filtros. Tente critérios menos restritivos.")
        else:
            st.error("❌ Nenhum vídeo encontrado. Tente uma busca diferente.")

elif search_button and not search_query:
    st.warning("⚠️ Digite algo para buscar!")

else:
    # Tela inicial
    st.markdown("""
    ## 🎯 O que este sistema faz:
    
    **Encontra VÍDEOS em alta de CANAIS novos** - a combinação perfeita para descobrir tendências emergentes!
    
    ### 🚀 Casos de uso perfeitos:
    - **📈 Identificar tendências:** Vídeos recentes com muitas views de canais novos
    - **🎯 Encontrar nichos emergentes:** Canais pequenos mas com conteúdo viral
    - **💡 Inspiração para conteúdo:** Ver o que está funcionando AGORA
    - **🔍 Pesquisa de mercado:** Analisar o que está bombando por categoria
    
    ### ✨ Filtros únicos que o YouTube não tem:
    - ✅ **Idade do canal:** Encontre apenas canais novos (ex: criados há menos de 1 ano)
    - ✅ **Vídeos em tendência:** Recentes + alta visualização = oportunidade
    - ✅ **Engagement rate:** Taxa likes+comentários/views para medir qualidade
    - ✅ **Combinação de filtros:** Canal novo + vídeo viral + nicho específico
    
    ### 🎬 Exemplo de busca poderosa:
    1. **Busque:** "investimentos" 
    2. **Filtre:** Canais criados há menos de 6 meses
    3. **Configure:** Vídeos com +5K views publicados na última semana
    4. **Ordene:** Por engagement rate
    5. **Resultado:** Novos criadores bombando no nicho de investimentos!
    
    **👈 Configure seus filtros na barra lateral e descubra oportunidades!**
    """)

    # Dicas rápidas
    with st.expander("💡 Dicas para buscas eficazes"):
        st.markdown("""
        **Para encontrar oportunidades:**
        - Canais novos (< 1 ano) + vídeos com views altas = tendência emergente
        - Use termos em inglês para resultados mais amplos
        - Ordene por "Maior engagement" para encontrar conteúdo de qualidade
        
        **Exemplos de buscas:**
        - `"como fazer"` - tutoriais virais de canais novos
        - `"react"` - reações que estão bombando  
        - `"review"` - análises de produtos em alta
        - `"2025"` - conteúdo sobre tendências atuais
        """)
