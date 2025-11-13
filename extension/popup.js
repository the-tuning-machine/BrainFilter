/**
 * Script pour le popup de configuration
 */

// Paramètres par défaut
const DEFAULT_SETTINGS = {
  enabled: true,
  allowedHourStart: 20,
  allowedHourEnd: 21,
  filteredCategories: ['jeux', 'divertissement', 'shorts']
};

// Charger les paramètres au démarrage
document.addEventListener('DOMContentLoaded', loadSettings);

// Sauvegarder quand on clique sur le bouton
document.getElementById('save').addEventListener('click', saveSettings);

/**
 * Charge les paramètres depuis le storage
 */
function loadSettings() {
  chrome.storage.sync.get(DEFAULT_SETTINGS, (settings) => {
    // Activer/désactiver
    document.getElementById('enabled').checked = settings.enabled;

    // Heures
    document.getElementById('hourStart').value = settings.allowedHourStart;
    document.getElementById('hourEnd').value = settings.allowedHourEnd;

    // Catégories
    document.querySelectorAll('.category').forEach(checkbox => {
      checkbox.checked = settings.filteredCategories.includes(checkbox.value);
    });

    // Afficher le statut
    updateStatus(settings.enabled);
  });
}

/**
 * Sauvegarde les paramètres
 */
function saveSettings() {
  const enabled = document.getElementById('enabled').checked;
  const hourStart = parseInt(document.getElementById('hourStart').value) || 20;
  const hourEnd = parseInt(document.getElementById('hourEnd').value) || 21;

  const filteredCategories = Array.from(document.querySelectorAll('.category:checked'))
    .map(checkbox => checkbox.value);

  const settings = {
    enabled,
    allowedHourStart: hourStart,
    allowedHourEnd: hourEnd,
    filteredCategories
  };

  chrome.storage.sync.set(settings, () => {
    // Afficher un message de confirmation
    showMessage('Paramètres sauvegardés !', true);
    updateStatus(enabled);

    // Recharger l'onglet YouTube actif pour appliquer les changements
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (tab && tab.url && tab.url.includes('youtube.com')) {
        chrome.tabs.reload(tab.id);
      }
    });
  });
}

/**
 * Affiche un message temporaire
 */
function showMessage(message, success = true) {
  const statusDiv = document.getElementById('status');
  statusDiv.textContent = message;
  statusDiv.className = 'status ' + (success ? 'enabled' : 'disabled');
  statusDiv.style.display = 'block';

  setTimeout(() => {
    statusDiv.style.display = 'none';
  }, 2000);
}

/**
 * Met à jour le statut affiché
 */
function updateStatus(enabled) {
  const statusDiv = document.getElementById('status');

  if (enabled) {
    const now = new Date();
    const currentHour = now.getHours();
    const hourStart = parseInt(document.getElementById('hourStart').value) || 20;
    const hourEnd = parseInt(document.getElementById('hourEnd').value) || 21;

    if (currentHour >= hourStart && currentHour < hourEnd) {
      statusDiv.textContent = '✅ Filtrage inactif (heure autorisée)';
      statusDiv.className = 'status enabled';
    } else {
      statusDiv.textContent = '🛡️ Filtrage actif';
      statusDiv.className = 'status enabled';
    }
  } else {
    statusDiv.textContent = '⏸️ Filtrage désactivé';
    statusDiv.className = 'status disabled';
  }

  statusDiv.style.display = 'block';
}

// Mettre à jour le statut quand on change l'activation
document.getElementById('enabled').addEventListener('change', (e) => {
  updateStatus(e.target.checked);
});
