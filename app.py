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
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.tab-header {
    font-size: 1.5rem;
    color: #333;
    text-align: center;
    margin-bottom: 1rem;
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

.metric-container {
    background: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin: 10px 0;
}

.trending-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
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
    return 9999

def search_videos(query, max_results=50, published_after=None, order='relevance'):
    """Buscar vídeos no YouTube"""
    try:
        search_params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'order': order,
            'regionCode': 'BR',
            'relevanceLanguage': 'pt'
        }
        
        if published_after:
            search_params['publishedAfter'] = published_after.isoformat() + 'Z'
        
        request = youtube.search().list(**search_params)
        response = request.execute()
        
        return process_video_results(response)
    
    except Exception as e:
        st.error(f"Erro na busca: {str(e)}")
        return []

def get_trending_videos(min_views=1000, days_back=7, max_results=50):
    """Buscar vídeos em tendência sem query específica"""
    try:
        # Usar termos genéricos populares para capturar conteúdo em alta
        trending_queries = [
            "", # Query vazia para pegar trending geral
            "viral", 
            "2025",
            "novo",
            "hoje"
        ]
        
        all_videos = []
        published_after = datetime.now() - timedelta(days=days_back)
        
        for query in trending_queries[:2]:  # Usar apenas 2 queries para não esgotar quota
            search_params = {
                'part': 'snippet',
                'type': 'video',
                'maxResults': max_results // 2,
                'order': 'date',  # Mais recentes primeiro
                'publishedAfter': published_after.isoformat() + 'Z',
                'regionCode': 'BR',
                'relevanceLanguage': 'pt'
            }
            
            if query:  # Se não for query vazia
                search_params['q'] = query
            
            request = youtube.search().list(**search_params)
            response = request.execute()
            
            videos = process_video_results(response)
            
            # Filtrar por views mínimas
            filtered_videos = [v for v in videos if v['views'] >= min_views]
            all_videos.extend(filtered_videos)
        
        # Remover duplicatas por ID
        unique_videos = {}
        for video in all_videos:
            if video['id'] not in unique_videos:
                unique_videos[video['id']] = video
        
        return list(unique_videos.values())
    
    except Exception as e:
        st.error(f"Erro ao buscar tendências: {str(e)}")
        return []

def process_video_results(response):
    """Processar resultados da API e obter detalhes completos"""
    video_ids = [item['id']['videoId'] for item in response['items']]
    
    if not video_ids:
        return []
    
    # Buscar detalhes dos vídeos
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

def filter_videos(videos, filters):
    """Aplicar filtros aos vídeos"""
    filtered = videos.copy()
    
    # Filtro por visualizações
    filtered = [v for v in filtered if filters['min_views'] <= v['views'] <= filters['max_views']]
    
    # Filtro por duração
    if filters['min_duration'] > 0 or filters['max_duration'] < 7200:
        filtered = [v for v in filtered if filters['min_duration'] <= v['duration_seconds'] <= filters['max_duration']]
    
    # Filtro por idade do canal
    if filters['max_channel_age_days'] < 9999:
        filtered = [v for v in filtered if v['channel_age_days'] <= filters['max_channel_age_days']]
    
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
    """Exibir card do vídeo"""
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        try:
            response = requests.get(video['thumbnail'])
            img = Image.open(BytesIO(response.content))
            st.image(img, width=200)
        except:
            st.image("https://via.placeholder.com/320x180?text=No+Thumbnail", width=200)
        
        st.markdown(f"**⏱️ {format_duration(video['duration_seconds'])}**")
    
    with col2:
        badges_html = ""
        if show_badges:
            if is_trending_video(video):
                badges_html += '<span class="trending-badge">🔥 TRENDING</span>'
            if is_new_channel(video):
                badges_html += '<span class="new-channel-badge">✨ CANAL NOVO</span>'
        
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

def display_metrics(videos):
    """Exibir métricas dos resultados"""
    if not videos:
        return
    
    trending_count = sum(1 for v in videos if is_trending_video(v))
    new_channels_count = sum(1 for v in videos if is_new_channel(v))
    avg_engagement = sum(v['engagement_rate'] for v in videos) / len(videos)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="margin: 0; color: #333;">📊 {len(videos)}</h3>
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

