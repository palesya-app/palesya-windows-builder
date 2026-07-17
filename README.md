# Palesya Desktop Builder

Repository pubblico e isolato usato esclusivamente per compilare e collaudare i
pacchetti Windows e Linux di Palesya sui runner standard gratuiti di GitHub.

- non contiene il sorgente Palesya;
- non contiene database o dati delle palestre;
- usa una deploy key in sola lettura per prelevare un tag dal repository privato;
- non conserva la chiave ufficiale degli aggiornamenti;
- produce artifact temporanei con SHA-256 e commit sorgente verificabile;
- firma e promozione Cloudflare avvengono nel repository privato `palesya-app/palesya`.

I workflow sono avviabili soltanto manualmente indicando un tag di release.

