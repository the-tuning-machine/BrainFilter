#!/bin/bash
# Serveur HTTP simple pour tester l'extension

echo "🚀 Démarrage du serveur de test..."
echo "📂 Dossier: $(pwd)"
echo ""
echo "Ouvrez dans votre navigateur:"
echo "  👉 http://localhost:8000/test-classifier.html"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

python3 -m http.server 8000
