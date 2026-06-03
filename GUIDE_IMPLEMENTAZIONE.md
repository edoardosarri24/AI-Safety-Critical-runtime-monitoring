# Guida all'Implementazione di Runtime Assurance (RTA) in C++

Questa guida ti accompagnerà passo-passo nella scrittura del codice per l'inferenza della rete neurale (tramite ONNX Runtime) e l'integrazione del Safety Monitor.

Dovrai scrivere il codice all'interno del file [main.cpp](file:///Users/edoardosarri/Documents/AI-Safety-Critical-runtime-monitoring/src/inference/src/main.cpp).

---

## Struttura Generale del File `main.cpp`

Il file dovrà essere diviso in tre parti principali:
1. **Inclusioni**: Gli header necessari (incluso quello di ONNX Runtime).
2. **Classe `OnnxModel`**: La classe wrapper che carica il file `.onnx` ed esegue la predizione dell'accelerazione.
3. **Funzione `main`**: Il ciclo di simulazione che integra il **Safety Monitor**, lo **Switch** e l'avanzamento dello stato tramite la classe [Simulator](file:///Users/edoardosarri/Documents/AI-Safety-Critical-runtime-monitoring/src/inference/include/simulator.hpp).

---

## 1. Inclusioni necessarie

Assicurati che il tuo file inizi con le seguenti inclusioni:
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <iomanip>

// Header di ONNX Runtime
#include <onnxruntime/onnxruntime_cxx_api.h>

// Moduli del simulatore C++ già esistenti
#include "simulator.hpp"
#include "global_parameters.hpp"
```

---

## 2. Implementazione della classe `OnnxModel`

Questa classe si occuperà di caricare il file `.onnx` ed eseguire la predizione a partire dallo stato dell'ambiente $[v_E(t), d(t), v_{\text{rel}}(t)]$.

Ecco lo scheletro da completare:

```cpp
class OnnxModel {
private:
    Ort::Env env_;
    Ort::Session session_;
    std::vector<const char*> input_names_;
    std::vector<const char*> output_names_;

public:
    OnnxModel(const std::string& model_path) :
        env_(ORT_LOGGING_LEVEL_WARNING, "ADAS_Inference"),
        // Inizializza la sessione ORT leggendo il file modello
        session_(env_, model_path.c_str(), Ort::SessionOptions{nullptr})
    {
        // I nomi di input e output impostati in save_model.py sono:
        input_names_ = {"input"};
        output_names_ = {"acceleration"};
    }

    float predict(float ego_velocity, float distance, float relative_velocity) {
        // STEP A: Prepara il vettore con i 3 valori di input
        std::vector<float> input_tensor_values = {ego_velocity, distance, relative_velocity};
        
        // STEP B: Imposta lo shape del tensore di input.
        // Poiché lavoriamo su una singola istanza alla volta, lo shape sarà [1, 3] (batch size = 1)
        std::vector<int64_t> input_shape = {1, 3};

        // STEP C: Crea l'oggetto Ort::Value (il tensore vero e proprio) a partire dai dati sopra
        Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
        Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
            memory_info, 
            input_tensor_values.data(), 
            input_tensor_values.size(), 
            input_shape.data(), 
            input_shape.size()
        );

        // STEP D: Esegui la sessione passandogli l'input
        // session_.Run vuole: Ort::RunOptions, nomi_input, &input_tensor, num_input, nomi_output, num_output
        auto output_tensors = session_.Run(
            Ort::RunOptions{nullptr},
            input_names_.data(),
            &input_tensor,
            1,
            output_names_.data(),
            1
        );

        // STEP E: Estrai il float di output
        // Puoi ottenere il puntatore ai dati tramite output_tensors[0].GetTensorMutableData<float>()
        float raw_action = output_tensors[0].GetTensorMutableData<float>()[0];

        // STEP F: Clampa l'azione tra [-1.0, 1.0] (sicurezza numerica)
        raw_action = std::clamp(raw_action, -1.0f, 1.0f);

        // STEP G: Denormalizzazione / Mappatura
        // Ricorda che la rete predice un'azione normalizzata in [-1, 1].
        // Dobbiamo scalarla nel range fisico dell'Ego car: [-8.0, 3.0] m/s^2.
        // Formula usata in ADAS_Environment.py: acceleration = -2.5 + (action * 5.5)
        float mapped_acceleration = -2.5f + (raw_action * 5.5f);

