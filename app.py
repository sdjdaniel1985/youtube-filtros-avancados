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
    page_title="YouTube Viral Hunter",
    page_icon="💎",
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
    color: #FFD700;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.strategy-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}

.gold-badge {
    background: linear-gradient(45deg, #FFD700, #FFA500);
    color: #333;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: 10px;
}

.viral-badge {
    background: linear-gradient(45deg, #FF6B6B, #FF8E53);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: 5px;
}

.small-channel-badge {
    background: linear-gradient(45deg, #A8E6CF, #88D8A3);
    color: #2d5a3d;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: 5px;
}

.video-card {
    border: 2px solid #ddd;
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    background: linear-gradient(135deg, #f9f9f9 0%, #ffffff 100%);
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.video-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    border-color: #FFD700;
}

.video-title {
    font-size: 1.4rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
    line-height: 1.3;
}

.performance-stats {
    background: #f0f8ff;
    padding: 10px;
    border-radius: 8px;
    margin: 10px 0;
    border-left: 4px solid #4ECDC4;
}

.metric-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
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

def is_short_video(duration_seconds):
    """Verificar se é um Short (vídeo curto)"""
    return duration_seconds <= 60

def get_channel_stats(channel_id):
    """Obter estatísticas do canal"""
    try:
        request = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        )
        response = request.execute()
        
        if response['items']:
            channel = response['items'][0]
            return {
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'created_date': channel['snippet']['publishedAt'],
                'channel_age_days': (datetime.now() - datetime.fromisoformat(channel['snippet']['publishedAt'].replace('Z', '+00:00')).replace(tzinfo=None)).days
            }
    except:
        pass
    return {'subscriber_count': 999999, 'created_date': '', 'channel_age_days': 9999}

def calculate_viral_score(video):
    """Calcular pontuação viral baseada na estratégia"""
    days_old = (datetime.now() - datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).replace(tzinfo=None)).days
    
    # Base score: views per day
    if days_old > 0:
        views_per_day = video['views'] / days_old
    else:
        views_per_day = video['views']  # Vídeo de hoje
    
    # Bonus para canais pequenos
    subscriber_bonus = 1
    if video['subscriber_count'] <= 1000:
        subscriber_bonus = 3
    elif video['subscriber_count'] <= 5000:
        subscriber_bonus = 2
    elif video['subscriber_count'] <= 10000:
        subscriber_bonus = 1.5
    
    # Bonus para vídeos muito recentes
    recency_bonus = 1
    if days_old <= 1:
        recency_bonus = 3
    elif days_old <= 2:
        recency_bonus = 2
    elif days_old <= 7:
        recency_bonus = 1.5
    
    # Engagement bonus
    engagement_bonus = min(video['engagement_rate'] / 2, 2)  # Max 2x bonus
    
    viral_score = views_per_day * subscriber_bonus * recency_bonus * (1 + engagement_bonus)
    return round(viral_score)

def hunt_viral_videos(min_views=50000, max_days_old=7, max_subscribers=50000, max_results=100):
    """Caçar vídeos virais seguindo a estratégia de modelagem"""
    try:
        all_videos = []
        
        # Múltiplas estratégias de busca para capturar mais conteúdo
        search_strategies = [
            {'order': 'date', 'publishedAfter': (datetime.now() - timedelta(days=max_days_old)).isoformat() + 'Z'},
            {'order': 'viewCount', 'publishedAfter': (datetime.now() - timedelta(days=max_days_old)).isoformat() + 'Z'},
            {'order': 'relevance', 'publishedAfter': (datetime.now() - timedelta(days=max_days_old)).isoformat() + 'Z'}
        ]
        
        # Termos que ajudam a encontrar conteúdo viral
        viral_keywords = [
            '',  # Sem palavra-chave para capturar geral
            'viral',
            'explodiu',
            'bomba',
            'incrível',
            'surpreendente'
        ]
        
        for strategy in search_strategies:
            for keyword in viral_keywords[:3]:  # Limitar para não esgotar quota
                try:
                    search_params = {
                        'part': 'snippet',
                        'type': 'video',
                        'maxResults': 50,
                        'regionCode': 'BR',
                        'relevanceLanguage': 'pt',
                        **strategy
                    }
                    
                    if keyword:
                        search_params['q'] = keyword
                    
                    request = youtube.search().list(**search_params)
                    response = request.execute()
                    
                    # Processar resultados
                    video_ids = [item['id']['videoId'] for item in response['items']]
                    
                    if video_ids:
                        # Buscar detalhes dos vídeos
                        stats_request = youtube.videos().list(
                            part='statistics,contentDetails',
                            id=','.join(video_ids)
                        )
                        stats_response = stats_request.execute()
                        
                        # Processar cada vídeo
                        for i, item in enumerate(response['items']):
                            video_stats = next((v for v in stats_response['items'] if v['id'] == item['id']['videoId']), None)
                            
                            if video_stats:
                                # Verificar duração (excluir Shorts)
                                duration_seconds = parse_duration(video_stats['contentDetails']['duration'])
                                if is_short_video(duration_seconds):
                                    continue  # Pular Shorts
                                
                                # Obter estatísticas do canal
                                channel_stats = get_channel_stats(item['snippet']['channelId'])
                                
                                # Aplicar filtros da estratégia
                                views = int(video_stats['statistics'].get('viewCount', 0))
                                if views < min_views:
                                    continue
                                
                                if channel_stats['subscriber_count'] > max_subscribers:
                                    continue
                                
                                # Verificar idade do vídeo
                                published_date = datetime.fromisoformat(item['snippet']['publishedAt'].replace('Z', '+00:00')).replace(tzinfo=None)
                                days_old = (datetime.now() - published_date).days
                                if days_old > max_days_old:
                                    continue
                                
                                # Criar objeto vídeo
                                video_data = {
                                    'id': item['id']['videoId'],
                                    'title': item['snippet']['title'],
                                    'channel_title': item['snippet']['channelTitle'],
                                    'channel_id': item['snippet']['channelId'],
                                    'published_at': item['snippet']['publishedAt'],
                                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                                    'description': item['snippet']['description'][:300] + '...' if len(item['snippet']['description']) > 300 else item['snippet']['description'],
                                    'views': views,
                                    'likes': int(video_stats['statistics'].get('likeCount', 0)),
                                    'comments': int(video_stats['statistics'].get('commentCount', 0)),
                                    'duration_seconds': duration_seconds,
                                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                                    'channel_url': f"https://www.youtube.com/channel/{item['snippet']['channelId']}",
                                    'subscriber_count': channel_stats['subscriber_count'],
                                    'channel_age_days': channel_stats['channel_age_days'],
                                    'days_old': days_old
                                }
                                
                                # Calcular engagement
                                if video_data['views'] > 0:
                                    video_data['engagement_rate'] = ((video_data['likes'] + video_data['comments']) / video_data['views']) * 100
                                else:
                                    video_data['engagement_rate'] = 0
                                
                                # Calcular score viral
                                video_data['viral_score'] = calculate_viral_score(video_data)
                                
                                all_videos.append(video_data)
                
                except Exception as e:
                    continue  # Continuar mesmo se uma busca falhar
        
        # Remover duplicatas e ordenar por score viral
        unique_videos = {}
        for video in all_videos:
            if video['id'] not in unique_videos:
                unique_videos[video['id']] = video
        
        final_videos = list(unique_videos.values())
        final_videos.sort(key=lambda x: x['viral_score'], reverse=True)
        
        return final_videos[:max_results]
    
    except Exception as e:
        st.error(f"Erro na caça viral: {str(e)}")
        return []

def is_viral_opportunity(video):
    """Determinar se é uma oportunidade viral de ouro"""
    # Critérios de ouro da estratégia
    return (
        video['days_old'] <= 2 and  # Até 2 dias
        video['subscriber_count'] <= 5000 and  # Canal pequeno
        video['views'] >= 50000 and  # Performance mínima
        not is_short_video(video['duration_seconds'])  # Não é Short
    )

def display_viral_card(video):
    """Exibir card do vídeo viral"""
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        try:
            response = requests.get(video['thumbnail'])
            img = Image.open(BytesIO(response.content))
            st.image(img, width=200)
        except:
            st.image("https://via.placeholder.com/320x180?text=No+Thumbnail", width=200)
        
        st.markdown(f"**⏱️ {format_duration(video['duration_seconds'])}**")
        
        # Mostrar score viral
        st.markdown(f"**🔥 Score Viral: {format_number(video['viral_score'])}**")
    
    with col2:
        # Badges especiais
        badges_html = ""
        if is_viral_opportunity(video):
            badges_html += '<span class="gold-badge">💎 OPORTUNIDADE OURO</span>'
        if video['days_old'] <= 1:
            badges_html += '<span class="viral-badge">⚡ ULTRA-RECENTE</span>'
        if video['subscriber_count'] <= 1000:
            badges_html += '<span class="small-channel-badge">🎯 CANAL PEQUENO</span>'
        
        # Calcular views por dia
        views_per_day = video['views'] / max(video['days_old'], 1)
        
        st.markdown(f"""
        <div class="video-card">
            <div class="video-title">{video['title']} {badges_html}</div>
            
            <div class="performance-stats">
                <strong>📊 Performance Viral:</strong><br>
                👁️ <strong>{format_number(video['views'])} views</strong> em {video['days_old']} dias = <strong>{format_number(views_per_day)} views/dia</strong><br>
                📺 Canal: <strong>{video['channel_title']}</strong> ({format_number(video['subscriber_count'])} inscritos)<br>
                📈 Engagement: <strong>{video['engagement_rate']:.2f}%</strong> | 
                👍 {format_number(video['likes'])} likes | 
                💬 {format_number(video['comments'])} comentários
            </div>
            
            <div style="color: #666; font-size: 0.9rem; margin: 10px 0;">
                📅 Publicado há <strong>{video['days_old']} dias</strong> | 
                🎂 Canal criado há {video['channel_age_days']} dias
            </div>
            
            <p style="color: #666; font-size: 0.85rem; margin: 10px 0;">
                {video['description']}
            </p>
            
            <div style="margin-top: 15px;">
                <a href="{video['url']}" target="_blank" style="color: #FF0000; text-decoration: none; margin-right: 20px; font-weight: bold;">
                    🎥 ANALISAR VÍDEO
                </a>
                <a href="{video['channel_url']}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">
                    📺 VER CANAL
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Interface principal
st.markdown('<h1 class="main-header">💎 YouTube Viral Hunter</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #666; font-weight: bold;">Estratégia de Modelagem Ultra-Recente | Encontre Ouro Viral Antes da Concorrência</p>', unsafe_allow_html=True)

# Caixa da estratégia
st.markdown("""
<div class="strategy-box">
    <h3>💎 ESTRATÉGIA DE CAÇA AO OURO VIRAL</h3>
    <ul style="margin: 10px 0;">
        <li><strong>🎯 Critério Ouro:</strong> Vídeos com até 48h que já explodiram</li>
        <li><strong>📺 Canal pequeno:</strong> Até 5K inscritos (não é força da marca)</li>
        <li><strong>📈 Performance mínima:</strong> 50K+ views em poucos dias</li>
        <li><strong>⏱️ Sem Shorts:</strong> Apenas vídeos longos de valor</li>
        <li><strong>🚀 Score Viral:</strong> Algoritmo que identifica as maiores oportunidades</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Controles da caça viral
col1, col2, col3, col4 = st.columns(4)

with col1:
    min_views = st.selectbox(
        "👁️ Views mínimas:",
        [10000, 25000, 50000, 100000, 200000],
        index=2,  # 50K por padrão
        help="Vídeos devem ter pelo menos essa performance"
    )

with col2:
    max_days = st.selectbox(
        "📅 Máximo dias:",
        [1, 2, 3, 7],
        index=2,  # 3 dias por padrão
        help="Idade máxima do vídeo para ser considerado ultra-recente"
    )

with col3:
    max_subs = st.selectbox(
        "📺 Máx inscritos:",
        [1000, 2500, 5000, 10000, 25000],
        index=2,  # 5K por padrão
        help="Canal deve ter no máximo essa quantidade de inscritos"
    )

with col4:
    hunt_results = st.selectbox(
        "🎯 Resultados:",
        [20, 30, 50, 75],
        index=2,  # 50 por padrão
        help="Quantos vídeos virais mostrar"
    )

# Botão principal de caça
if st.button("🏹 CAÇAR OPORTUNIDADES VIRAIS!", type="primary", use_container_width=True):
    with st.spinner(f'💎 Caçando ouro viral dos últimos {max_days} dias...'):
        viral_videos = hunt_viral_videos(
            min_views=min_views,
            max_days_old=max_days,
            max_subscribers=max_subs,
            max_results=hunt_results
        )
        
        if viral_videos:
            # Estatísticas especiais
            gold_opportunities = sum(1 for v in viral_videos if is_viral_opportunity(v))
            ultra_recent = sum(1 for v in viral_videos if v['days_old'] <= 1)
            small_channels = sum(1 for v in viral_videos if v['subscriber_count'] <= 1000)
            avg_viral_score = sum(v['viral_score'] for v in viral_videos) / len(viral_videos)
            
            # Métricas em destaque
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0;">💎 {gold_opportunities}</h3>
                    <p style="margin: 0;">Oportunidades Ouro</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0;">⚡ {ultra_recent}</h3>
                    <p style="margin: 0;">Ultra-Recentes (1 dia)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0;">🎯 {small_channels}</h3>
                    <p style="margin: 0;">Canais <1K subs</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0;">🔥 {format_number(avg_viral_score)}</h3>
                    <p style="margin: 0;">Score Viral Médio</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Export
            if st.button("📥 Exportar Oportunidades Virais"):
                df = pd.DataFrame(viral_videos)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV - Ouro Viral",
                    data=csv,
                    file_name=f"ouro_viral_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Resultados
            st.markdown("---")
            st.markdown("## 💎 OPORTUNIDADES VIRAIS ENCONTRADAS:")
            st.markdown("*Ordenado por Score Viral (views/dia × bônus canal pequeno × bônus recência)*")
            
            for video in viral_videos:
                display_viral_card(video)
                st.markdown("---")
                
        else:
            st.warning(f"💔 Nenhuma oportunidade viral encontrada com esses critérios. Tente views mínimas menores ou mais dias.")

else:
    # Tela inicial
    st.markdown("""
    ## 🎯 Por que esta estratégia funciona:
    
    ### 💎 **O Segredo da Modelagem Ultra-Recente:**
    Quando um vídeo de canal pequeno explode rapidamente, significa que o **conteúdo** é viral, não a audiência. 
    Isso é **OURO PURO** para modelagem!
    
    ### 🚀 **Vantagens desta caça:**
    - ✅ **Tendência fresca:** Vídeos de 24-48h ainda não saturados
    - ✅ **Prova social:** Já demonstrou potencial viral
    - ✅ **Canal pequeno:** Sucesso vem do conteúdo, não da audiência
    - ✅ **Sem Shorts:** Foco em conteúdo de valor real
    - ✅ **Score Viral:** Algoritmo identifica as melhores oportunidades
    
    ### 💡 **Como usar os resultados:**
    1. **Analise os vídeos com badge "OPORTUNIDADE OURO"**
    2. **Estude o padrão:** título, thumbnail, tema, estrutura
    3. **Modele rapidamente:** crie sua versão única
    4. **Lance enquanto está quente:** máximo 2-3 dias depois
    
    **👆 Configure os filtros e descubra seu próximo viral!**
    """)

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>💎 <strong>YouTube Viral Hunter</strong> | Estratégia de Modelagem Ultra-Recente</p>
    <p>Encontre oportunidades virais antes que se tornem saturadas!</p>
</div>
""", unsafe_allow_html=True)
