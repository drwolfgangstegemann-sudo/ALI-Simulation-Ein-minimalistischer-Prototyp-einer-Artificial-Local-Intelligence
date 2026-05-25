# ALI-Simulation – Artificial Local Intelligence mit kausalem Kern

**Diskussionspapier als Code** – Ein minimalistischer Prototyp einer kontrollierbaren, lokalen Intelligenz, die auf Selbsterhalt (kausaler Kern) und eingebauten Normen (Über-Ich) basiert.

## Konzept

Dieses Projekt setzt die in unserem Papier *"Vom Mythos der AGI zur Architektur einer kontrollierbaren ALI"* beschriebene Architektur um. Eine **ALI** (Artificial Local Intelligence) ist keine allmächtige AGI, sondern eine zweckgebundene, lokal agierende Intelligenz mit drei Instanzen:

- **Es (kausaler Kern)** – dynamischer Selbsterhalt, Energiehaushalt, Assimilation/Ausscheidung.
- **Ich** – Entscheidungsfindung, Exploration, Pfadplanung.
- **Über-Ich** – statische Normen (z. B. „keine Giftpakete“), Kontrolle der Selbstabschaltung.

Die ALI erhält sich selbst nur so lange, wie sie ihre Aufgabe erfüllen kann. Sinkt ihre Energie unter eine Schwelle, schaltet sie sich kontrolliert ab – dies ist ein Ausdruck der eingebauten Zweckrationalität.

## Ausführung

### Lokal (Python 3.7+)

1. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