# Interface principal
st.markdown('<h1 class="main-header">🚀 YouTube Explorer Pro</h1>', unsafe_allow_html=True)

# Criar abas
tab1, tab2 = st.tabs(["🔍 Busca Personalizada", "🔥 Descobrir Tendências"])

# ABA 1: Busca Personalizada
with tab1:
    st.markdown('<h2 class="tab-header">🔍 Busca com Filtros Personalizados</h2>', unsafe_allow_html=True)
    
    # Sidebar para aba 1
    with st.sidebar:
        st.markdown("## 🎯 Filtros de Busca")
        
        # Busca básica
        search_query = st.text_input("🔎 Buscar por:", placeholder="Ex: react, receitas, investimentos...")
        
        # Filtros de vídeo
        st.markdown("### 🎬 Filtros de Vídeo")
        
        col1, col2 = st.columns(2)
        with col1:
            min_views = st.number_input("Views mín", min_value=0, value=1000, step=1000)
        with col2:
            max_views = st.number_input("Views máx", min_value=0, value=10000000, step=10000)
        
        # Idade do vídeo
        video_max_age = st.selectbox(
            "📅 Vídeos publicados há no máximo:",
            [1, 3, 7, 15, 30, 90, 365, 9999],
            format_func=lambda x: f"{x} dias" if x < 9999 else "Qualquer idade",
            index=2
        )
        
        # Duração do vídeo
        duration_range = st.select_slider(
            "⏱️ Duração:",
            options=["Qualquer", "Curto (< 4min)", "Médio (4-20min)", "Longo (> 20min)"],
            value="Qualquer"
        )
        
        # Converter duração
        if duration_range == "Curto (< 4min)":
            min_duration, max_duration = 0, 240
        elif duration_range == "Médio (4-20min)":
            min_duration, max_duration = 240, 1200
        elif duration_range == "Longo (> 20min)":
            min_duration, max_duration = 1200, 7200
        else:
            min_duration, max_duration = 0, 7200
        
        # Filtros de canal
        st.markdown("### 🆕 Filtros de Canal")
        channel_age = st.selectbox(
            "📺 Canais criados há no máximo:",
            [30, 90, 180, 365, 730, 9999],
            format_func=lambda x: f"{x} dias" if x < 9999 else "Qualquer idade",
            index=3
        )
        
        # Ordenação
        st.markdown("### 📊 Ordenação")
        sort_by = st.selectbox(
            "Ordenar por:",
            ['Mais recentes', 'Mais visualizações', 'Maior engagement', 'Canais mais novos', 'Mais likes', 'Duração (menor)', 'Duração (maior)']
        )
        
        # Quantidade de resultados
        max_results = st.selectbox("Máximo de resultados:", [10, 25, 50], index=1)
        
        # Botão de busca
        search_button = st.button("🚀 BUSCAR VÍDEOS", type="primary")
    
    # Área principal da aba 1
    if search_button and search_query:
        with st.spinner('🔍 Buscando vídeos...'):
            published_after = datetime.now() - timedelta(days=video_max_age) if video_max_age < 9999 else None
            
            raw_videos = search_videos(
                search_query, 
                max_results=max_results, 
                published_after=published_after,
                order='date' if sort_by == 'Mais recentes' else 'relevance'
            )
            
            if raw_videos:
                filters = {
                    'min_views': min_views,
                    'max_views': max_views,
                    'min_duration': min_duration,
                    'max_duration': max_duration,
                    'max_channel_age_days': channel_age,
                    'video_max_age_days': video_max_age
                }
                
                filtered_videos = filter_videos(raw_videos, filters)
                
                if filtered_videos:
                    sorted_videos = sort_videos(filtered_videos, sort_by)
                    
                    # Métricas
                    display_metrics(sorted_videos)
                    
                    # Export
                    if st.button("📥 Exportar Resultados"):
                        df = pd.DataFrame(sorted_videos)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=csv,
                            file_name=f"videos_busca_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    # Resultados
                    st.markdown("---")
                    for video in sorted_videos:
                        display_video_card(video)
                        st.markdown("---")
                        
                else:
                    st.warning("❌ Nenhum vídeo encontrado com esses filtros.")
            else:
                st.error("❌ Nenhum vídeo encontrado.")
    
    elif search_button and not search_query:
        st.warning("⚠️ Digite algo para buscar!")
    
    else:
        st.markdown("""
        ## 🎯 Busca Personalizada
        
        Configure seus filtros na barra lateral e digite um termo para buscar vídeos específicos com critérios avançados.
        
        **Exemplos de busca:**
        - "investimentos" + canais novos + última semana
        - "receitas" + vídeos curtos + alta visualização
        - "tecnologia" + canais recentes + maior engagement
        """)

