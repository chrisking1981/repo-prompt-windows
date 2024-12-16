# Repo Prompt Tool: Laravel Framework Versie - Projectbeschrijving en Gedetailleerde Werking

## **Overzicht van het Doel**
De **Repo Prompt Tool** is ontworpen om Laravel-projecten te analyseren, bestanden te selecteren, irrelevante bestanden uit te filteren, en vervolgens een duidelijke **filetree** en **geformatteerde prompt** (bijv. XML of JSON) te genereren. Deze prompt wordt gebruikt om een **Large Language Model (LLM)**, zoals GPT-4, specifieke wijzigingen of toevoegingen te laten maken aan de Laravel-codebase.

Het project richt zich specifiek op **Laravel-bestanden** en houdt rekening met de structuur, configuratiebestanden, routes, modellen en andere standaard Laravel-componenten.

---

## **Workflow: Prompt Generatie voor Laravel Projecten**

### **1. Bestandsstructuur en Filtering**
De tool detecteert en visualiseert de **standaard Laravel-bestandsstructuur**. De gebruiker kan bestanden **selecteren** of **uitsluiten** met behulp van filters.

**Standaard Laravel-mappen**:
- `app/`  
- `config/`  
- `database/`  
- `routes/`  
- `resources/`  
- `tests/`  

**Bestandsfiltering**:
- De tool gebruikt een filterfunctie gebaseerd op **.gitignore-syntaxis** om irrelevante bestanden uit te sluiten, zoals:
  - `node_modules/`
  - `vendor/`
  - `storage/`
  - `bootstrap/cache/`
  - `.env`
  - **Log- en cachebestanden** (`*.log`, `*.cache`).

**Voorbeeld Filterlijst**:
```plaintext
# Laravel onnodige bestanden
node_modules/
vendor/
storage/
bootstrap/cache/
*.log
.env
```

---

### **2. Selecteren van Relevante Laravel Bestanden**
- In het **linkerpaneel** (File Tree) ziet de gebruiker de volledige Laravel-bestandsstructuur.
- De gebruiker vinkt bestanden aan die **relevant** zijn voor de opdracht, zoals:
  - Controllers (`app/Http/Controllers/`)
  - Modellen (`app/Models/`)
  - Routes (`routes/web.php`, `routes/api.php`)
  - Blade-templates (`resources/views/`)
  - Configuratiebestanden (`config/`).
- Geselecteerde bestanden worden in het **rechterpaneel** weergegeven, inclusief:
  - **Bestandsnaam**
  - **Tokenbijdrage** (bijv. `0.18k tokens`).
  - **Percentage** van het totale aantal tokens.

**Voorbeeld Geselecteerde Bestanden**:
```
app/
├── Http/
│   └── Controllers/
│       └── TaskController.php
├── Models/
│   └── Task.php
routes/
├── web.php
resources/
└── views/
    └── tasks/
        └── index.blade.php
```

---

### **3. Tokenberekening en Optimalisatie**
- De tool berekent het aantal tokens per geselecteerd bestand.
- Het totale aantal tokens wordt onderaan weergegeven (bijv. **48.5k Tokens**).
- Dit helpt om binnen de **AI-tokenlimieten** te blijven.

---

### **4. Prompt Generatie**
De tool genereert een prompt met twee secties: **Samenvatting** en **XML**.
De exacte prompt voor het OpenAI GPT O1 Pro model staat in: OpenAI-GPT-O1-Pro-XML-Prompt.md

**Samenvattingssectie**:
- Een kort overzicht van de wijzigingen.
- 1-zins samenvattingen per gewijzigd bestand.

**XML-sectie**:
- Volgt een vast formaat met:
   - **File Summary**: Een korte beschrijving van de wijziging.
   - **File Operation**: CREATE, UPDATE of DELETE.
   - **File Path**: Het pad naar het bestand.
   - **File Code**: De volledige inhoud van het bestand.

**Voorbeeld XML-Structuur**:
```xml
<code_changes>
  <changed_files>
    <file>
      <file_summary>Updated TaskController to add sub-task functionality</file_summary>
      <file_operation>UPDATE</file_operation>
      <file_path>app/Http/Controllers/TaskController.php</file_path>
      <file_code><![CDATA[
      __FULL FILE CODE HERE__
      ]]></file_code>
    </file>
    <file>
      <file_summary>Added Task model relationships for sub-tasks</file_summary>
      <file_operation>UPDATE</file_operation>
      <file_path>app/Models/Task.php</file_path>
      <file_code><![CDATA[
      __FULL FILE CODE HERE__
      ]]></file_code>
    </file>
    <file>
      <file_summary>Modified routes to include sub-task routes</file_summary>
      <file_operation>UPDATE</file_operation>
      <file_path>routes/web.php</file_path>
      <file_code><![CDATA[
      __FULL FILE CODE HERE__
      ]]></file_code>
    </file>
  </changed_files>
</code_changes>
```

---

## **Workflow Samenvatting**
1. **Bestandsfiltering**:
   - De gebruiker filtert onnodige bestanden zoals `node_modules/` en `storage/`.
2. **Bestandsselectie**:
   - Gebruikers selecteren relevante Laravel-bestanden.
3. **Tokenberekening**:
   - De tool berekent tokens per bestand en het totaal.
4. **Promptgeneratie**:
   - De tool genereert een XML-prompt met samenvatting en volledige bestandscodes.
5. **Exporteren**:
   - De prompt kan worden gekopieerd en geplakt in een AI-tool zoals GPT-4.

---

## **Belangrijkste Functionaliteiten**
1. **Laravel-bestandsstructuur**: Volledige ondersteuning voor standaard Laravel-mappen en -bestanden.  
2. **Filterfunctie**: Negeert irrelevante bestanden en mappen.  
3. **Promptgeneratie**: Gestructureerde XML-output met samenvattingen en volledige code.  
4. **Tokenbeheer**: Houdt rekening met AI-tokenlimieten en optimaliseert de prompt.  
5. **Gebruiksvriendelijke interface**: Bestanden selecteren en exporteren in een paar klikken.  

---

## **Voordelen**
- **Laravel-specifiek**: Gebouwd voor Laravel-projecten met ondersteuning voor controllers, modellen, routes en views.
- **Efficiëntie**: Snelle selectie, filtering en promptgeneratie.
- **Gebruiksvriendelijk**: Intuïtieve interface en automatische tokenberekening.
- **Flexibel**: Ondersteunt zowel kleine als grote projecten.

---

Dit document biedt een complete beschrijving van de **Repo Prompt Tool** voor het **Laravel Framework**. Het legt uit hoe de tool werkt, welke bestanden belangrijk zijn en hoe de gegenereerde prompt eruitziet. Gebruik dit als **context** voor een LLM om de tool na te bouwen.
