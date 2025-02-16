# Self-driving car in 2D environment, using NEAT genetic algorithm

Una simulazione 2D per allenare alla guida autonoma un auto che deve percorrere una serie di percorsi di difficoltà crescente. Sfrutta delle reti neurali che evolvono grazie all'algoritmo genetico NEAT. Piccolo progetto divertente creato per il corso universitario di Machine Learning :)

![](https://github.com/andreadelorenzis/AI-Autonomous-Car/blob/main/imgs/video.gif)

### Modalità
1. **Simulazione:** scelta di un range di valori per alcuni parametri significativi dell algoritmo, e simulazione per un numero
prestabilito di generazioni. La simulazione viene svolta per ogni variazione nei parametri dell'algoritmo. Al termine vengono 
generati dei grafici, per visualizzare quale variazione porta ai migliori risultati. La simulazione può essere eseguita su più
percorsi uno dopo l'altro (curriculum based learning).
2. **Allenamento:** modalità per allenare il modello su un certo numero di parametri per un numero illimitato di generazioni, con 
possibilità di salvare il modello migliore in ogni momento.
3. **Validazione:** modalità per validare un modello allenato precedentemente salvato, su un certo numero di percorsi.

Sono stati usati 6 percorsi, che possono essere selezionati o deselezionati tramite l'opzione di menu "Percorsi".
