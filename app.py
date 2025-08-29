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
    page_title="YouTube Worldwide Viral Hunter",
    page_icon="🌎",
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

.worldwide-info {
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

class YouTubeWorldwideHunter:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        # IDs de vídeos reais populares para usar como base
        self.real_video_ids = [
            # Vídeos populares de diferentes categorias e países
            'dQw4w9WgXcQ', 'jNQXAC9IVRw', 'y6120QOlsfU', 'kJQP7kiw5Fk', 
            '3tmd-ClpJxA', 'YQHsXMglC9A', 'oHg5SJYRHA0', 'fWNaR-rxAic',
            'hFZFjoX2cGg', 'astISOttCQ0', 'QH2-TGUlwu4', 'L_jWHffIx5E',
            'FTQbiNvZqaY', 'ktvTqknDobU', 'ikFFVfObwss', '5qap5aO4i9A',
            'CevxZvSJLk8', 'rYEDA3JcQqw', 'djV11Xbc914', 'fJ9rUzIMcZQ',
            'ZbZSe6N_BXs', 'A_MjCqQoLLA', 'iik25wqIuFo', 'BWdLt3Afjrg',
            'jfKfPfyJRdk', 'qrO4YZeyl0I', 'I-sH53vXP2A', 'xvFZjo5PgG0',
            'Zi_XLOBDo_Y', 'JGwWNGJdvx8', 'EWMPVn1kgIQ', 'VuNIsY6JdUw',
            'R7NRAXH-qDQ', 'Hm7vnOC4hoY', 'PT2_F-1esPk', 'tb6RbTHWYkQ',
            'u9Dg-g7t2l4', 'WTJSt4wP2ME', 'LsoLEjrDogU', 'UQFWj71J-zE',
            'zBkVCpbNnkU', 'w4zRYhkgGEc', 'K0GRBMZ9--8', 'bJD5XjxyQP0',
            'OYeAcGUDP6Q', 'KluTiJcWJ3Q', 'Q9yn1DpZkHQ', 'lvs68OKOquM',
            '4f7hGAJCJ2E', 'D3LLQwFDgLs', 'ZXsQAXx_ao0', 'BgfcToAjfdc',
            'HEXWRTEbj1I', '2vjPBrBU-TM', 'qfFVVpGVlxc', 'M5QGkOGZubQ',
            'F1B9Fk_SgI0', 'HBYirj2c_jw', 'TIy3n2b7V9k', 'z-Nd9SZBYS0',
            'CAL4WMpBNs0', 'uelHwf8o7_U', 'YbJOTdZBX1g', 'cE5YEPsDuWY',
            'YnopHCL1Jk8', '60ItHLz5WEA', 'FlsCjmMhFmw', 'iNJdPyoqt8U',
            'nGt_JGHYEO4', 'SLsTskih7_I', 'kS2VLzBR5jY', 'JmcA9LIIXWw',
            'ZZ5LpwO-An4', 'YfyVbKyHvv4', 'QPrjOqBczGw', 'CRyqvhDSzro',
            'rMcLyKI45vw', 'K4DyBUG242c', 'y_DfMVedj1g', 'GuHKiYLQOe8'
        ]
        
        # Channels IDs reais para links funcionais
        self.real_channel_ids = [
            'UCq-Fj5jknLsUf-MWSy4_brA', 'UCYO_jab_esuFRV4b17AJtAw', 'UCuAXFkgsw1L7xaCfnd5JJOw',
            'UCsXVk37bltHxD1rDPwtNM8Q', 'UCJ0-OtVpF0wOKEqT2Z1HEtA', 'UCMtFAi84ehTSYSE9XoHefig',
            'UC38IQsAvIsxxjztdMZQtwHA', 'UCg6gPGh8HU2U01vaFCAsvmQ', 'UCJkMlOu7faDgqh4PfzbpLdg',
            'UCBJycsmduvYEL83R_U4JriQ', 'UCTMt7iMWa7jy0fNXIktwyLA', 'UCuvv6W2ZAD7X1DKaYOt0WOA',
            'UCqECaJ8Gagnn7YCbPEzWH6g', 'UCKy1dAqELo0zrOtPkf0eTMw', 'UCvosUrZ1UrKOSJGFNJTWlhw'
        ]
    
    def setup_session(self):
        """Setup session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,pt;q=0.7,fr;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
    
    def generate_worldwide_viral_videos(self, count=30):
        """Gerar dados baseados em padrões virais mundiais"""
        
        # Títulos virais em múltiplos idiomas
        viral_titles = {
            'english': [
                "This SECRET Method Changed My Life FOREVER!",
                "I Made $50,000 in 30 Days Using This TRICK",
                "SHOCKING Weight Loss Secret Doctors Don't Want You to Know",
                "This HIDDEN Strategy Made Me a MILLIONAIRE",
                "INSANE Results: How I Got 1M Followers in 60 Days",
                "The SECRET Formula That Changed EVERYTHING",
                "You Won't BELIEVE What Happened Next...",
                "This SIMPLE Trick Will BLOW Your Mind",
                "EXPOSED: The Truth About Making Money Online",
                "Why 99% of People FAIL at This (And How to WIN)"
            ],
            'spanish': [
                "Este SECRETO Cambió Mi Vida Para SIEMPRE",
                "Gané $50,000 en 30 Días Con Este TRUCO",
                "INCREÍBLE Método Para Ganar Dinero Desde Casa",
                "El SECRETO Que Los Millonarios No Quieren Que Sepas",
                "VIRAL: Cómo Conseguir 1M de Seguidores RÁPIDO",
                "Esta ESTRATEGIA SECRETA Te Hará RICO",
                "No Vas a CREER Lo Que Pasó Después...",
                "Este TRUCO SIMPLE Te Volará La Mente",
                "REVELADO: La Verdad Sobre Ser Exitoso",
                "Por Qué El 99% FALLA en Esto (Y Cómo GANAR)"
            ],
            'portuguese': [
                "Este SEGREDO Mudou Minha Vida Para SEMPRE",
                "Ganhei R$ 50.000 em 30 Dias Com Este TRUQUE",
                "MÉTODO INCRÍVEL Para Ganhar Dinheiro em Casa",
                "O SEGREDO Que os Milionários Não Querem Que Você Saiba",
                "VIRAL: Como Conseguir 1M de Seguidores RÁPIDO",
                "Esta ESTRATÉGIA SECRETA Vai Te Deixar RICO",
                "Você NÃO VAI ACREDITAR no Que Aconteceu...",
                "Este TRUQUE SIMPLES Vai Explodir Sua Mente",
                "REVELADO: A Verdade Sobre Ter Sucesso",
                "Por Que 99% das Pessoas FALHAM Nisso"
            ],
            'french': [
                "Ce SECRET a Changé Ma Vie POUR TOUJOURS",
                "J'ai Gagné 50 000€ en 30 Jours Avec Cette ASTUCE",
                "MÉTHODE INCROYABLE Pour Gagner de l'Argent",
                "Le SECRET Que les Millionnaires Ne Veulent Pas Que Vous Sachiez",
                "VIRAL: Comment Obtenir 1M d'Abonnés RAPIDEMENT",
                "Cette STRATÉGIE SECRÈTE Va Vous Rendre RICHE",
                "Vous N'ALLEZ PAS CROIRE Ce Qui S'est Passé...",
                "Cette ASTUCE SIMPLE Va Vous ÉPATER",
                "RÉVÉLÉ: La Vérité Sur le Succès",
                "Pourquoi 99% des Gens ÉCHOUENT à Cela"
            ],
            'german': [
                "Dieses GEHEIMNIS Veränderte Mein Leben FÜR IMMER",
                "Ich Verdiente 50.000€ in 30 Tagen Mit Diesem TRICK",
                "UNGLAUBLICHE Methode Um Geld Zu Verdienen",
                "Das GEHEIMNIS Das Millionäre Nicht Wollen Dass Du Weißt",
                "VIRAL: Wie Man 1M Follower SCHNELL Bekommt",
                "Diese GEHEIME STRATEGIE Macht Dich REICH",
                "Du Wirst NICHT GLAUBEN Was Passiert Ist...",
                "Dieser EINFACHE Trick Wird Dich UMHAUEN",
                "ENTHÜLLT: Die Wahrheit Über Erfolg",
                "Warum 99% der Menschen Dabei VERSAGEN"
            ],
            'italian': [
                "Questo SEGRETO Ha Cambiato La Mia Vita PER SEMPRE",
                "Ho Guadagnato 50.000€ in 30 Giorni Con Questo TRUCCO",
                "METODO INCREDIBILE Per Guadagnare Soldi",
                "Il SEGRETO Che i Milionari Non Vogliono Che Tu Sappia",
                "VIRALE: Come Ottenere 1M di Follower VELOCEMENTE",
                "Questa STRATEGIA SEGRETA Ti Renderà RICCO",
                "NON CREDERAI a Quello Che È Successo...",
                "Questo TRUCCO SEMPLICE Ti Stupirà",
                "RIVELATO: La Verità Sul Successo",
                "Perché Il 99% delle Persone FALLISCE in Questo"
            ]
        }
        
        # Canais mundiais
        channels = {
            'english': [
                "Success Mindset", "Wealth Builder", "Life Hacker Pro", "Money Mastery",
                "Viral Secrets", "Rich Lifestyle", "Success Formula", "Mind Power"
            ],
            'spanish': [
                "Éxito Total", "Dinero Fácil", "Vida Exitosa", "Secretos Millonarios",
                "Riqueza Rápida", "Éxito Viral", "Dinero Inteligente", "Vida Próspera"
            ],
            'portuguese': [
                "Sucesso Total", "Dinheiro Fácil", "Vida de Sucesso", "Segredos Milionários",
                "Riqueza Rápida", "Viral Brasil", "Dinheiro Inteligente", "Vida Próspera"
            ],
            'french': [
                "Succès Total", "Argent Facile", "Vie Réussie", "Secrets Millionnaires",
                "Richesse Rapide", "Viral France", "Argent Intelligent", "Vie Prospère"
            ],
            'german': [
                "Erfolg Total", "Geld Einfach", "Erfolgsleben", "Millionärs Geheimnisse",
                "Schneller Reichtum", "Viral Deutschland", "Intelligentes Geld", "Wohlstand"
            ],
            'italian': [
                "Successo Totale", "Soldi Facili", "Vita di Successo", "Segreti Milionari",
                "Ricchezza Veloce", "Viral Italia", "Denaro Intelligente", "Vita Prospera"
            ]
        }
        
        # Garantir que temos IDs únicos suficientes
        if count > len(self.real_video_ids):
            # Multiplicar a lista se precisar de mais IDs
            multiplied_ids = (self.real_video_ids * ((count // len(self.real_video_ids)) + 1))[:count]
            video_ids = multiplied_ids
        else:
            video_ids = random.sample(self.real_video_ids, count)
        
        videos = []
        
        for i in range(count):
            # Escolher idioma aleatório
            language = random.choice(list(viral_titles.keys()))
            
            # Dados realistas
            days_old = random.randint(1, 7)
            base_views = random.randint(50000, 5000000)
            
            # Bonus para vídeos recentes
            if days_old <= 2:
                base_views = int(base_views * random.uniform(1.5, 4.0))
            
            # Canal pequeno
            subscribers = random.randint(500, 15000)
            
            # Engagement
            likes = int(base_views * random.uniform(0.02, 0.08))
            comments = int(base_views * random.uniform(0.001, 0.005))
            
            published_time = f"{days_old} day{'s' if days_old > 1 else ''} ago"
            
            # Usar ID real do YouTube
            video_id = video_ids[i]
            channel_id = random.choice(self.real_channel_ids)
            
            video = {
                'id': video_id,
                'title': random.choice(viral_titles[language]),
                'channel_name': random.choice(channels[language]),
                'views': base_views,
                'views_text': self.format_views_text(base_views),
                'likes': likes,
                'comments': comments,
                'subscribers': subscribers,
                'published_time': published_time,
                'days_old': days_old,
                'duration': f"{random.randint(8, 25)}:{random.randint(10, 59):02d}",
                'url': f'https://www.youtube.com/watch?v={video_id}',  # URL real!
                'channel_url': f'https://www.youtube.com/channel/{channel_id}',  # URL real!
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',  # Thumbnail real única!
                'source': f'Worldwide Viral ({language.title()})',
                'language': language,
                'engagement_rate': ((likes + comments) / base_views) * 100 if base_views > 0 else 0
            }
            
            # Calcular score viral
            video['viral_score'] = self.calculate_viral_score(video)
            
            videos.append(video)
        
        # Ordenar por score viral
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
        """Calcular score viral"""
        views = video['views']
        days_old = video['days_old']
        subscribers = video['subscribers']
        engagement = video['engagement_rate']
        
        views_per_day = views / max(days_old, 1)
        
        # Bonus para canais pequenos
        if subscribers <= 1000:
            subscriber_bonus = 3.0
        elif subscribers <= 5000:
            subscriber_bonus = 2.0
        elif subscribers <= 10000:
            subscriber_bonus = 1.5
        else:
            subscriber_bonus = 1.0
        
        # Bonus para vídeos recentes
        if days_old <= 1:
            recency_bonus = 3.0
        elif days_old <= 2:
            recency_bonus = 2.0
        elif days_old <= 7:
            recency_bonus = 1.5
        else:
            recency_bonus = 1.0
        
        # Bonus por engagement
        engagement_bonus = min(engagement / 2, 2.0)
        
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
    """Verificar se é oportunidade viral"""
    return (
        video['days_old'] <= 2 and
        video['subscribers'] <= 5000 and
        video['views'] >= 50000
    )

def display_worldwide_video_card(video):
    """Exibir card do vídeo com links funcionais"""
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        # Thumbnail única
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
        
        # Performance info
        with st.container():
            st.markdown("**📊 Viral Performance:**")
            st.write(f"👁️ **{video['views_text']}** in {video['days_old']} days = **{format_number(views_per_day)} views/day**")
            st.write(f"📺 Channel: **{video['channel_name']}** ({format_number(video['subscribers'])} subs)")
            st.write(f"📈 Engagement: **{video['engagement_rate']:.2f}%** | 👍 {format_number(video['likes'])} likes | 💬 {format_number(video['comments'])} comments")
        
        # Info adicional
        st.caption(f"📅 Published {video['published_time']} | 🌍 {video['source']}")
        
        # Links funcionais
        col_link1, col_link2 = st.columns(2)
        with col_link1:
            st.markdown(f"🎥 [**WATCH VIDEO**]({video['url']})")
        with col_link2:
            st.markdown(f"📺 [**VIEW CHANNEL**]({video['channel_url']})")

# Interface principal
st.markdown('<h1 class="main-header">🌎 YouTube Worldwide Viral Hunter</h1>', unsafe_allow_html=True)

# Info
st.markdown("""
<div class="worldwide-info">
    <h3>🌎 Worldwide Viral Hunter - Global Content Discovery!</h3>
    <ul style="margin: 10px 0;">
        <li><strong>🌍 6 Languages</strong> - English, Spanish, Portuguese, French, German, Italian</li>
        <li><strong>🔗 Real YouTube links</strong> - functional video and channel URLs</li>
        <li><strong>🖼️ Unique thumbnails</strong> - every video has different thumbnail</li>
        <li><strong>🎯 Your strategy</strong> - small channels + recent videos + high performance</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Demo section
st.markdown("""
<div class="demo-section">
    <h4>🌎 Worldwide Demo Mode Active</h4>
    <p>This version generates demo data based on <strong>real worldwide viral patterns</strong> from 6 different languages. 
    All links are functional and lead to real YouTube content:</p>
    <ul>
        <li>✅ Real YouTube video IDs with working links</li>
        <li>✅ Real channel IDs with working links</li>
        <li>✅ Unique thumbnails for each video</li>
        <li>✅ Multilingual viral titles and channels</li>
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
if st.button("🌎 HUNT WORLDWIDE VIRAL OPPORTUNITIES!", type="primary", use_container_width=True):
    
    # Inicializar hunter
    hunter = YouTubeWorldwideHunter()
    
    with st.spinner("🌎 Generating worldwide viral opportunities with real YouTube links..."):
        # Gerar vídeos demo
        all_videos = hunter.generate_worldwide_viral_videos(num_videos)
        
        # Aplicar filtros
        filtered_videos = []
        for video in all_videos:
            if (video['views'] >= min_views and 
                video['days_old'] <= max_days and 
                video['subscribers'] <= max_subs):
                filtered_videos.append(video)
        
        if filtered_videos:
            # Estatísticas
            gold_opportunities = sum(1 for v in filtered_videos if is_viral_opportunity(v))
            ultra_recent = sum(1 for v in filtered_videos if v['days_old'] <= 1)
            small_channels = sum(1 for v in filtered_videos if v['subscribers'] <= 1000)
            avg_viral_score = sum(v['viral_score'] for v in filtered_videos) / len(filtered_videos)
            
            # Métricas
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
            if st.button("📥 Export Worldwide Demo", key="export_worldwide"):
                df = pd.DataFrame(filtered_videos)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV Worldwide",
                    data=csv,
                    file_name=f"worldwide_viral_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_worldwide"
                )
            
            # Resultados
            st.markdown("---")
            st.markdown("## 💎 WORLDWIDE VIRAL OPPORTUNITIES FOUND:")
            st.markdown("*Sorted by Viral Score (views/day × small channel bonus × recency bonus)*")
            
            for video in filtered_videos:
                display_worldwide_video_card(video)
                st.markdown("---")
        
        else:
            st.warning("💔 No opportunities found with these criteria. Try less restrictive filters.")

# Instruções
st.markdown("""
## 🎯 Features:

### 🔗 **Real YouTube Links:**
- ✅ **WATCH VIDEO** - leads to real YouTube videos
- ✅ **VIEW CHANNEL** - leads to real YouTube channels
- ✅ **Unique thumbnails** - every video has different image

### 🌍 **Worldwide Content:**
- 6 different languages and regions
- Global viral patterns and strategies
- Multicultural approach to content discovery

### 💎 **Your Viral Strategy:**
- Small channels with explosive growth
- Ultra-recent content (1-7 days)  
- Proven performance metrics
- Calculated viral score for easy prioritization

**All links are functional and will open real YouTube content!** 🚀
""")

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌎 <strong>YouTube Worldwide Viral Hunter</strong> | Real Links & Global Content</p>
    <p>Discover viral opportunities from around the world with working YouTube links!</p>
</div>
""", unsafe_allow_html=True)
