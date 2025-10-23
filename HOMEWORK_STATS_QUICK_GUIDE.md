# ⚡ Guide Rapide - Statistiques des Devoirs

## 🎯 Nouveautés

L'API `/api/homework/` retourne maintenant **automatiquement** pour chaque devoir :

```json
{
  "id": 1,
  "name": "Devoir de Maths",
  
  // ⭐ NOUVELLES STATISTIQUES
  "average_score": 15.75,        // Moyenne générale
  "submitted_count": 25,          // Nombre de rendus
  "submission_rate": 83.33,       // Taux de soumission (%)
  "highest_score": 20,            // Meilleure note
  "lowest_score": 8,              // Note la plus basse
  "target_students_count": 30     // Étudiants ciblés
}
```

---

## 💻 Utilisation Frontend

### JavaScript Simple
```javascript
fetch('http://localhost:8000/api/homework/1/')
  .then(r => r.json())
  .then(hw => {
    console.log(`Moyenne: ${hw.average_score}/20`);
    console.log(`Rendus: ${hw.submitted_count}/${hw.target_students_count}`);
    console.log(`Taux: ${hw.submission_rate}%`);
  });
```

### React Component
```jsx
function HomeworkCard({ homework }) {
  return (
    <div>
      <h3>{homework.name}</h3>
      <p>Moyenne: {homework.average_score}/20</p>
      <p>Rendus: {homework.submitted_count}/{homework.target_students_count}</p>
      <p>Taux: {homework.submission_rate}%</p>
    </div>
  );
}
```

---

## ✅ Tests Effectués

### Devoir sans notes
```
average_score: null
submitted_count: 0
submission_rate: 0%
```

### Devoir avec notes
```
average_score: 154.38
submitted_count: 8
submission_rate: 266.67%
highest_score: 200
lowest_score: 17
```

---

## 📚 Documentation Complète

Voir `API_HOMEWORK_STATS_README.md` pour :
- Exemples React, Vue.js, Angular
- Graphiques avec Chart.js
- Cas d'usage avancés
- Détails techniques

---

**Prêt à utiliser !** 🚀  
**Plus besoin de calculer les statistiques côté frontend !** ✅

