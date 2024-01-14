# AI-Autonomous-Car

### Modalità
1. **Simulazione:** scelta di un range di valori per alcuni parametri significativi dell algoritmo, e simulazione per un numero
prestabilito di generazioni. La simulazione viene svolta per ogni variazione nei parametri dell'algoritmo. Al termine vengono 
generati dei grafici, per visualizzare quale variazione porta ai migliori risultati. La simulazione può essere eseguita su più
percorsi uno dopo l'altro (curriculum based learning).
2. **Allenamento:** modalità per allenare il modello su un certo numero di parametri per un numero illimitato di generazioni, con 
possibilità di salvare il modello migliore in ogni momento.
3. **Validazione:** modalità per validare un modello allenato precedentemente salvato, su un certo numero di percorsi.

Sono stati usati 6 percorsi, che possono essere selezionati o deselezionati tramite l'opzione di menu "Percorsi".

### TODO:
+ **NEAT**: Trovare la configurazione che porta al migliore apprendimento su un singolo percorso: 
  1. plottare la fitness media e la best fitness in funzione delle
  generazioni su un singolo percorso, variando diversi parametri dell'algoritmo (es. tasso di mutazione dei 
  pesi, numero di macchine, ecc.)
  2. selezionare la configurazione che porta alla miglior best o average fitness
+ **Curriculum Based Learning**: Fornire all'auto più percorsi, di graduale difficoltà. Data la configurazione migliore 
di apprendimento, trovare il set di percorsi che porti l'auto a superare il percorso di validazione nel minor 
numero di generazioni possibile. L'obiettivo è rispondere alla seguente domanda: si posson raggiungere prestazioni 
migliori tramite questo approccio? O conviene partire subito dal percorso/esempio più difficile?
+ Aggiungere modo per fare un'installazione semplice delle dipendenze.
+ Refactoring
+ Portare i parametri di simulazione in un file esterno.

### Attenzione
Per poter eseguire il programma svolgere i seguenti passi:
1. Installare NEAT e aggiungere in "site-packages/neat/" la classe "visualize.py".
   Andare in "site-packages/neat/\_\_init.py\_\_" e aggiungere "import neat.visualize as visualize".
2. Se non già presente sul sistema, installare il programma open source "graphviz", e aggiungere
   il suo eseguibile alle variabilli d'ambiente. Se la procedura è andata a buon fine, scrivendo
   sulla riga di comando "dot -v", si dovrebbe vedere la sua versione.