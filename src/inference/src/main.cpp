#include <iostream>
#include <iomanip>
#include "simulator.hpp"
#include "leader_acceleration_predictor.hpp"
#include "safety_monitor.hpp"
#include "statistics_collector.hpp"

int main() {
    // Inizializzazione
    Simulator simulator{};
    simulator.reset();
    
    Leader_acceleration_predictor predictor{};
    StatisticsCollector stats{};

    std::cout << "Avvio Simulazione ADAS con Run-Time Assurance (RTA)\n";
    std::cout << "--------------------------------------------------------------------------------------\n";
    std::cout << std::left 
              << std::setw(8)  << "Tempo"
              << std::setw(12) << "Distanza"
              << std::setw(12) << "Dist.Crit"
              << std::setw(12) << "Vel. Ego"
              << std::setw(12) << "Vel. Lead"
              << std::setw(12) << "Accel"
              << std::setw(12) << "Attore RTA" 
              << "\n";
    std::cout << "--------------------------------------------------------------------------------------\n";

    // Ciclo Principale
    while (!simulator.is_terminated() && !simulator.is_truncated()) {
        // Lettura sensori
        double ego_velocity = simulator.get_ego_velocity();
        double relative_velocity = simulator.get_relative_velocity();
        double leader_velocity = ego_velocity + relative_velocity;
        double critical_distance = safety_monitor::cirtical_distance(leader_velocity, ego_velocity);
        double actual_distance = simulator.get_distance();

        // Controllo RTA: Decide se deve agire il Safety Monitor o l'AI
        bool rta_active = (actual_distance <= critical_distance);
        double action = 0.0;
        std::string controller_name = "";

        if (rta_active) {
            action = safety_monitor::safe_acceleration();
            controller_name = "MONITOR";
        } else {
            // Downcast esplicito per evitare warning con -Wconversion
            action = static_cast<double>(predictor.predict(
                static_cast<float>(ego_velocity), 
                static_cast<float>(actual_distance), 
                static_cast<float>(relative_velocity)
            ));
            controller_name = "AI MODEL";
        }

        // Avanzamento fisica
        simulator.step(action);

        // Registrazione statistiche
        stats.record_step(simulator.get_time(), actual_distance, critical_distance, ego_velocity, leader_velocity, action, rta_active);

        // Log del tick a schermo
        std::cout << std::left << std::fixed << std::setprecision(2)
                  << std::setw(8)  << simulator.get_time()
                  << std::setw(12) << actual_distance
                  << std::setw(12) << critical_distance
                  << std::setw(12) << ego_velocity
                  << std::setw(12) << leader_velocity
                  << std::setw(12) << action
                  << std::setw(12) << controller_name
                  << "\n";
    }

    std::cout << "--------------------------------------------------------------------------------------\n";
    
    // Verdetto finale
    if (simulator.get_distance() <= 0.0) {
        std::cout << "RISULTATO: COLLISIONE RILEVATA! (Distanza <= 0)\n";
    } else if (simulator.get_distance() >= 50.0) {
        std::cout << "RISULTATO: CARRO ATTREZZI NECESSARIO (Veicolo leader perso, d >= 50m)\n";
    } else {
        std::cout << "RISULTATO: SIMULAZIONE COMPLETATA CON SUCCESSO! (Nessuna collisione)\n";
    }

    // Stampa del report delle statistiche
    stats.print_summary();
    
    // Generazione del report PDF
    stats.generate_pdf_report();

    return 0;
}
