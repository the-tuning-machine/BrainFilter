/**
 * Script pour le popup de configuration
 */

// Paramètres par défaut
const DEFAULT_SETTINGS = {
  enabled: true,
  allowedHourStart: 20,
  allowedHourEnd: 21,
  filteredCategories: ['jeux', 'divertissement', 'shorts'],
  blockedChannels: [] // Nouvelle propriété
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

    // Chaînes bloquées
    renderBlockedChannels(settings.blockedChannels);

    // Afficher le statut
    updateStatus(settings.enabled);
  });
}

// Ajouter un écouteur d'événement pour le bouton "Ajouter"
document.getElementById('addChannel').addEventListener('click', addBlockedChannel);

/**
 * Ajoute une chaîne à la liste des chaînes bloquées
 */
function addBlockedChannel() {
  const channelNameInput = document.getElementById('channelNameInput');
  const channelName = channelNameInput.value.trim();

  if (channelName) {
    chrome.storage.sync.get(DEFAULT_SETTINGS, (settings) => {
      let blockedChannels = settings.blockedChannels;
      // Convertir en minuscule et vérifier l'unicité
      const lowerCaseChannelName = channelName.toLowerCase();
      if (!blockedChannels.map(c => c.toLowerCase()).includes(lowerCaseChannelName)) {
        blockedChannels.push(channelName);
        chrome.storage.sync.set({ blockedChannels }, () => {
          channelNameInput.value = ''; // Vider le champ
          renderBlockedChannels(blockedChannels);
          showMessage('Chaîne ajoutée !', true);
          // Recharger l'onglet YouTube actif pour appliquer les changements
          reloadYouTubeTab();
        });
      } else {
        showMessage('Cette chaîne est déjà dans la liste.', false);
      }
    });
  }
}

/**
 * Supprime une chaîne de la liste des chaînes bloquées
 */
function removeBlockedChannel(channelToRemove) {
  chrome.storage.sync.get(DEFAULT_SETTINGS, (settings) => {
    let blockedChannels = settings.blockedChannels.filter(channel => channel !== channelToRemove);
    chrome.storage.sync.set({ blockedChannels }, () => {
      renderBlockedChannels(blockedChannels);
      showMessage('Chaîne supprimée.', true);
      // Recharger l'onglet YouTube actif pour appliquer les changements
      reloadYouTubeTab();
    });
  });
}

/**
 * Rend la liste des chaînes bloquées dans l'interface utilisateur
 */
function renderBlockedChannels(blockedChannels) {
  const blockedChannelsList = document.getElementById('blockedChannelsList');
  blockedChannelsList.innerHTML = ''; // Nettoyer la liste existante

  if (blockedChannels.length === 0) {
    blockedChannelsList.innerHTML = '<p class="info">Aucune chaîne bloquée pour l\'instant.</p>';
    return;
  }

  blockedChannels.forEach(channel => {
    const channelItem = document.createElement('div');
    channelItem.className = 'category-item'; // Réutiliser la classe pour le style
    channelItem.style.display = 'flex';
    channelItem.style.justifyContent = 'space-between';
    channelItem.style.alignItems = 'center';
    channelItem.style.marginBottom = '4px';

    const channelNameSpan = document.createElement('span');
    channelNameSpan.textContent = channel;
    channelItem.appendChild(channelNameSpan);

    const removeButton = document.createElement('button');
    removeButton.textContent = 'X';
    removeButton.style.background = 'none';
    removeButton.style.border = '1px solid #c5221f';
    removeButton.style.color = '#c5221f';
    removeButton.style.borderRadius = '50%';
    removeButton.style.width = '24px';
    removeButton.style.height = '24px';
    removeButton.style.fontSize = '12px';
    removeButton.style.fontWeight = 'bold';
    removeButton.style.cursor = 'pointer';
    removeButton.style.flexShrink = '0';
    removeButton.style.marginLeft = '8px';
    removeButton.addEventListener('click', () => removeBlockedChannel(channel));
    channelItem.appendChild(removeButton);

    blockedChannelsList.appendChild(channelItem);
  });
}

/**
 * Sauvegarde les paramètres
 */
function saveSettings() {
  const enabled = document.getElementById('enabled').checked;
  const hourStart = parseInt(document.getElementById('hourStart').value) || DEFAULT_SETTINGS.allowedHourStart;
  const hourEnd = parseInt(document.getElementById('hourEnd').value) || DEFAULT_SETTINGS.allowedHourEnd;

  const filteredCategories = Array.from(document.querySelectorAll('.category:checked'))
    .map(checkbox => checkbox.value);

  // Récupérer les chaînes bloquées existantes
  chrome.storage.sync.get(DEFAULT_SETTINGS, (currentSettings) => {
    const blockedChannels = currentSettings.blockedChannels; // Utilisez les chaînes déjà stockées

    const settings = {
      enabled,
      allowedHourStart: hourStart,
      allowedHourEnd: hourEnd,
      filteredCategories,
      blockedChannels // Inclure les chaînes bloquées dans la sauvegarde
    };

    chrome.storage.sync.set(settings, () => {
      // Afficher un message de confirmation
      showMessage('Paramètres sauvegardés !', true);
      updateStatus(enabled);
      // Recharger l'onglet YouTube actif pour appliquer les changements
      reloadYouTubeTab();
    });
  });
}

/**
 * Recharge l'onglet YouTube actif
 */
function reloadYouTubeTab() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs[0];
    if (tab && tab.url && tab.url.includes('youtube.com')) {
      chrome.tabs.reload(tab.id);
    }
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
