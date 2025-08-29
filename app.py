import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from datetime import datetime, timedelta
import re
from PIL import Image
import requests
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="YouTube Selenium Hunter",
    page_icon="🎭",
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

.selenium-info {
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

.status-box {
    background: #d4edda;
    color: #155724;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #28a745;
    margin: 20px 0;
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

class YouTubeSeleniumScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configurar o driver do Selenium com máxima discrição"""
        try:
            chrome_options = Options()
            
            # Configurações para parecer com usuário real
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent realista
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Headless para Streamlit Cloud
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Configurações de idioma
            chrome_options.add_argument('--lang=pt-BR')
            chrome_options.add_experimental_option('prefs', {
                'intl.accept_languages': 'pt-BR,pt,en-US,en'
            })
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Script para remover traces de webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            st.error(f"Erro ao configurar navegador: {str(e)}")
            return False
    
    def human_like_delay(self, min_seconds=1, max_seconds=3):
        """Delay aleatório para simular comportamento humano"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def scroll_page(self, scrolls=3):
        """Scroll realista da página"""
        for i in range(scrolls):
            # Scroll aleatório
            scroll_height = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
            self.human_like_delay(0.5, 1.5)
    
    def extract_number_from_text(self, text):
        """Extrair número de visualizações do texto"""
        if not text:
            return 0
        
        text = text.lower().replace('.', '').replace(',', '')
        
        # Padrões para diferentes idiomas
        patterns = {
            'mil': 1000,
            'k': 1000,
            'milhões': 1000000,
            'milhão': 1000000,
            'm': 1000000,
            'mi': 1000000,
            'bilhões': 1000000000,
            'bilhão': 1000000000,
            'b': 1000000000
        }
        
        for suffix, multiplier in patterns.items():
            if suffix in text:
                numbers = re.findall(r'\d+', text.replace(suffix, ''))
                if numbers:
                    return int(float(numbers[0]) * multiplier)
        
        # Se não encontrou sufixo, pegar apenas números
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0
    
    def scrape_trending_page(self, max_videos=50):
        """Scraper da página de trending com Selenium"""
        videos = []
        
        try:
            st.info("🎭 Navegando para página de trending...")
            
            # Ir para página de trending
            self.driver.get('https://www.youtube.com/feed/trending')
            self.human_like_delay(3, 5)
            
            # Scroll para carregar mais vídeos
            st.info("📜 Carregando mais vídeos...")
            self.scroll_page(5)
            
            # Aguardar carregamento
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "contents"))
            )
            
            # Encontrar vídeos
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div#dismissible')
            
            st.info(f"🔍 Encontrados {len(video_elements)} elementos de vídeo")
            
            for idx, video_element in enumerate(video_elements[:max_videos]):
                try:
                    video_data = self.extract_video_data(video_element)
                    if video_data:
                        videos.append(video_data)
                        
                    # Delay entre extrações
                    if idx % 10 == 0:
                        self.human_like_delay(1, 2)
                        
                except Exception as e:
                    continue
            
            return videos
            
        except Exception as e:
            st.error(f"Erro no scraping de trending: {str(e)}")
            return videos
    
    def extract_video_data(self, video_element):
        """Extrair dados de um elemento de vídeo"""
        try:
            video_data = {}
            
            # Título
            try:
                title_element = video_element.find_element(By.CSS_SELECTOR, 'a#video-title')
                video_data['title'] = title_element.get_attribute('title') or title_element.text
                video_data['url'] = title_element.get_attribute('href')
                
                # Extrair ID do vídeo
                if video_data['url']:
                    video_id_match = re.search(r'watch\?v=([^&]+)', video_data['url'])
                    video_data['id'] = video_id_match.group(1) if video_id_match else ''
            except:
                return None
            
            # Canal
            try:
                channel_element = video_element.find_element(By.CSS_SELECTOR, 'a.yt-simple-endpoint.style-scope.yt-formatted-string')
                video_data['channel_name'] = channel_element.text
                video_data['channel_url'] = channel_element.get_attribute('href')
            except:
                video_data['channel_name'] = 'Canal desconhecido'
                video_data['channel_url'] = ''
            
            # Views e tempo
            try:
                metadata = video_element.find_elements(By.CSS_SELECTOR, 'span.style-scope.ytd-video-meta-block')
                if len(metadata) >= 2:
                    video_data['views_text'] = metadata[0].text
                    video_data['published_time'] = metadata[1].text
                    video_data['views'] = self.extract_number_from_text(metadata[0].text)
                else:
                    video_data['views_text'] = '0 visualizações'
                    video_data['published_time'] = 'Desconhecido'
                    video_data['views'] = 0
            except:
                video_data['views_text'] = '0 visualizações'
                video_data['published_time'] = 'Desconhecido'
                video_data['views'] = 0
            
            # Thumbnail
            try:
                thumbnail_element = video_element.find_element(By.CSS_SELECTOR, 'img')
                video_data['thumbnail'] = thumbnail_element.get_attribute('src')
            except:
                video_data['thumbnail'] = ''
            
            # Duração
            try:
                duration_element = video_element.find_element(By.CSS_SELECTOR, 'span.style-scope.ytd-thumbnail-overlay-time-status-renderer')
                video_data['duration'] = duration_element.text
            except:
                video_data['duration'] = '0:00'
            
            return video_data if video_data.get('title') else None
            
        except Exception as e:
            return None
    
    def search_videos(self, query, max_videos=50):
        """Buscar vídeos com Selenium"""
        videos = []
        
        try:
            st.info(f"🎭 Buscando por: '{query}'...")
            
            # Fazer busca
            search_url = f'https://www.youtube.com/results?search_query={query}'
            self.driver.get(search_url)
            self.human_like_delay(3, 5)
            
            # Scroll para carregar mais resultados
            st.info("📜 Carregando mais resultados...")
            self.scroll_page(5)
            
            # Aguardar carregamento
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "contents"))
            )
            
            # Encontrar vídeos
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.ytd-video-renderer')
            
            st.info(f"🔍 Encontrados {len(video_elements)} resultados")
            
            for idx, video_element in enumerate(video_elements[:max_videos]):
                try:
                    video_data = self.extract_video_data(video_element)
                    if video_data:
                        videos.append(video_data)
                        
                    # Delay entre extrações
                    if idx % 10 == 0:
                        self.human_like_delay(1, 2)
                        
                except Exception as e:
                    continue
            
            return videos
            
        except Exception as e:
            st.error(f"Erro na busca: {str(e)}")
            return videos
    
    def close(self):
        """Fechar o navegador"""
        if self.driver:
            self.driver.quit()

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
    recent_keywords = ['hora', 'horas', 'minuto', 'minutos', '1 dia', '2 dias', 'há 1 dia', 'há 2 dias']
    return any(keyword in published_time.lower() for keyword in recent_keywords)

