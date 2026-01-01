// Configuration de l'API
const API_URL = 'http://localhost:8000';

// Éléments DOM
const textInput = document.getElementById('text-input');
const analyzeBtn = document.getElementById('analyze-btn');
const btnText = document.getElementById('btn-text');
const btnLoader = document.getElementById('btn-loader');
const resultSection = document.getElementById('result-section');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');

// Fonction principale d'analyse
async function analyzeText() {
    const text = textInput.value.trim();
    
    // Validation
    if (!text) {
        showError('Veuillez entrer un texte à analyser.');
        return;
    }
    
    // Masquer les sections précédentes
    hideResults();
    hideError();
    
    // Afficher le loader avec message informatif
    setLoading(true);
    
    // Message informatif pendant le chargement
    const loadingMessage = document.createElement('div');
    loadingMessage.id = 'loading-message';
    loadingMessage.style.cssText = 'text-align: center; color: #666; margin-top: 10px; font-style: italic;';
    loadingMessage.textContent = 'Analyse en cours... Cela peut prendre quelques secondes.';
    analyzeBtn.parentElement.appendChild(loadingMessage);
    
    try {
        // Appel à l'API avec timeout de 60 secondes
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 secondes timeout
        
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erreur lors de l\'analyse');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Erreur:', error);
        if (error.name === 'AbortError') {
            showError('Le délai d\'attente a été dépassé. L\'analyse prend plus de temps que prévu. Veuillez réessayer.');
        } else {
            showError(error.message || 'Une erreur est survenue lors de l\'analyse. Vérifiez que le serveur est démarré.');
        }
    } finally {
        setLoading(false);
        // Supprimer le message de chargement
        const loadingMsg = document.getElementById('loading-message');
        if (loadingMsg) {
            loadingMsg.remove();
        }
    }
}

// Afficher les résultats
function displayResults(data) {
    // Afficher la section de résultats
    resultSection.style.display = 'block';
    
    // Verdict
    const verdictText = document.getElementById('verdict-text');
    const verdictBadge = document.getElementById('verdict-badge');
    verdictText.textContent = data.verdict;
    
    // Déterminer la classe CSS selon le verdict
    let badgeClass = '';
    if (data.verdict.includes('vraie')) {
        badgeClass = 'true';
    } else if (data.verdict.includes('douteuse')) {
        badgeClass = 'doubtful';
    } else {
        badgeClass = 'false';
    }
    
    verdictBadge.className = `verdict-badge ${badgeClass}`;
    verdictBadge.textContent = data.verdict;
    
    // Score
    const scoreValue = document.getElementById('score-value');
    const scoreFill = document.getElementById('score-fill');
    const score = data.score;
    
    scoreValue.textContent = (score * 100).toFixed(2) + '%';
    scoreFill.style.width = (score * 100) + '%';
    
    // Déterminer la classe CSS selon le score
    let scoreClass = '';
    if (score > 0.85) {
        scoreClass = 'high';
    } else if (score >= 0.65) {
        scoreClass = 'medium';
    } else {
        scoreClass = 'low';
    }
    
    scoreFill.className = `score-fill ${scoreClass}`;
    
    // Article le plus proche
    const closestArticle = document.getElementById('closest-article');
    closestArticle.textContent = data.closest_article || 'Aucun article trouvé';
    
    // URL source
    const sourceUrl = document.getElementById('source-url');
    if (data.source_url) {
        sourceUrl.href = data.source_url;
        sourceUrl.style.display = 'inline-block';
    } else {
        sourceUrl.style.display = 'none';
    }
    
    // Langue détectée
    const detectedLanguage = document.getElementById('detected-language');
    const langNames = {
        'fr': 'Français',
        'en': 'Anglais'
    };
    detectedLanguage.textContent = langNames[data.language] || data.language;
}

// Afficher une erreur
function showError(message) {
    errorSection.style.display = 'block';
    errorMessage.textContent = message;
}

// Masquer les résultats
function hideResults() {
    resultSection.style.display = 'none';
}

// Masquer les erreurs
function hideError() {
    errorSection.style.display = 'none';
}

// Gérer l'état de chargement
function setLoading(loading) {
    if (loading) {
        analyzeBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
    } else {
        analyzeBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Permettre l'analyse avec la touche Entrée (Ctrl+Enter ou Cmd+Enter)
textInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        analyzeText();
    }
});

// Focus automatique sur le textarea au chargement
window.addEventListener('load', () => {
    textInput.focus();
});

