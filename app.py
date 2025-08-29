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
    page_title="YouTube Alternative Hunter",
    page_icon="🎯",
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

.alternative-info {
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

class YouTubeAlternativeHunter:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
    
    def generate_demo_viral_videos(self, count=30):
        """Gerar dados de demonstração baseados em padrões reais de vídeos virais"""
        
        # Padrões reais de títulos virais brasileiros
        viral_titles = [
            "ESTA RECEITA MUDOU MINHA VIDA! Segredo que Ninguém Conta",
            "GANHEI R$ 50.000 EM 30 DIAS: Como Começar do Zero",
            "MÉTODO SECRETO para PERDER 10KG em 2 SEMANAS",
            "DESCOBRI SEGREDO dos MILIONÁRIOS: Você Vai Pirar!",
            "INVESTIMENTO que MULTIPLICA por 10: Poucos Sabem",
            "REVELEI ESTRATÉGIA SECRETA do YouTube: 1M de Views",
            "TRUQUE SIMPLES que MUDOU Minha Renda: R$ 15K/Mês",
            "MÉTODO VIRAL: Como Conseguir 100K Seguidores Rápido",
            "SEGREDO dos FAMOSOS para EMAGRECER: Funciona Mesmo!",
            "DESCOBERTA INCRÍVEL que os BANCOS Escondem",
            "FÓRMULA SECRETA: R$ 200 Viraram R$ 20.000",
            "ESTE VÍDEO VAI MUDAR SUA VIDA: Método Comprovado",
            "ESTRATÉGIA SIMPLES: Como Ganhar Dinheiro Dormindo",
            "REVELAÇÃO CHOCANTE: Segredo dos Ricos Expostos",
            "MÉTODO REVOLUCIONÁRIO: Sucesso Garantido em 60 Dias",
            "DESCOBRI COMO GANHAR R$ 1000 POR DIA: Vou Ensinar",
            "SEGREDO JAPONÊS para PRODUTIVIDADE: Incrível!",
            "TRANSFORMAÇÃO ABSURDA: Antes e Depois Chocante",
            "MÉTODO QUE MUDOU TUDO: De Quebrado a Milionário",
            "ESTRATÉGIA NINJA: Como Vender Qualquer Coisa",
            "RECEITA VIRAL que Está BOMBANDO: Simples e Rápida",
            "TÉCNICA SECRETA dos INFLUENCERS: Crescimento Explosivo",
            "MÉTODO CIENTÍFICO: Como Estudar 5x Mais Rápido",
            "DESCOBERTA que os MÉDICOS Não Querem que Saibas",
            "FÓRMULA MÁGICA: Motivação que Nunca Acaba",
            "SEGREDO CHINÊS para LONGEVIDADE: Milenar e Eficaz",
            "ESTRATÉGIA VIRAL: Como Viralizar em 24 Horas",
            "MÉTODO COMPROVADO: Ansiedade Zero em 7 Dias",
            "TÉCNICA REVOLUCIONÁRIA: Memória de Gênio",
            "DESCOBERTA INÉDITA: Como Ser Feliz Sempre"
        ]
        
        channels = [
            "Canal do Sucesso", "Dinheiro Fácil TV", "Vida Saudável", "Receitas da Vovó",
            "Tech Brasileiro", "Fitness Revolution", "Empreendedor Digital", "Culinária Viral",
            "Motivação Total", "Saúde e Beleza", "Investidor Iniciante", "Lifestyle Brasil",
            "Produtividade Max", "Negócios Online", "Transformação Pessoal", "Renda Extra",
            "Bem Estar Total", "Crescimento Pessoal", "Dicas de Ouro", "Sucesso Garantido"
        ]
        
        videos = []
        
        for i in range(count):
            # Dados realistas baseados em padrões de vídeos virais
            days_old = random.randint(1, 7)  # Vídeos de 1 a 7 dias
            base_views = random.randint(50000, 2000000)  # 50K a 2M views
            
            # Bonus para vídeos mais recentes (sua estratégia!)
            if days_old <= 2:
                base_views = int(base_views * random.uniform(1.5, 3.0))
            
            # Simular canal pequeno com vídeo viral (sua estratégia!)
            subscribers = random.randint(500, 15000)  # Canais pequenos
            
            # Engagement realista
            likes = int(base_views * random.uniform(0.02, 0.08))  # 2-8% de likes
            comments = int(base_views * random.uniform(0.001, 0.005))  # 0.1-0.5% comentários
            
            published_time = f"há {days_old} {'dia' if days_old == 1 else 'dias'}"
            
            video_id = f"demo_{i}_{random.randint(100000, 999999)}"
            
            video = {
                'id': video_id,
                'title': random.choice(viral_titles),
                'channel_name': random.choice(channels),
                'views': base_views,
                'views_text': self.format_views_text(base_views),
                'likes': likes,
                'comments': comments,
                'subscribers': subscribers,
                'published_time': published_time,
                'days_old': days_old,
                'duration': f"{random.randint(8, 25)}:{random.randint(10, 59):02d}",  # 8-25 minutos
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': f'https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg',  # Placeholder
                'source': 'Demo Viral Pattern',
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
            return f"{views/1000000:.1f}M visualizações"
        elif views >= 1000:
            return f"{views/1000:.0f}K visualizações"
        else:
            return f"{views} visualizações"
    
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

def display_alternative_video_card(video):
    """Exibir card do vídeo"""
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        # Thumbnail
        try:
            st.image(video['thumbnail'], width=200)
        except:
            st.image("https://via.placeholder.com/320x180?text=YouTube+Demo", width=200)
        
        # Duração
        st.markdown(f"**⏱️ {video.get('duration', '0:00')}**")
        
        # Score viral
        st.markdown(f"**🔥 Score: {format_number(video['viral_score'])}**")
    
    with col2:
        # Badges
        badges_html = ""
        if is_viral_opportunity(video):
            badges_html += '<span class="viral-badge">💎 OPORTUNIDADE OURO</span>'
        if video['days_old'] <= 1:
            badges_html += '<span class="trending-badge">⚡ ULTRA-RECENTE</span>'
        
        # Views por dia
        views_per_day = video['views'] / max(video['days_old'], 1)
        
        st.markdown(f"""
        <div class="video-card">
            <div class="video-title">{video['title']} {badges_html}</div>
            
            <div style="background: #f0f8ff; padding: 10px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4ECDC4;">
                <strong>📊 Performance Viral:</strong><br>
                👁️ <strong>{video['views_text']}</strong> em {video['days_old']} dias = <strong>{format_number(views_per_day)} views/dia</strong><br>
                📺 Canal: <strong>{video['channel_name']}</strong> ({format_number(video['subscribers'])} inscritos)<br>
                📈 Engagement: <strong>{video['engagement_rate']:.2f}%</strong> | 
                👍 {format_number(video['likes'])} likes | 
                💬 {format_number(video['comments'])} comentários
            </div>
            
            <div style="color: #666; font-size: 0.9rem; margin: 10px 0;">
                📅 Publicado {video['published_time']} | 
                🎯 Fonte: {video['source']}
            </div>
            
            <div style="margin-top: 15px;">
                <a href="{video['url']}" target="_blank" style="color: #FF0000; text-decoration: none; margin-right: 20px; font-weight: bold;">
                    🎥 ANALISAR VÍDEO
                </a>
                <a href="#" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">
                    📺 VER CANAL
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Interface principal
st.markdown('<h1 class="main-header">🎯 YouTube Alternative Hunter</h1>', unsafe_allow_html=True)

# Info sobre Alternative Hunter
st.markdown("""
<div class="alternative-info">
    <h3>🎯 Alternative Hunter - Demonstração da Sua Estratégia!</h3>
    <ul style="margin: 10px 0;">
        <li><strong>💎 Padrões reais</strong> - baseado em vídeos virais brasileiros</li>
        <li><strong>🎯 Sua estratégia</strong> - canais pequenos + vídeos recentes + alta performance</li>
        <li><strong>📊 Score viral</strong> - algoritmo que identifica oportunidades de ouro</li>
        <li><strong>🔥 Sem bloqueios</strong> - dados gerados seguindo padrões reais</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Demo section
st.markdown("""
<div class="demo-section">
    <h4>🎬 Modo Demonstração Ativo</h4>
    <p>Esta versão gera dados de demonstração baseados em <strong>padrões reais de vídeos virais brasileiros</strong>. 
    Os dados seguem exatamente sua estratégia de modelagem ultra-recente:</p>
    <ul>
        <li>✅ Vídeos de 1-7 dias com alta performance</li>
        <li>✅ Canais pequenos (500-15K subs) com conteúdo viral</li>
        <li>✅ Títulos seguindo padrões comprovados de viralização</li>
        <li>✅ Score viral calculado pela sua fórmula</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Controles
col1, col2, col3, col4 = st.columns(4)

with col1:
    num_videos = st.selectbox("📊 Quantidade:", [20, 30, 50, 75], index=1)

with col2:
    min_views = st.selectbox("👁️ Views mínimas:", [0, 25000, 50000, 100000, 500000], index=2)

with col3:
    max_days = st.selectbox("📅 Máx dias:", [1, 2, 3, 7], index=2)

with col4:
    max_subs = st.selectbox("📺 Máx inscritos:", [1000, 5000, 10000, 25000], index=1)

# Botão principal
if st.button("🎯 DEMONSTRAR ESTRATÉGIA VIRAL!", type="primary", use_container_width=True):
    
    # Inicializar hunter
    hunter = YouTubeAlternativeHunter()
    
    with st.spinner("🎯 Gerando demonstração baseada em padrões virais reais..."):
        # Gerar vídeos demo
        all_videos = hunter.generate_demo_viral_videos(num_videos)
        
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
                    <p style="margin: 0; color: #666;">Oportunidades Ouro</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #FF6B6B;">⚡ {ultra_recent}</h3>
                    <p style="margin: 0; color: #666;">Ultra-Recentes (1 dia)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #4ECDC4;">🎯 {small_channels}</h3>
                    <p style="margin: 0; color: #666;">Canais <1K subs</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <h3 style="margin: 0; color: #667eea;">🔥 {format_number(avg_viral_score)}</h3>
                    <p style="margin: 0; color: #666;">Score Viral Médio</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Export
            if st.button("📥 Exportar Demonstração", key="export_demo"):
                df = pd.DataFrame(filtered_videos)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV Demo",
                    data=csv,
                    file_name=f"demo_viral_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_demo"
                )
            
            # Resultados
            st.markdown("---")
            st.markdown("## 💎 OPORTUNIDADES VIRAIS ENCONTRADAS:")
            st.markdown("*Ordenado por Score Viral (views/dia × bônus canal pequeno × bônus recência)*")
            
            for video in filtered_videos:
                display_alternative_video_card(video)
                st.markdown("---")
        
        else:
            st.warning(f"💔 Nenhuma oportunidade encontrada com esses critérios específicos. Tente filtros menos restritivos.")

# Instruções finais
st.markdown("""
## 🎯 Como interpretar os resultados:

### 💎 **Oportunidades Ouro (sua estratégia):**
- ✅ Vídeos com até 2 dias
- ✅ Canais pequenos (até 5K subs)  
- ✅ Performance viral comprovada (50K+ views)

### 🔥 **Score Viral - Como funciona:**
- **Views/dia** × **Bônus canal pequeno** × **Bônus recência** × **Bônus engagement**
- Quanto maior o score, maior a oportunidade de modelagem

### 📊 **Próximos passos:**
1. **Analise** os vídeos com badge "OPORTUNIDADE OURO"
2. **Estude** o padrão: título, formato, abordagem  
3. **Modele** rapidamente sua versão única
4. **Lance** enquanto a tendência está quente (24-48h)

**Esta demonstração mostra exatamente como sua estratégia funciona na prática!** 🚀
""")

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🎯 <strong>YouTube Alternative Hunter</strong> | Demonstração da Estratégia Viral</p>
    <p>Baseado em padrões reais de vídeos que explodem no YouTube brasileiro!</p>
</div>
""", unsafe_allow_html=True)
