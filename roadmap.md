# Tabella di Marcia per l'Implementazione ADAS RTA

Segui questa lista ordinata di passi per completare l'implementazione del sistema di Runtime Assurance (RTA) per l'ADAS in C++.

---

## 📋 Checklist dei Passaggi

### [ ] Passo 1: Correggere le configurazioni globali
* **File da modificare**: [global_parameters.hpp](file:///Users/edoardosarri/Documents/AI-Safety-Critical-runtime-monitoring/src/inference/include/global_parameters.hpp)
* **Cosa fare**:
  - Aggiungi `#include <string_view>` in cima al file (subito dopo `#include <cstddef>`).
  - Questo risolverà l'errore del compilatore che non riconosce `std::string_view` per la costante `MODEL_PATH`.

---

### [ ] Passo 2: Correggere la firma di `predict` nel predittore
* **File da modificare**: [leader_acceleration_predictor.hpp](file:///Users/edoardosarri/Documents/AI-Safety-Critical-runtime-monitoring/src/inference/include/leader_acceleration_predictor.hpp)
* **Cosa fare**:
  - Alla riga 16, rimuovi il modificatore `const` finale dalla dichiarazione del metodo `predict`.
  - La riga dovrà apparire così: `float predict(float ego_velocity, float distance, float relative_velocity);`.
  - Questo risolverà il conflitto di const-correctness con il file `.cpp` e con le API interne di ONNX Runtime.

---

### [ ] Passo 3: Rimuovere `constexpr` e correggere la formula del Safety Monitor
* **File 1**: [safety_monitor.hpp](file:///Users/edoardosarri/Documents/AI-Safety-Critical-runtime-monitoring/src/inference/include/safety_monitor.hpp)
  - Rimuovi `constexpr` alla riga 9: la dichiarazione di `safe_acceleration()` deve diventare `double safe_acceleration();`.
  - Rinomina la funzione alla riga 10 da `cirtical_distance` a `critical_distance` (correggendo il refuso).
* **File 2**: [safety_monitor.cpp](file:///Users/edoardosarri/Documents/AI-Safety-Critical-runtime-monitoring/src/inference/src/safety_monitor.cpp)
  - Rimuovi `constexpr` alla riga 5: la definizione deve iniziare con `double safety_monitor::safe_acceleration()`.
  - Rinomina il metodo alla riga 9 da `cirtical_distance` a `critical_distance`.
  - Modifica la formula alla riga 14 per usare il valore assoluto della decelerazione: dividi per `(2 * std::abs(physic_parameters::MIN_ACCELLERATION))` invece di `(2 * physic_parameters::MIN_ACCELLERATION)`.

---

### [ ] Passo 4: Implementare la funzione principale in `main.cpp`
* **File da modificare**: [main.cpp](file:///Users/edoardosarri/Documents/AI-Safety-Critical-runtime-monitoring/src/inference/src/main.cpp)
* **Cosa fare**:
  1. Includi le librerie necessarie (`<iostream>`, `<vector>`, `<cmath>`, `<iomanip>`).
  2. Includi gli header di progetto: `"simulator.hpp"`, `"leader_acceleration_predictor.hpp"`, `"safety_monitor.hpp"`.
  3. All'interno del `main`:
     - Istanzia l'oggetto `Simulator` sullo stack e chiama `reset()`.
     - Istanzia l'oggetto `Leader_acceleration_predictor` sullo stack (caricherà in automatico il modello ONNX).
     - Imposta le variabili di simulazione (`current_time = 0.0`, `dt = 0.1`).
     - Scrivi il ciclo `while (!sim.is_terminated() && !sim.is_truncated())`.
     - Dentro il ciclo:
       * Leggi $v_E$, $d$, $v_{\text{rel}}$ dal simulatore.
       * Calcola $v_L = v_E + v_{\text{rel}}$.
       * Calcola la distanza critica: `safety_monitor::critical_distance(v_L, v_E)`.
       * Se `d <= d_critical`: imposta l'azione a `safety_monitor::safe_acceleration()` (RTA attivo).
       * Altrimenti: interroga il modello con `predictor.predict(...)` (AI attiva).
       * Avanza la fisica con `sim.step(azione)`.
       * Stampa a schermo i valori del tick corrente per tracciare la simulazione.
     - Fuori dal ciclo:
       * Controlla come è finita la simulazione (collisione se $d \le 0$, persa se $d \ge 50$, o successo) e mostra il verdetto.

---

### [ ] Passo 5: Test e validazione
* **Cosa fare**:
  - Esegui lo script dal terminale nella root del progetto:
    ```bash
    ./exec/inference.sh
    ```
  - Controlla i log generati: verifica se l'intervento di recupero (`safe_acceleration` a $-8.0\,\text{m/s}^2$) si attiva correttamente quando la distanza scende sotto la soglia di sicurezza, evitando la collisione.
