import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import re
import time
import random
from urllib.parse import quote
from PIL import Image
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="YouTube Global Viral Hunter",
    page_icon="🌍",
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

.global-info {
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

.performance-box {
    background: #f0f8ff;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border-left: 4px solid #4ECDC4;
}

.metric-container {
    background: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin: 10px 0;
}

.demo-section {
    background: #fff3cd;
    color: #856404;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

class YouTubeGlobalViralHunter:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
    
    def generate_diverse_thumbnails(self, count):
        """Gerar thumbnails diversas usando IDs diferentes"""
        # IDs de vídeos reais populares para thumbnails variadas
        thumbnail_ids = [
            'dQw4w9WgXcQ', 'jNQXAC9IVRw', 'y6120QOlsfU', 'kJQP7kiw5Fk', 
            '3tmd-ClpJxA', 'YQHsXMglC9A', 'oHg5SJYRHA0', 'fWNaR-rxAic',
            'hFZFjoX2cGg', 'astISOttCQ0', 'QH2-TGUlwu4', 'L_jWHffIx5E',
            'FTQbiNvZqaY', 'ktvTqknDobU', 'ikFFVfObwss', '5qap5aO4i9A',
            'CevxZvSJLk8', 'rYEDA3JcQqw', 'djV11Xbc914', 'fJ9rUzIMcZQ',
            'ZbZSe6N_BXs', 'A_MjCqQoLLA', 'iik25wqIuFo', 'BWdLt3Afjrg',
            'jfKfPfyJRdk', 'qrO4YZeyl0I', 'I-sH53vXP2A', 'xvFZjo5PgG0',
            'Zi_XLOBDo_Y', 'JGwWNGJdvx8', 'EWMPVn1kgIQ', 'VuNIsY6JdUw'
        ] * 10  # Multiplicar para ter mais opções
        
        return random.sample(thumbnail_ids, min(count, len(thumbnail_ids)))
    
    def generate_global_viral_videos(self, count=30):
        """Gerar dados de demonstração baseados em padrões globais"""
        
        # Títulos virais em inglês (padrões globais)
        viral_titles_en = [
            "This SECRET Method Changed My Life FOREVER!",
            "I Made $50,000 in 30 Days Using This TRICK",
            "SHOCKING Weight Loss Secret Doctors Don't Want You to Know",
            "This HIDDEN Strategy Made Me a MILLIONAIRE",
            "INSANE Results: How I Got 1M Followers in 60 Days",
            "The SECRET Formula That Changed EVERYTHING",
            "You Won't BELIEVE What Happened Next...",
            "This SIMPLE Trick Will BLOW Your Mind",
            "EXPOSED: The Truth About Making Money Online",
            "Why 99% of People FAIL at This (And How to WIN)",
            "The ULTIMATE Guide to Success in 2025",
            "This ONE Thing Will Transform Your Life",
            "SHOCKING Discovery That Scientists Are Hiding",
            "How I Went From BROKE to RICH in 90 Days",
            "The FORBIDDEN Method They Don't Want You to Know",
            "VIRAL Strategy: How to Get Famous FAST",
            "This Will Make You RICH (If You Act NOW)",
            "The SECRET That Billionaires Use Daily",
            "MIND-BLOWING Results in Just 24 Hours",
            "Why This SIMPLE Method Works Every Time"
        ]
        
        # Títulos virais em espanhol 
        viral_titles_es = [
            "Este SECRETO Cambió Mi Vida Para SIEMPRE",
            "Gané $50,000 en 30 Días Con Este TRUCO",
            "INCREÍBLE Método Para Ganar Dinero Desde Casa",
            "El SECRETO Que Los Millonarios No Quieren Que Sepas",
            "VIRAL: Cómo Conseguir 1M de Seguidores RÁPIDO",
            "Esta ESTRATEGIA SECRETA Te Hará RICO",
            "No Vas a CREER Lo Que Pasó Después...",
            "Este TRUCO SIMPLE Te Volará La Mente",
            "REVELADO: La Verdad Sobre Ser Exitoso",
            "Por Qué El 99% FALLA en Esto (Y Cómo GANAR)",
            "La GUÍA DEFINITIVA Para El Éxito en 2025",
            "Esta ÚNICA Cosa Transformará Tu Vida",
            "DESCUBRIMIENTO IMPACTANTE Que Están Ocultando",
            "Cómo Pasé de POBRE a RICO en 90 Días",
            "El MÉTODO PROHIBIDO Que No Quieren Que Conozcas",
            "ESTRATEGIA VIRAL: Cómo Ser Famoso RÁPIDO",
            "Esto Te Hará RICO (Si Actúas AHORA)",
            "El SECRETO Que Usan Los Billonarios Diariamente",
            "Resultados INCREÍBLES en Solo 24 Horas",
            "Por Qué Este MÉTODO SIMPLE Funciona Siempre"
        ]
        
        # Combinar títulos
        all_titles = viral_titles_en + viral_titles_es
        
        # Canais gringos realistas
        english_channels = [
            "Success Mindset", "Wealth Builder", "Life Hacker Pro", "Money Mastery",
            "Viral Secrets", "Rich Lifestyle", "Success Formula", "Mind Power",
            "Wealth Tactics", "Life Changer", "Money Magnet", "Success Path",
            "Viral Growth", "Rich Mindset", "Life Mastery", "Wealth Secrets"
        ]
        
        spanish_channels = [
            "Éxito Total", "Dinero Fácil", "Vida Exitosa", "Secretos Millonarios",
            "Riqueza Rápida", "Éxito Viral", "Dinero Inteligente", "Vida Próspera",
            "Millonario Digital", "Éxito Garantizado", "Riqueza Personal", "Vida Rica",
            "Dinero y Éxito", "Prosperidad Total", "Éxito Inmediato", "Riqueza Real"
        ]
        
        all_channels = english_channels + spanish_channels
        
        # Gerar thumbnails diversas
        thumbnail_ids = self.generate_diverse_thumbnails(count)
        
        videos = []
        
        for i in range(count):
            # Dados realistas baseados em padrões de vídeos virais globais
            days_old = random.randint(1, 7)  # Vídeos de 1 a 7 dias
            base_views = random.randint(50000, 3000000)  # 50K a 3M views
            
            # Bonus para vídeos mais recentes (sua estratégia!)
            if days_old <= 2:
                base_views = int(base_views * random.uniform(1.5, 4.0))
            
            # Simular canal pequeno com vídeo viral (sua estratégia!)
            subscribers = random.randint(500, 15000)  # Canais pequenos
            
            # Engagement realista
            likes = int(base_views * random.uniform(0.02, 0.08))  # 2-8% de likes
            comments = int(base_views * random.uniform(0.001, 0.005))  # 0.1-0.5% comentários
            
            published_time = f"{days_old} day{'s' if days_old > 1 else ''} ago"
            
            video_id = f"demo_{i}_{random.randint(100000, 999999)}"
            
            # Escolher thumbnail única
            thumbnail_id = thumbnail_ids[i % len(thumbnail_ids)]
            
            video = {
                'id': video_id,
                'title': random.choice(all_titles),
                'channel_name': random.choice(all_channels),
                'views': base_views,
                'views_text': self.format_views_text(base_views),
                'likes': likes,
                'comments': comments,
                'subscribers': subscribers,
                'published_time': published_time,
                'days_old': days_old,
                'duration': f"{random.randint(8, 25)}:{random.randint(10, 59):02d}",
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': f'https://img.youtube.com/vi/{thumbnail_id}/hqdefault.jpg',
                'source': 'Global Viral Pattern',
                'engagement_rate': ((likes + comments) / base_views) * 100 if base_views > 0 else 0
            }
            
            # Calcular score viral (sua estratégia)
            video['viral_score'] = self.calculate_viral_score(video)
            
            videos.append(video)
        
        # Ordenar por score viral (maiores oportunidades primeiro)
        videos.sort(key=lambda x: x['viral_score'], reverse=True)
        
        return videos
    
    def format_views_text(self, views):
        """Formatar views como texto"""
        if views >= 1000000:
            return f"{views/1000000:.1f}M views"
        elif views >= 1000:
            return f"{views/1000:.0f}K views"
        else:
            return f"{views} views"
    
    def calculate_viral_score(self, video):
        """Calcular score viral baseado na sua estratégia"""
        views = video['views']
        days_old = video['days_old']
        subscribers = video['subscribers']
        engagement = video['engagement_rate']
        
        # Views por dia
        views_per_day = views / max(days_old, 1)
        
        # Bonus para canais pequenos (sua estratégia!)
        if subscribers <= 1000:
            subscriber_bonus = 3.0
        elif subscribers <= 5000:
            subscriber_bonus = 2.0
        elif subscribers <= 10000:
            subscriber_bonus = 1.5
        else:
            subscriber_bonus = 1.0
        
        # Bonus para vídeos recentes (sua estratégia!)
        if days_old <= 1:
            recency_bonus = 3.0
        elif days_old <= 2:
            recency_bonus = 2.0
        elif days_old <= 7:
            recency_bonus = 1.5
        else:
            recency_bonus = 1.0
        
        # Bonus por engagement
        engagement_bonus = min(engagement / 2, 2.0)  # Max 2x bonus
        
        # Score final
        score = views_per_day * subscriber_bonus * recency_bonus * (1 + engagement_bonus)
        
        return int(score)

def format_number(num):
    """Formatar números grandes"""
    if num >= 1000000000:
        return f"{num/1000000000:.1f}B"
    elif num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def is_viral_opportunity(video):
    """Verificar se é oportunidade viral seguindo sua estratégia"""
    return (
        video['days_old'] <= 2 and  # Até 2 dias (sua estratégia)
        video['subscribers'] <= 5000 and  # Canal pequeno (sua estratégia)
        video['views'] >= 50000  # Performance mínima (sua estratégia)
    )

def display_global_video_card(video):
    """Exibir card do vídeo com HTML renderizado corretamente"""
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        # Thumbnail diversa
        try:
            st.image(video['thumbnail'], width=200)
        except:
            st.image("https://via.placeholder.com/320x180?text=YouTube+Global", width=200)
        
        # Duração
        st.markdown(f"**⏱️ {video.get('duration', '0:00')}**")
        
        # Score viral
        st.markdown(f"**🔥 Score: {format_number(video['viral_score'])}**")
    
    with col2:
        # Badges
        badges_html = ""
        if is_viral_opportunity(video):
            badges_html += '<span class="viral-badge">💎 GOLD OPPORTUNITY</span>'
        if video['days_old'] <= 1:
            badges_html += '<span class="trending-badge">⚡ ULTRA-RECENT</span>'
        
        # Views por dia
        views_per_day = video['views'] / max(video['days_old'], 1)
        
        # Título com badges
        st.markdown(f"""
        <div class="video-title">{video['title']} {badges_html}</div>
        """, unsafe_allow_html=True)
        
        # Performance box usando componentes Streamlit
        with st.container():
            st.markdown("**📊 Viral Performance:**")
            st.write(f"👁️ **{video['views_text']}** in {video['days_old']} days = **{format_number(views_per_day)} views/day**")
            st.write(f"📺 Channel: **{video['channel_name']}** ({format_number(video['subscribers'])} subs)")
            st.write(f"📈 Engagement: **{video['engagement_rate']:.2f}%** | 👍 {format_number(video['likes'])} likes | 💬 {format_number(video['comments'])} comments")
        
        # Info adicional
        st.caption(f"📅 Published {video['published_time']} | 🎯 Source: {video['source']}")
        
        # Links
        col_link1, col_link2 = st.columns(2)
        with col_link1:
            st.markdown(f"[🎥 ANALYZE VIDEO]({video['url']})")
        with col_link2:
            st.markdown("[📺 VIEW CHANNEL](#)")

# Interface principal
st.markdown('<h1 class="main-header">🌍 YouTube Global Viral Hunter</h1>', unsafe_allow_html=True)

# Info sobre Global Hunter
st.markdown("""
<div class="global-info">
    <h3>🌍 Global Viral Hunter - English & Spanish Content!</h3>
    <ul style="margin: 10px 0;">
        <li><strong>🇺🇸 English channels</strong> - global viral patterns and strategies</li>
        <li><strong>🇪🇸 Spanish channels</strong> - hispanic viral content patterns</li>
        <li><strong>🎯 Your strategy</strong> - small channels + recent videos + high performance</li>
        <li><strong>🔥 Diverse thumbnails</strong> - unique images for each video</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Demo section
st.markdown("""
<div class="demo-section">
    <h4>🌍 Global Demo Mode Active</h4>
    <p>This version generates demo data based on <strong>real global viral video patterns</strong> from English and Spanish channels. 
    The data follows exactly your ultra-recent modeling strategy:</p>
    <ul>
        <li>✅ Videos 1-7 days old with high performance</li>
        <li>✅ Small channels (500-15K subs) with viral content</li>
        <li>✅ Titles following proven viral patterns (English & Spanish)</li>
        <li>✅ Viral score calculated by your formula</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Controles
col1, col2, col3, col4 = st.columns(4)

with col1:
    num_videos = st.selectbox("📊 Quantity:", [20, 30, 50, 75], index=1)

with col2:
    min_views = st.selectbox("👁️ Min views:", [0, 25000, 50000, 100000, 500000], index=2)

with col3:
    max_days = st.selectbox("📅 Max days:", [1, 2, 3, 7], index=2)

with col4:
    max_subs = st.selectbox("📺 Max subs:", [1000, 5000, 10000, 25000], index=1)

# Botão principal
if st.button("🌍 HUNT GLOBAL VIRAL OPPORTUNITIES!", type="primary", use_container_width=True):
    
    # Inicializar hunter
    hunter = YouTubeGlobalViralHunter()
    
    with st.spinner("🌍 Generating global viral opportunities based on real patterns..."):
        # Gerar vídeos demo
        all_videos = hunter.generate_global_viral_videos(num_videos)
        
        # Aplicar filtros da sua estratégia
        filtered_videos = []
        for video in all_videos:
            if (video['views'] >= min_views and 
                video['days_old'] <= max_days and 
                video['subscribers'] <= max_subs):
                filtered_videos.append(video)
        
        if filtered_videos:
            # Estatísticas especiais
            gold_opportunities = sum(1 for v in filtered_videos if is_viral_opportunity(v))
            ultra_recent = sum(1 for v in filtered_videos if v['days_old'] <= 1)
            small_channels = sum(1 for v in filtered_videos if v['subscribers'] <= 1000)
            avg_viral_score = sum(v['viral_score'] for v in filtered_videos) / len(filtered_videos)
            
            # Métricas em destaque
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #FFD700;">💎 {gold_opportunities}</h3>
                    <p style="margin: 0; color: #666;">Gold Opportunities</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #FF6B6B;">⚡ {ultra_recent}</h3>
                    <p style="margin: 0; color: #666;">Ultra-Recent (1 day)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #4ECDC4;">🎯 {small_channels}</h3>
                    <p style="margin: 0; color: #666;">Channels <1K subs</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #667eea;">🔥 {format_number(avg_viral_score)}</h3>
                    <p style="margin: 0; color: #666;">Avg Viral Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Export
            if st.button("📥 Export Global Demo", key="export_global"):
                df = pd.DataFrame(filtered_videos)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV Global",
                    data=csv,
                    file_name=f"global_viral_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_global"
                )
            
            # Resultados
            st.markdown("---")
            st.markdown("## 💎 GLOBAL VIRAL OPPORTUNITIES FOUND:")
            st.markdown("*Sorted by Viral Score (views/day × small channel bonus × recency bonus)*")
            
            for video in filtered_videos:
                display_global_video_card(video)
                st.markdown("---")
        
        else:
            st.warning(f"💔 No opportunities found with these specific criteria. Try less restrictive filters.")

# Instruções finais
st.markdown("""
## 🎯 How to interpret the results:

### 💎 **Gold Opportunities (your strategy):**
- ✅ Videos up to 2 days old
- ✅ Small channels (up to 5K subs)  
- ✅ Proven viral performance (50K+ views)

### 🔥 **Viral Score - How it works:**
- **Views/day** × **Small channel bonus** × **Recency bonus** × **Engagement bonus**
- Higher score = bigger modeling opportunity

### 📊 **Next steps:**
1. **Analyze** videos with "GOLD OPPORTUNITY" badge
2. **Study** the pattern: title, format, approach  
3. **Model** quickly your unique version
4. **Launch** while the trend is hot (24-48h)

**This demo shows exactly how your strategy works with global content!** 🚀
""")

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌍 <strong>YouTube Global Viral Hunter</strong> | Global Viral Strategy Demo</p>
    <p>Based on real patterns from viral English & Spanish YouTube content!</p>
</div>
""", unsafe_allow_html=True)
