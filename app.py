import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import json
from urllib.parse import quote, urlencode
import random
from PIL import Image
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="YouTube Real Scraper",
    page_icon="🕷️",
    layout="wide"
)

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

.scraper-info {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
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

.trending-badge {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: 10px;
}

.viral-badge {
    background: linear-gradient(45deg, #FFD700, #FFA500);
    color: #333;
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

.warning-box {
    background: #fff3cd;
    color: #856404;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

class YouTubeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def format_number(self, text):
        """Converter texto de visualizações para número"""
        if not text:
            return 0
        
        text = text.replace('.', '').replace(',', '').lower()
        multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000, 'mi': 1000000, 'mil': 1000}
        
        for suffix, multiplier in multipliers.items():
            if suffix in text:
                number = re.findall(r'\d+', text.replace(suffix, ''))
                if number:
                    return int(float(number[0]) * multiplier)
        
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0
    
    def extract_video_data_from_script(self, html):
        """Extrair dados de vídeos do JavaScript do YouTube"""
        videos = []
        
        try:
            # Procurar por dados JSON no HTML
            script_pattern = r'var ytInitialData = ({.*?});'
            match = re.search(script_pattern, html, re.DOTALL)
            
            if match:
                data = json.loads(match.group(1))
                
                # Navegar pela estrutura complexa do YouTube
                contents = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
                
                for tab in contents:
                    tab_renderer = tab.get('tabRenderer', {})
                    content = tab_renderer.get('content', {})
                    
                    # Diferentes estruturas possíveis
                    section_list = content.get('sectionListRenderer', {}).get('contents', [])
                    
                    for section in section_list:
                        items = section.get('itemSectionRenderer', {}).get('contents', [])
                        
                        for item in items:
                            shelf = item.get('shelfRenderer', {})
                            if shelf:
                                shelf_contents = shelf.get('content', {}).get('horizontalListRenderer', {}).get('items', [])
                                
                                for video_item in shelf_contents:
                                    video_renderer = video_item.get('gridVideoRenderer', {})
                                    if video_renderer:
                                        video_data = self.parse_video_renderer(video_renderer)
                                        if video_data:
                                            videos.append(video_data)
            
        except Exception as e:
            st.error(f"Erro ao extrair dados: {str(e)}")
        
        return videos
    
    def parse_video_renderer(self, renderer):
        """Parsear dados de um vídeo do renderer"""
        try:
            video_id = renderer.get('videoId', '')
            
            title_runs = renderer.get('title', {}).get('runs', [])
            title = title_runs[0].get('text', '') if title_runs else 'Sem título'
            
            # Canal
            owner_text = renderer.get('ownerText', {}).get('runs', [])
            channel_name = owner_text[0].get('text', '') if owner_text else 'Canal desconhecido'
            
            # Views e data
            view_count = renderer.get('viewCountText', {}).get('simpleText', '0')
            published_time = renderer.get('publishedTimeText', {}).get('simpleText', '')
            
            # Thumbnail
            thumbnails = renderer.get('thumbnail', {}).get('thumbnails', [])
            thumbnail_url = thumbnails[-1].get('url', '') if thumbnails else ''
            
            # Duração
            duration = renderer.get('lengthText', {}).get('simpleText', '0:00')
            
            return {
                'id': video_id,
                'title': title,
                'channel_name': channel_name,
                'views_text': view_count,
                'views': self.format_number(view_count),
                'published_time': published_time,
                'thumbnail': thumbnail_url,
                'duration': duration,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'channel_url': f'https://www.youtube.com/channel/{renderer.get("ownerNavigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", "").replace("/channel/", "")}'
            }
        
        except Exception as e:
            return None
    
    def scrape_trending_page(self, category='0'):
        """Scraper da página de trending do YouTube"""
        try:
            url = f'https://www.youtube.com/feed/trending'
            if category != '0':
                url += f'?bp={category}'
            
            response = self.session.get(url)
            
            if response.status_code == 200:
                videos = self.extract_video_data_from_script(response.text)
                return videos
            else:
                st.error(f"Erro ao acessar YouTube: {response.status_code}")
                return []
        
        except Exception as e:
            st.error(f"Erro no scraping: {str(e)}")
            return []
    
    def scrape_search_results(self, query, max_results=50):
        """Scraper de resultados de busca"""
        try:
            # Simular busca real no YouTube
            search_url = f'https://www.youtube.com/results?search_query={quote(query)}'
            
            response = self.session.get(search_url)
            
            if response.status_code == 200:
                videos = self.extract_video_data_from_script(response.text)
                return videos[:max_results]
            else:
                return []
        
        except Exception as e:
            st.error(f"Erro na busca: {str(e)}")
            return []
    
    def get_channel_info_basic(self, video_data):
        """Obter informações básicas do canal (sem API)"""
        # Para versão básica, vamos estimar baseado nos dados disponíveis
        views = video_data.get('views', 0)
        
        # Estimativa de idade do canal baseada em padrões
        if 'hora' in video_data.get('published_time', '').lower():
            estimated_channel_age = 'Novo (estimado)'
        elif 'dia' in video_data.get('published_time', '').lower():
            estimated_channel_age = 'Recente (estimado)'
        else:
            estimated_channel_age = 'Estabelecido (estimado)'
        
        return {
            'estimated_size': 'Pequeno' if views < 100000 else 'Médio' if views < 1000000 else 'Grande',
            'estimated_age': estimated_channel_age
        }

def format_number(num):
    """Formatar números grandes"""
    if num >= 1000000000:
        return f"{num/1000000000:.1f}B"
    elif num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def is_recent_video(published_time):
    """Verificar se é vídeo recente"""
    recent_keywords = ['hora', 'horas', 'minuto', 'minutos', '1 dia', '2 dias']
    return any(keyword in published_time.lower() for keyword in recent_keywords)

def is_viral_candidate(video):
    """Verificar se é candidato viral baseado nos dados disponíveis"""
    return (
        video['views'] > 50000 and
        is_recent_video(video.get('published_time', ''))
    )

def display_scraped_video_card(video):
    """Exibir card do vídeo scrapado"""
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        # Thumbnail
        if video.get('thumbnail'):
            try:
                st.image(video['thumbnail'], width=200)
            except:
                st.image("https://via.placeholder.com/320x180?text=YouTube", width=200)
        else:
            st.image("https://via.placeholder.com/320x180?text=No+Thumbnail", width=200)
        
        # Duração
        st.markdown(f"**⏱️ {video.get('duration', '0:00')}**")
    
    with col2:
        # Badges
        badges_html = ""
        if is_viral_candidate(video):
            badges_html += '<span class="viral-badge">🔥 VIRAL CANDIDATE</span>'
        if is_recent_video(video.get('published_time', '')):
            badges_html += '<span class="trending-badge">⚡ RECENTE</span>'
        
        # Informações básicas do canal
        channel_info = scraper.get_channel_info_basic(video)
        
        st.markdown(f"""
        <div class="video-card">
            <div class="video-title">{video['title']} {badges_html}</div>
            
            <div style="color: #666; font-size: 1rem; margin-bottom: 8px;">
                📺 <strong>{video['channel_name']}</strong> 
                <span style="color: #999;">({channel_info['estimated_size']} - {channel_info['estimated_age']})</span>
            </div>
            
            <div style="color: #0066cc; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px;">
                👁️ {video['views_text']} visualizações • 
                📅 {video.get('published_time', 'Data não disponível')}
            </div>
            
            <div style="margin-top: 15px;">
                <a href="{video['url']}" target="_blank" style="color: #FF0000; text-decoration: none; margin-right: 20px; font-weight: bold;">
                    🎥 ASSISTIR VÍDEO
                </a>
                <a href="{video.get('channel_url', '#')}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">
                    📺 VER CANAL
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Inicializar scraper
scraper = YouTubeScraper()

# Interface principal
st.markdown('<h1 class="main-header">🕷️ YouTube Real Scraper</h1>', unsafe_allow_html=True)

# Info sobre scraper
st.markdown("""
<div class="scraper-info">
    <h3>🚀 Scraper Real do YouTube - SEM Limitações da API!</h3>
    <ul style="margin: 10px 0;">
        <li><strong>✅ Acesso direto</strong> às páginas do YouTube (como navegador real)</li>
        <li><strong>✅ Sem quotas</strong> ou limitações da API oficial</li>
        <li><strong>✅ Dados reais</strong> de trending e busca</li>
        <li><strong>✅ Muito mais resultados</strong> que a API restritiva</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Warning sobre legalidade
st.markdown("""
<div class="warning-box">
    <strong>⚠️ Aviso Legal:</strong> Este scraper acessa dados públicos do YouTube para fins educacionais e de pesquisa. 
    Use com responsabilidade e respeite os termos de uso do YouTube.
</div>
""", unsafe_allow_html=True)

# Abas do scraper
tab1, tab2 = st.tabs(["🔥 Trending Real", "🔍 Busca Avançada"])

# ABA 1: Trending Real
with tab1:
    st.markdown("### 🔥 Trending Real do YouTube")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "📂 Categoria:",
            [
                ("Geral", "0"),
                ("Música", "10"),
                ("Gaming", "20"),
                ("Filmes", "30"),
                ("Notícias", "25")
            ],
            format_func=lambda x: x[0]
        )
    
    with col2:
        min_views_trending = st.selectbox(
            "👁️ Views mínimas:",
            [0, 1000, 5000, 10000, 50000, 100000],
            index=0
        )
    
    if st.button("🕷️ SCRAPE TRENDING AGORA!", type="primary"):
        with st.spinner('🔄 Fazendo scraping da página de trending...'):
            trending_videos = scraper.scrape_trending_page(category[1])
            
            if trending_videos:
                # Filtrar por views mínimas
                if min_views_trending > 0:
                    trending_videos = [v for v in trending_videos if v['views'] >= min_views_trending]
                
                if trending_videos:
                    # Estatísticas
                    viral_candidates = sum(1 for v in trending_videos if is_viral_candidate(v))
                    recent_videos = sum(1 for v in trending_videos if is_recent_video(v.get('published_time', '')))
                    total_views = sum(v['views'] for v in trending_videos)
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="margin: 0; color: #333;">📊 {len(trending_videos)}</h3>
                            <p style="margin: 0; color: #666;">Vídeos Encontrados</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="margin: 0; color: #FF6B6B;">🔥 {viral_candidates}</h3>
                            <p style="margin: 0; color: #666;">Candidatos Virais</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="margin: 0; color: #4ECDC4;">⚡ {recent_videos}</h3>
                            <p style="margin: 0; color: #666;">Vídeos Recentes</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="margin: 0; color: #45B7D1;">👁️ {format_number(total_views)}</h3>
                            <p style="margin: 0; color: #666;">Views Totais</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Export
                    if st.button("📥 Exportar Trending"):
                        df = pd.DataFrame(trending_videos)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="⬇️ Download CSV Trending",
                            data=csv,
                            file_name=f"trending_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    # Resultados
                    st.markdown("---")
                    st.markdown("## 🔥 Vídeos em Trending:")
                    
                    for video in trending_videos:
                        display_scraped_video_card(video)
                        st.markdown("---")
                
                else:
                    st.warning("❌ Nenhum vídeo encontrado com esses filtros.")
            else:
                st.error("❌ Erro ao fazer scraping. O YouTube pode estar bloqueando temporariamente.")

# ABA 2: Busca Avançada
with tab2:
    st.markdown("### 🔍 Busca Real no YouTube")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_query = st.text_input("🔎 Buscar por:", placeholder="Ex: viral, tendência, bomba...")
    
    with col2:
        max_search_results = st.selectbox("📊 Máx resultados:", [20, 30, 50, 75], index=2)
    
    if st.button("🕷️ SCRAPE BUSCA AGORA!", type="primary") and search_query:
        with st.spinner(f'🔄 Fazendo scraping da busca: "{search_query}"...'):
            search_videos = scraper.scrape_search_results(search_query, max_search_results)
            
            if search_videos:
                # Estatísticas
                viral_candidates = sum(1 for v in search_videos if is_viral_candidate(v))
                recent_videos = sum(1 for v in search_videos if is_recent_video(v.get('published_time', '')))
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3 style="margin: 0; color: #333;">📊 {len(search_videos)}</h3>
                        <p style="margin: 0; color: #666;">Resultados</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3 style="margin: 0; color: #FF6B6B;">🔥 {viral_candidates}</h3>
                        <p style="margin: 0; color: #666;">Candidatos Virais</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3 style="margin: 0; color: #4ECDC4;">⚡ {recent_videos}</h3>
                        <p style="margin: 0; color: #666;">Recentes</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export
                if st.button("📥 Exportar Busca"):
                    df = pd.DataFrame(search_videos)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV Busca",
                        data=csv,
                        file_name=f"busca_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Resultados
                st.markdown("---")
                st.markdown(f"## 🔍 Resultados para: '{search_query}'")
                
                for video in search_videos:
                    display_scraped_video_card(video)
                    st.markdown("---")
            
            else:
                st.error("❌ Nenhum resultado encontrado ou erro no scraping.")
    
    elif st.button("🕷️ SCRAPE BUSCA AGORA!", type="primary") and not search_query:
        st.warning("⚠️ Digite algo para buscar!")

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🕷️ <strong>YouTube Real Scraper</strong> | Sem limitações da API oficial</p>
    <p>Acesso direto aos dados reais do YouTube!</p>
</div>
""", unsafe_allow_html=True)
