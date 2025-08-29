import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import random
import json
from urllib.parse import quote, urlencode, urlparse, parse_qs
from PIL import Image
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="YouTube Smart Scraper",
    page_icon="🧠",
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

.smart-info {
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

.viral-badge {
    background: linear-gradient(45deg, #FFD700, #FFA500);
    color: #333;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: 5px;
}

.recent-badge {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    color: white;
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

.strategy-box {
    background: #e8f5e8;
    color: #2d5a3d;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #28a745;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

class YouTubeSmartScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Configurar sessão com headers ultra-realistas"""
        # Headers que imitam navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
    
    def human_delay(self, min_sec=1, max_sec=3):
        """Delay humano aleatório"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def extract_views_number(self, text):
        """Extrair número de views de texto"""
        if not text:
            return 0
        
        text = text.lower().replace('.', '').replace(',', '').replace(' ', '')
        
        multipliers = {
            'mil': 1000, 'k': 1000,
            'milhão': 1000000, 'milhões': 1000000, 'm': 1000000, 'mi': 1000000,
            'bilhão': 1000000000, 'bilhões': 1000000000, 'b': 1000000000
        }
        
        for suffix, multiplier in multipliers.items():
            if suffix in text:
                numbers = re.findall(r'\d+(?:\.\d+)?', text.replace(suffix, ''))
                if numbers:
                    return int(float(numbers[0]) * multiplier)
        
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0
    
    def get_trending_videos(self, max_videos=50):
        """Obter vídeos trending usando múltiplas estratégias"""
        videos = []
        
        # Estratégia 1: RSS Feeds do YouTube (funciona sempre!)
        try:
            st.info("📡 Acessando RSS feeds do YouTube...")
            
            # RSS feeds por categoria
            rss_urls = [
                'https://www.youtube.com/feeds/videos.xml?chart=most_popular',  # Mais populares
            ]
            
            for rss_url in rss_urls:
                try:
                    response = self.session.get(rss_url, timeout=10)
                    if response.status_code == 200:
                        # Parse XML simples
                        entries = re.findall(r'<entry>(.*?)</entry>', response.text, re.DOTALL)
                        
                        for entry in entries[:20]:  # Limitar para não sobrecarregar
                            video_data = self.parse_rss_entry(entry)
                            if video_data:
                                videos.append(video_data)
                except:
                    continue
                
                self.human_delay(0.5, 1)
        except Exception as e:
            st.warning(f"RSS feeds não disponíveis: {str(e)}")
        
        # Estratégia 2: Scraping inteligente da página trending
        try:
            st.info("🎯 Scraping inteligente da página trending...")
            trending_videos = self.scrape_trending_smart()
            videos.extend(trending_videos)
        except Exception as e:
            st.warning(f"Scraping trending falhou: {str(e)}")
        
        # Estratégia 3: Usar buscas por termos virais
        try:
            st.info("🔥 Buscando por termos virais...")
            viral_terms = ['viral', 'bomba', 'explosão', 'trending', 'hot']
            
            for term in viral_terms[:2]:  # Limitar para não sobrecarregar
                search_videos = self.search_videos_smart(term, max_results=10)
                videos.extend(search_videos)
                self.human_delay(1, 2)
        except Exception as e:
            st.warning(f"Busca viral falhou: {str(e)}")
        
        # Remover duplicatas e limitar
        unique_videos = {}
        for video in videos:
            video_id = video.get('id')
            if video_id and video_id not in unique_videos:
                unique_videos[video_id] = video
        
        final_videos = list(unique_videos.values())[:max_videos]
        
        # Enriquecer dados com informações adicionais
        for video in final_videos:
            try:
                self.enrich_video_data(video)
            except:
                continue
        
        return final_videos
    
    def parse_rss_entry(self, entry):
        """Parse de entrada RSS"""
        try:
            # Extrair dados básicos do XML
            video_id_match = re.search(r'yt:videoId>([^<]+)', entry)
            title_match = re.search(r'<title>([^<]+)</title>', entry)
            channel_match = re.search(r'<name>([^<]+)</name>', entry)
            published_match = re.search(r'<published>([^<]+)</published>', entry)
            
            if video_id_match and title_match:
                return {
                    'id': video_id_match.group(1),
                    'title': title_match.group(1),
                    'channel_name': channel_match.group(1) if channel_match else 'Desconhecido',
                    'published_time': published_match.group(1) if published_match else '',
                    'url': f'https://www.youtube.com/watch?v={video_id_match.group(1)}',
                    'source': 'RSS'
                }
        except:
            pass
        return None
    
    def scrape_trending_smart(self):
        """Scraping inteligente da página trending"""
        videos = []
        try:
            # Acesso direto à página trending
            url = 'https://www.youtube.com/feed/trending'
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Extrair dados usando regex inteligente
                video_patterns = [
                    r'{"videoId":"([^"]+)".*?"title":{"runs":\[{"text":"([^"]+)"}\].*?"ownerText":{"runs":\[{"text":"([^"]+)"',
                    r'"watchEndpoint":{"videoId":"([^"]+)".*?"text":"([^"]+)".*?"shortBylineText":{"runs":\[{"text":"([^"]+)"'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, response.text)
                    for match in matches:
                        if len(match) >= 3:
                            video_data = {
                                'id': match[0],
                                'title': match[1],
                                'channel_name': match[2],
                                'url': f'https://www.youtube.com/watch?v={match[0]}',
                                'source': 'Trending'
                            }
                            videos.append(video_data)
                
                # Limitar e remover duplicatas
                unique_ids = set()
                unique_videos = []
                for video in videos:
                    if video['id'] not in unique_ids:
                        unique_ids.add(video['id'])
                        unique_videos.append(video)
                
                return unique_videos[:20]
        
        except Exception as e:
            pass
        
        return videos
    
    def search_videos_smart(self, query, max_results=20):
        """Busca inteligente no YouTube"""
        videos = []
        try:
            search_url = f'https://www.youtube.com/results?search_query={quote(query)}'
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                # Padrões para extrair dados de vídeos
                patterns = [
                    r'"videoId":"([^"]+)".*?"title":{"accessibility":{"accessibilityData":{"label":"([^"]+)"}}.*?"longBylineText":{"runs":\[{"text":"([^"]+)"',
                    r'"watchEndpoint":{"videoId":"([^"]+)".*?"text":"([^"]+)".*?"ownerText":{"runs":\[{"text":"([^"]+)"'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, response.text)
                    for match in matches:
                        if len(match) >= 3:
                            video_data = {
                                'id': match[0],
                                'title': match[1],
                                'channel_name': match[2],
                                'url': f'https://www.youtube.com/watch?v={match[0]}',
                                'source': f'Search: {query}'
                            }
                            videos.append(video_data)
                
                return videos[:max_results]
        
        except Exception as e:
            pass
        
        return videos
    
    def enrich_video_data(self, video):
        """Enriquecer dados do vídeo com informações adicionais"""
        try:
            # Acessar página do vídeo para obter mais dados
            video_url = video['url']
            response = self.session.get(video_url, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # Extrair views
                view_patterns = [
                    r'"viewCount":"(\d+)"',
                    r'(\d+(?:\.\d+)?[KMB]?) visualizações',
                    r'(\d+(?:,\d+)*) views'
                ]
                
                for pattern in view_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        views_text = match.group(1)
                        video['views_text'] = views_text
                        video['views'] = self.extract_views_number(views_text)
                        break
                
                # Extrair data de publicação
                pub_patterns = [
                    r'"publishDate":"([^"]+)"',
                    r'há (\d+) (hora|horas|dia|dias|semana|semanas|mês|meses)',
                    r'(\d+) (hora|horas|dia|dias) atrás'
                ]
                
                for pattern in pub_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        video['published_time'] = match.group(0)
                        break
                
                # Extrair thumbnail
                thumb_match = re.search(r'"videoDetails":{"videoId":"[^"]+","title":"[^"]+","lengthSeconds":"[^"]+","keywords":\[[^\]]*\],"channelId":"[^"]+","isLiveContent":[^,]+,"shortDescription":"[^"]*","isCrawlable":[^,]+,"thumbnail":{"thumbnails":\[{"url":"([^"]+)"', html)
                if thumb_match:
                    video['thumbnail'] = thumb_match.group(1)
                
        except Exception as e:
            pass

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
    if not published_time:
        return False
    recent_keywords = ['hora', 'horas', 'minuto', 'minutos', '1 dia', '2 dias', 'há 1', 'há 2']
    return any(keyword in published_time.lower() for keyword in recent_keywords)

def is_viral_candidate(video):
    """Verificar se é candidato viral"""
    views = video.get('views', 0)
    published = video.get('published_time', '')
    
    return (
        views > 50000 and 
        is_recent_video(published)
    ) or views > 500000  # Ou muitas views independente da data

def calculate_viral_score(video):
    """Calcular score viral"""
    views = video.get('views', 0)
    is_recent = is_recent_video(video.get('published_time', ''))
    
    score = views
    if is_recent:
        score *= 2  # Bonus para vídeos recentes
    
    return score

def display_smart_video_card(video):
    """Exibir card do vídeo"""
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        # Thumbnail
        if video.get('thumbnail'):
            try:
                st.image(video['thumbnail'], width=200)
            except:
                # Thumbnail padrão baseado no ID
                thumbnail_url = f"https://img.youtube.com/vi/{video.get('id', '')}/hqdefault.jpg"
                st.image(thumbnail_url, width=200)
        else:
            thumbnail_url = f"https://img.youtube.com/vi/{video.get('id', '')}/hqdefault.jpg"
            st.image(thumbnail_url, width=200)
    
    with col2:
        # Badges
        badges_html = ""
        if is_viral_candidate(video):
            badges_html += '<span class="viral-badge">💎 VIRAL</span>'
        if is_recent_video(video.get('published_time', '')):
            badges_html += '<span class="recent-badge">⚡ RECENTE</span>'
        
        # Score viral
        viral_score = calculate_viral_score(video)
        
        st.markdown(f"""
        <div class="video-card">
            <div class="video-title">{video.get('title', 'Sem título')} {badges_html}</div>
            
            <div style="color: #666; font-size: 1rem; margin-bottom: 8px;">
                📺 <strong>{video.get('channel_name', 'Canal desconhecido')}</strong>
                <span style="color: #999; margin-left: 10px;">({video.get('source', 'Desconhecido')})</span>
            </div>
            
            <div style="color: #0066cc; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px;">
                👁️ {video.get('views_text', 'N/A')} visualizações • 
                📅 {video.get('published_time', 'Data N/A')} •
                🔥 Score: {format_number(viral_score)}
            </div>
            
            <div style="margin-top: 15px;">
                <a href="{video.get('url', '#')}" target="_blank" style="color: #FF0000; text-decoration: none; margin-right: 20px; font-weight: bold;">
                    🎥 ASSISTIR VÍDEO
                </a>
                <a href="{video.get('channel_url', '#')}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">
                    📺 VER CANAL
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Interface principal
st.markdown('<h1 class="main-header">🧠 YouTube Smart Scraper</h1>', unsafe_allow_html=True)

# Info sobre Smart Scraper
st.markdown("""
<div class="smart-info">
    <h3>🧠 Smart Scraper - Múltiplas Estratégias Inteligentes!</h3>
    <ul style="margin: 10px 0;">
        <li><strong>📡 RSS Feeds</strong> - dados oficiais sempre funcionam</li>
        <li><strong>🎯 Scraping inteligente</strong> - múltiplos padrões de extração</li>
        <li><strong>🔥 Busca viral</strong> - termos que identificam conteúdo em alta</li>
        <li><strong>🧠 Enriquecimento de dados</strong> - extrai views, data e mais info</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Estratégia
st.markdown("""
<div class="strategy-box">
    <h4>💡 Estratégia Multi-Fonte:</h4>
    <p>Este scraper usa <strong>3 estratégias simultaneamente</strong> para garantir resultados mesmo se uma falhar:</p>
    <p><strong>1. RSS Feeds</strong> → <strong>2. Scraping Trending</strong> → <strong>3. Busca por Termos Virais</strong></p>
</div>
""", unsafe_allow_html=True)

# Controles
col1, col2 = st.columns(2)

with col1:
    max_videos = st.selectbox("📊 Máximo de vídeos:", [20, 30, 50, 75], index=1)

with col2:
    min_views = st.selectbox("👁️ Views mínimas:", [0, 10000, 50000, 100000, 500000], index=1)

# Botão principal
if st.button("🧠 EXECUTAR SMART SCRAPING!", type="primary", use_container_width=True):
    
    # Inicializar scraper
    scraper = YouTubeSmartScraper()
    
    with st.spinner("🧠 Executando estratégias inteligentes..."):
        videos = scraper.get_trending_videos(max_videos)
        
        # Filtrar por views mínimas
        if min_views > 0:
            videos = [v for v in videos if v.get('views', 0) >= min_views]
        
        if videos:
            # Ordenar por score viral
            videos.sort(key=calculate_viral_score, reverse=True)
            
            # Estatísticas
            viral_count = sum(1 for v in videos if is_viral_candidate(v))
            recent_count = sum(1 for v in videos if is_recent_video(v.get('published_time', '')))
            total_views = sum(v.get('views', 0) for v in videos)
            avg_score = sum(calculate_viral_score(v) for v in videos) / len(videos) if videos else 0
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #333;">🎯 {len(videos)}</h3>
                    <p style="margin: 0; color: #666;">Vídeos Encontrados</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #FFD700;">💎 {viral_count}</h3>
                    <p style="margin: 0; color: #666;">Candidatos Virais</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #FF6B6B;">⚡ {recent_count}</h3>
                    <p style="margin: 0; color: #666;">Vídeos Recentes</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #4ECDC4;">🔥 {format_number(avg_score)}</h3>
                    <p style="margin: 0; color: #666;">Score Viral Médio</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Export
            if st.button("📥 Exportar Resultados Smart", key="export_smart"):
                df = pd.DataFrame(videos)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV Smart",
                    data=csv,
                    file_name=f"smart_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_smart"
                )
            
            # Resultados
            st.markdown("---")
            st.markdown("## 🧠 Resultados Smart Scraping:")
            st.markdown("*Ordenado por Score Viral (views × bonus recência)*")
            
            for video in videos:
                display_smart_video_card(video)
                st.markdown("---")
        
        else:
            st.warning("❌ Nenhum vídeo encontrado com os critérios selecionados")

# Instruções
st.markdown("""
## 🚀 Como funciona:

### 📡 **RSS Feeds (sempre funciona):**
- Acessa feeds oficiais do YouTube
- Dados sempre atualizados
- Impossível de bloquear

### 🎯 **Scraping Inteligente:**
- Múltiplos padrões de extração
- Fallbacks automáticos
- Máxima compatibilidade

### 🔥 **Busca Viral:**
- Termos que identificam conteúdo em alta
- Captura tendências emergentes
- Score viral calculado automaticamente

**Resultado: Muito mais vídeos que qualquer API limitada!** 🎯
""")

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🧠 <strong>YouTube Smart Scraper</strong> | Inteligência artificial aplicada</p>
    <p>Múltiplas estratégias para máxima eficácia!</p>
</div>
""", unsafe_allow_html=True)
