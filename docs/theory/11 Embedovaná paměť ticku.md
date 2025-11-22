# Embedovaná paměť ticku

## 1. Definice
Embedovaná paměť ticku je vrstva informací přenesená z minulých uzávěrů (PoF) do aktuálního ticku.  
Nejde o reaktivovatelný stav, ale o **datový otisk minulosti**, který je součástí současného ticku a může být pozorován agenty.

---

## 2. Struktura ticku
Každý tick \(n\) obsahuje:
- **Aktuální stav:** \(x(t_n)\)
- **Akumulátor práce:** \(\Theta(t_n)\)
- **Modulátor komplexity:** \(F(x(t_n))\)
- **Embedovaná paměť:** \(\text{Log}_n\)

\[
\text{Tick}_n = \{x(t_n), \Theta(t_n), F(x(t_n)), \text{Log}_n\}
\]

---

## 3. Obsah embedované paměti
\[
\text{Log}_n = \{(t_{n-k}, \text{artefakty}_{n-k}) \mid k \geq 1\}
\]

- **Artefakty:** signály, fotony, gravitační vlny, struktury.  
- Jsou součástí současného ticku, i když jejich původ je v minulosti.  
- Pozorování minulosti = interakce s artefakty embedovanými v aktuálním ticku.

---

## 4. Mechanismus přenosu
1. **Commit (PoF):** uzávěr ticku zapisuje stav do logu.  
2. **Artefaktová propagace:** část stavu se embeduje do následujících ticků jako signál.  
3. **Aktuální tick:** obsahuje vlastní stav + artefakty z minulých ticků.  
4. **Agentické pozorování:** agent čte artefakty → interpretuje je jako „minulost“.

---

## 5. Auditní pravidla
- Historie není reaktivovatelná, pouze čitelná.  
- Každý artefakt nese časovou značku (TickID původu).  
- Embedovaná paměť je neměnná.  
- Pozorování minulosti = čtení embedovaných artefaktů, nikoli přístup k minulému ticku.

---

## 6. Diagram (textová vizualizace)
    ┌───────────────────────────────┐
    │           Tick n              │
    │   Aktuální stav x(t_n)        │
    │   Θ(t_n), F(x(t_n))           │
    │                               │
    │   ┌───────────────────────┐   │
    │   │ Embedovaná paměť Log_n│   │
    │   │  Artefakty z Tick n-1 │   │
    │   │  Artefakty z Tick n-2 │   │
    │   │  ...                  │   │
    │   └───────────────────────┘   │
    └───────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │          Agent A_k            │
    │  Čte artefakty z Log_n        │
    │  → interpretuje jako minulost │
    └───────────────────────────────┘


---

## 7. Shrnutí
- Root tick je jediný aktivní stav.  
- Historie je embedovaná v logu, ne reaktivovatelná.  
- Artefakty z minulých ticků jsou součástí současného ticku.  
- Pozorování minulosti = čtení embedované paměti.