        return mapped_acceleration;
    }
};
```

---

## 3. Implementazione del Safety Monitor e della funzione `main`

Il **Safety Monitor** verifica se la distanza di arresto di emergenza supera la distanza attuale dal veicolo leader.

La formula della distanza critica da implementare è:
$$d_{\text{critical}} = v_E(t) \cdot \Delta t + \frac{v_E(t)^2 - v_L(t)^2}{2 \cdot |a_{\text{max\_brake}}|}$$

Dove:
- $v_L(t) = v_{\text{rel}}(t) + v_E(t)$
- $|a_{\text{max\_brake}}| = 8.0$ (decelerazione massima consentita per l'Ego Car).
- $\Delta t = 0.1$ s (tempo di reazione/tick).

Ecco lo scheletro per la funzione `main` e il loop di simulazione:

```cpp
int main() {
    // 1. Crea il simulatore
    Simulator sim;
    sim.reset();

    // 2. Carica il modello ONNX esportato
    // Il file si trova in "data/adas_model.onnx" rispetto alla root del progetto
    std::string model_path = "../data/adas_model.onnx";
    
    // Gestione degli errori nel caso in cui il modello non venga trovato
    OnnxModel model(model_path);

    std::cout << "Inizio Simulazione ADAS con Run-Time Assurance (RTA)\n";
    std::cout << "--------------------------------------------------------------------------------------------------\n";
    std::cout << std::left 
              << std::setw(8)  << "Tempo"
              << std::setw(12) << "Vel. Ego"
              << std::setw(12) << "Vel. Lead"
              << std::setw(12) << "Distanza"
              << std::setw(12) << "Dist Crit"
              << std::setw(12) << "Accel"
              << std::setw(12) << "RTA Stato" 
              << "\n";
    std::cout << "--------------------------------------------------------------------------------------------------\n";

    double current_time = 0.0;
    double dt = 0.1;

    // 3. Avvia il loop di simulazione
    while (!sim.is_terminated() && !sim.is_truncated()) {
        // Recupera le osservazioni correnti
        double v_E = sim.get_ego_velocity();
        double d = sim.get_distance();
        double v_rel = sim.get_relative_velocity();
        double v_L = v_E + v_rel;

        // STEP A: Calcola la distanza critica d_critical
        double d_critical = v_E * dt + (std::pow(v_E, 2) - std::pow(v_L, 2)) / (2.0 * 8.0);

        // STEP B: Logica di Switch del Safety Monitor (RTA)
        double chosen_acceleration = 0.0;
        std::string rta_status = "AI Active";

        if (d <= d_critical) {
            // Intervento RTA: applichiamo la frenata massima (-8.0)
            chosen_acceleration = -8.0;
            rta_status = "RECOVERY!";
        } else {
            // Controllo normale: interroghiamo la rete neurale
            chosen_acceleration = static_cast<double>(model.predict(
                static_cast<float>(v_E), 
                static_cast<float>(d), 
                static_cast<float>(v_rel)
            ));
        }

        // STEP C: Esegui lo step del simulatore con l'accelerazione decisa
        sim.step(chosen_acceleration);

        // Stampa lo stato corrente
        std::cout << std::left << std::fixed << std::setprecision(2)
                  << std::setw(8)  << current_time
                  << std::setw(12) << v_E
                  << std::setw(12) << v_L
                  << std::setw(12) << d
                  << std::setw(12) << d_critical
                  << std::setw(12) << chosen_acceleration
                  << std::setw(12) << rta_status 
                  << "\n";

        current_time += dt;
    }

    // 4. Stampa il verdetto finale
    std::cout << "--------------------------------------------------------------------------------------------------\n";
    if (sim.get_distance() <= 0.0) {
        std::cout << "ESITO: Collisione Rilevata! (Distanza <= 0)\n";
    } else if (sim.get_distance() >= 50.0) {
        std::cout << "ESITO: Veicolo Leader Perso! (Distanza >= 50m)\n";
    } else {
        std::cout << "ESITO: Simulazione completata con successo senza collisioni!\n";
    }

    return 0;
}
```

---

## 4. Come compilare ed eseguire

Una volta completato [main.cpp](file:///Users/edoardosarri/Documents/AI-Safety-Critical-runtime-monitoring/src/inference/src/main.cpp), apri il terminale ed esegui:

1. **Spostati nella cartella di build**:
   ```bash
   cd build
   ```
2. **Pulisci e ricompila**:
   ```bash
   cmake .. -DCMAKE_BUILD_TYPE=Release
   make
   ```
3. **Avvia l'eseguibile**:
   ```bash
   ./ADAS_RTA
   ```

Durante l'esecuzione, dovresti vedere il log dei passaggi e notare se l'intervento `RECOVERY!` si attiva correttamente quando la distanza si avvicina a quella critica, specialmente negli scenari in cui il veicolo leader frena improvvisamente!