def is_viral_candidate(video):
    """Verificar se é candidato viral"""
    return (
        video.get('views', 0) > 50000 and
        is_recent_video(video.get('published_time', ''))
    )

def display_selenium_video_card(video):
    """Exibir card do vídeo scrapado com Selenium"""
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
            badges_html += '<span class="viral-badge">💎 VIRAL</span>'
        if is_recent_video(video.get('published_time', '')):
            badges_html += '<span class="recent-badge">⚡ RECENTE</span>'
        
        st.markdown(f"""
        <div class="video-card">
            <div class="video-title">{video.get('title', 'Sem título')} {badges_html}</div>
            
            <div style="color: #666; font-size: 1rem; margin-bottom: 8px;">
                📺 <strong>{video.get('channel_name', 'Canal desconhecido')}</strong>
            </div>
            
            <div style="color: #0066cc; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px;">
                👁️ {video.get('views_text', '0 visualizações')} • 
                📅 {video.get('published_time', 'Data não disponível')}
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
st.markdown('<h1 class="main-header">🎭 YouTube Selenium Hunter</h1>', unsafe_allow_html=True)

# Info sobre Selenium
st.markdown("""
<div class="selenium-info">
    <h3>🎭 Selenium Scraper - Navegador Real Invisível!</h3>
    <ul style="margin: 10px 0;">
        <li><strong>✅ Navegador real</strong> - Chrome invisível simulando usuário</li>
        <li><strong>✅ JavaScript funciona</strong> - carrega conteúdo como usuário real</li>
        <li><strong>✅ Anti-detecção</strong> - headers realistas e comportamento humano</li>
        <li><strong>✅ Muito mais dados</strong> - acessa tudo que um usuário vê</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Status do navegador
if 'scraper_initialized' not in st.session_state:
    st.session_state.scraper_initialized = False
    st.session_state.scraper = None

# Botão para inicializar
if not st.session_state.scraper_initialized:
    if st.button("🚀 INICIALIZAR NAVEGADOR SELENIUM", type="primary"):
        with st.spinner("🎭 Configurando navegador invisível..."):
            scraper = YouTubeSeleniumScraper()
            if scraper.driver:
                st.session_state.scraper = scraper
                st.session_state.scraper_initialized = True
                st.success("✅ Navegador configurado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("❌ Erro ao configurar navegador")

# Interface principal (só aparece após inicializar)
if st.session_state.scraper_initialized:
    
    st.markdown("""
    <div class="status-box">
        <strong>✅ Navegador Ativo:</strong> Chrome headless configurado e pronto para scraping!
    </div>
    """, unsafe_allow_html=True)
    
    # Abas
    tab1, tab2 = st.tabs(["🔥 Trending Selenium", "🔍 Busca Selenium"])
    
    # ABA 1: Trending
    with tab1:
        st.markdown("### 🔥 Trending Real com Selenium")
        
        max_trending_videos = st.selectbox("📊 Máximo de vídeos:", [20, 30, 50, 75], index=1)
        
        if st.button("🎭 SCRAPE TRENDING COM SELENIUM!", type="primary", key="selenium_trending"):
            with st.spinner("🎭 Navegador acessando trending..."):
                trending_videos = st.session_state.scraper.scrape_trending_page(max_trending_videos)
                
                if trending_videos:
                    # Estatísticas
                    viral_count = sum(1 for v in trending_videos if is_viral_candidate(v))
                    recent_count = sum(1 for v in trending_videos if is_recent_video(v.get('published_time', '')))
                    total_views = sum(v.get('views', 0) for v in trending_videos)
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-container">
                            <h3 style="margin: 0; color: #333;">📊 {len(trending_videos)}</h3>
                            <p style="margin: 0; color: #666;">Vídeos Extraídos</p>
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
                            <h3 style="margin: 0; color: #4ECDC4;">👁️ {format_number(total_views)}</h3>
                            <p style="margin: 0; color: #666;">Views Totais</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Export
                    if st.button("📥 Exportar Trending Selenium", key="export_selenium_trending"):
                        df = pd.DataFrame(trending_videos)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="⬇️ Download CSV Selenium",
                            data=csv,
                            file_name=f"selenium_trending_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key="download_selenium_trending"
                        )
                    
                    # Resultados
                    st.markdown("---")
                    st.markdown("## 🎭 Vídeos Trending (Selenium):")
                    
                    for video in trending_videos:
                        display_selenium_video_card(video)
                        st.markdown("---")
                
                else:
                    st.warning("❌ Nenhum vídeo encontrado")
    
    # ABA 2: Busca
    with tab2:
        st.markdown("### 🔍 Busca Real com Selenium")
        
        col1, col2 = st.columns(2)
        with col1:
            search_query_selenium = st.text_input("🔎 Buscar por:", placeholder="Ex: viral, bomba, trending...")
        with col2:
            max_search_videos = st.selectbox("📊 Máx resultados:", [20, 30, 50], index=1)
        
        if st.button("🎭 BUSCAR COM SELENIUM!", type="primary", key="selenium_search"):
            if search_query_selenium:
                with st.spinner(f"🎭 Navegador buscando: '{search_query_selenium}'..."):
                    search_videos = st.session_state.scraper.search_videos(search_query_selenium, max_search_videos)
                    
                    if search_videos:
                        # Estatísticas
                        viral_count = sum(1 for v in search_videos if is_viral_candidate(v))
                        recent_count = sum(1 for v in search_videos if is_recent_video(v.get('published_time', '')))
                        
                        # Métricas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"""
                            <div class="metric-container">
                                <h3 style="margin: 0; color: #333;">🔍 {len(search_videos)}</h3>
                                <p style="margin: 0; color: #666;">Resultados</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="metric-container">
                                <h3 style="margin: 0; color: #FFD700;">💎 {viral_count}</h3>
                                <p style="margin: 0; color: #666;">Virais</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class="metric-container">
                                <h3 style="margin: 0; color: #FF6B6B;">⚡ {recent_count}</h3>
                                <p style="margin: 0; color: #666;">Recentes</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Export
                        if st.button("📥 Exportar Busca Selenium", key="export_selenium_search"):
                            df = pd.DataFrame(search_videos)
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="⬇️ Download CSV Busca",
                                data=csv,
                                file_name=f"selenium_busca_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key="download_selenium_search"
                            )
                        
                        # Resultados
                        st.markdown("---")
                        st.markdown(f"## 🎭 Resultados Selenium: '{search_query_selenium}'")
                        
                        for video in search_videos:
                            display_selenium_video_card(video)
                            st.markdown("---")
                    
                    else:
                        st.warning("❌ Nenhum resultado encontrado")
            else:
                st.warning("⚠️ Digite algo para buscar!")
    
    # Botão para fechar navegador
    if st.button("🔴 FECHAR NAVEGADOR", key="close_selenium"):
        st.session_state.scraper.close()
        st.session_state.scraper_initialized = False
        st.session_state.scraper = None
        st.success("✅ Navegador fechado!")
        st.experimental_rerun()

else:
    # Instruções iniciais
    st.markdown("""
    ## 🎭 Como funciona o Selenium:
    
    ### 🚀 **Vantagens do navegador real:**
    - ✅ **JavaScript executa** - carrega conteúdo dinâmico
    - ✅ **Headers realistas** - parece usuário real
    - ✅ **Scrolling humano** - comportamento natural
    - ✅ **Anti-detecção** - muito difícil de bloquear
    
    ### 🎯 **Para sua estratégia viral:**
    - Acessa páginas exatamente como você
    - Vê todos os vídeos que um usuário veria
    - Extrai dados frescos em tempo real
    - Muito mais resultados que API limitada
    
    **👆 Clique em "INICIALIZAR NAVEGADOR" para começar!**
    """)

# Requirements.txt atualizado
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🎭 <strong>YouTube Selenium Hunter</strong> | Navegador real invisível</p>
    <p>A arma mais poderosa contra as limitações do YouTube!</p>
</div>
""", unsafe_allow_html=True)