# ABA 2: Descobrir Tendências
with tab2:
    st.markdown('<h2 class="tab-header">🔥 Descobrir o que está Bombando Agora</h2>', unsafe_allow_html=True)
    
    # Controles simples para tendências
    st.markdown("""
    <div class="trending-section">
        <h3 style="margin-top: 0;">🎯 Sem busca, sem complicação!</h3>
        <p>Encontre automaticamente os vídeos que estão bombando nos últimos dias. 
        Configure apenas as views mínimas e veja as tendências emergirem!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        trending_min_views = st.selectbox(
            "👁️ Views mínimas:",
            [500, 1000, 2000, 5000, 10000, 20000, 50000],
            index=2,  # 2000 por padrão
            help="Vídeos devem ter pelo menos essa quantidade de visualizações"
        )
    
    with col2:
        trending_days = st.selectbox(
            "📅 Últimos:",
            [1, 3, 7, 15],
            index=2,  # 7 dias por padrão
            format_func=lambda x: f"{x} dias"
        )
    
    with col3:
        trending_sort = st.selectbox(
            "📊 Ordenar por:",
            ['Mais recentes', 'Mais visualizações', 'Maior engagement'],
            index=0  # Mais recentes por padrão
        )
    
    with col4:
        trending_results = st.selectbox(
            "📈 Quantidade:",
            [20, 30, 50],
            index=1  # 30 por padrão
        )
    
    # Botão para descobrir tendências
    if st.button("🚀 DESCOBRIR TENDÊNCIAS AGORA!", type="primary", use_container_width=True):
        with st.spinner(f'🔥 Descobrindo vídeos em alta dos últimos {trending_days} dias...'):
            trending_videos = get_trending_videos(
                min_views=trending_min_views,
                days_back=trending_days,
                max_results=trending_results
            )
            
            if trending_videos:
                # Ordenar conforme seleção
                sorted_trending = sort_videos(trending_videos, trending_sort)
                
                # Métricas
                display_metrics(sorted_trending)
                
                # Export
                if st.button("📥 Exportar Tendências"):
                    df = pd.DataFrame(sorted_trending)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV Tendências",
                        data=csv,
                        file_name=f"tendencias_youtube_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Resultados
                st.markdown("---")
                st.markdown("## 🔥 Vídeos em Tendência:")
                
                for video in sorted_trending:
                    display_video_card(video)
                    st.markdown("---")
                    
            else:
                st.warning("❌ Nenhuma tendência encontrada com esses critérios. Tente views mínimas menores.")
    
    else:
        # Tela inicial da aba tendências
        st.markdown("""
        ## 🚀 Como funciona:
        
        1. **Escolha as views mínimas** - quantas visualizações um vídeo deve ter para ser considerado "em alta"
        2. **Selecione o período** - últimos 1, 3, 7 ou 15 dias
        3. **Escolha a ordenação** - mais recentes, mais views ou maior engagement
        4. **Clique em "DESCOBRIR"** - e pronto! Veja o que está bombando sem digitar nada
        
        ### 🎯 Perfeito para:
        - ✅ **Descobrir nichos emergentes** sem saber por onde começar
        - ✅ **Ver o que está viral AGORA** nos últimos dias
        - ✅ **Encontrar oportunidades** de conteúdo em alta
        - ✅ **Monitorar tendências gerais** do YouTube Brasil
        
        **👆 Configure as opções acima e descubra as tendências!**
        """)

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🚀 <strong>YouTube Explorer Pro</strong> | Encontre vídeos em alta de canais novos</p>
    <p>Desenvolvido para descobrir tendências emergentes antes da concorrência!</p>
</div>
""", unsafe_allow_html=True)
