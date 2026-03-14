/*!
 * FileInput Italian Translation
 *
 * Author: Lorenzo Milesi <maxxer@yetopen.it>, Albano Battistella <albanobattistella@gmail.com>
 *
 * This file must be loaded after 'fileinput.js'. Patterns in braces '{}', or
 * any HTML markup tags in the messages must not be converted or translated.
 *
 * @see http://github.com/kartik-v/bootstrap-fileinput
 *
 * NOTE: this file must be saved in UTF-8 encoding.
 */
(function (factory) {
  "use strict";
  if (typeof define === "function" && define.amd) {
    define(["jquery"], factory);
  } else if (typeof module === "object" && typeof module.exports === "object") {
    factory(require("jquery"));
  } else {
    factory(window.jQuery);
  }
})(function ($) {
  "use strict";

  $.fn.fileinputLocales["it"] = {
    sizeUnits: ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"],
    bitRateUnits: [
      "B/s",
      "KB/s",
      "MB/s",
      "GB/s",
      "TB/s",
      "PB/s",
      "EB/s",
      "ZB/s",
      "YB/s",
    ],
    fileSingle: "file",
    filePlural: "file",
    browseLabel: "Sfoglia &hellip;",
    removeLabel: "Rimuovi",
    removeTitle: "Rimuovi i file selezionati",
    cancelLabel: "Annulla",
    cancelTitle: "Annulla i caricamenti in corso",
    pauseLabel: "Pausa",
    pauseTitle: "Metti in pausa il caricamento in corso",
    uploadLabel: "Carica",
    uploadTitle: "Carica i file selezionati",
    msgNo: "No",
    msgNoFilesSelected: "Nessun file selezionato",
    msgPaused: "Paused",
    msgCancelled: "Annullato",
    msgPlaceholder: "Seleziona {files} ...",
    msgZoomModalHeading: "Anteprima dettagliata",
    msgFileRequired: "Devi selezionare un file da caricare.",
    msgSizeTooSmall:
      'Il file "{name}" (<b>{size}</b>) è troppo piccolo, deve essere almeno di <b>{minSize}</b>.',
    msgSizeTooLarge:
      'Il file "{name}" (<b>{size}</b>) eccede la dimensione massima di caricamento di <b>{maxSize}</b>.',
    msgMultipleSizeTooLarge:
      'Il file "{name}" (<b>{size}</b>) eccede la dimensione massima di caricamento di <b>{maxSize}</b>.',
    msgFilesTooLess: "Devi selezionare almeno <b>{n}</b> {files} da caricare.",
    msgFilesTooMany:
      "Il numero di file selezionati per il caricamento <b>({n})</b> eccede il numero massimo di file accettati <b>{m}</b>.",
    msgTotalFilesTooMany:
      "Puoi caricare un massimo di <b>{m}</b> file (<b>{n}</b> file rilevati).",
    msgFileNotFound: 'File "{name}" non trovato!',
    msgFileSecured:
      'Restrizioni di sicurezza impediscono la lettura del file "{name}".',
    msgFileNotReadable: 'Il file "{name}" non è leggibile.',
    msgFilePreviewAborted: 'Generazione anteprima per "{name}" annullata.',
    msgFilePreviewError: 'Errore durante la lettura del file "{name}".',
    msgInvalidFileName:
      'Carattere non valido o non supportato nel file "{name}".',
    msgInvalidFileType:
      'Tipo non valido per il file "{name}". Sono ammessi solo file di tipo "{types}".',
    msgInvalidFileExtension:
      'Estensione non valida per il file "{name}". Sono ammessi solo file con estensione "{extensions}".',
    msgFileTypes: {
      image: "immagine",
      html: "HTML",
      text: "testo",
      video: "video",
      audio: "audio",
      flash: "flash",
      pdf: "PDF",
      object: "oggetto",
    },
    msgUploadAborted: "Il caricamento del file è stato interrotto",
    msgUploadThreshold: "In lavorazione &hellip;",
    msgUploadBegin: "Inizializzazione &hellip;",
    msgUploadEnd: "Fatto",
    msgUploadResume: "Ripresa del caricamento &hellip;",
    msgUploadEmpty: "Dati non disponibili",
    msgUploadError: "Errore di caricamento",
    msgDeleteError: "Elimina errore",
    msgProgressError: "Errore",
    msgValidationError: "Errore di convalida",
    msgLoading: "Caricamento file {index} di {files} &hellip;",
    msgProgress:
      "Caricamento file {index} di {files} - {name} - {percent}% completato.",
    msgSelected: "{n} {files} selezionati",
    msgProcessing: "Processing ...",
    msgFoldersNotAllowed: "Trascina solo file! Ignorata/e {n} cartella/e.",
    msgImageWidthSmall:
      'La larghezza dell\'immagine "{name}" deve essere di almeno <b>{size} px</b> (detected <b>{dimension} px</b>).',
    msgImageHeightSmall:
      "L'altezza dell'immagine \"{name}\" deve essere di almeno <b>{size} px</b> (detected <b>{dimension} px</b>).",
    msgImageWidthLarge:
      'La larghezza dell\'immagine "{name}" non può superare <b>{size} px</b> (detected <b>{dimension} px</b>).',
    msgImageHeightLarge:
      "L'altezza dell'immagine \"{name}\" non può superare <b>{size} px</b> (detected <b>{dimension} px</b>).",
    msgImageResizeError:
      "Impossibile ottenere le dimensioni dell'immagine per ridimensionare.",
    msgImageResizeException:
      "Errore durante il ridimensionamento dell'immagine.<pre>{errors}</pre>",
    msgAjaxError:
      "Qualcosa non ha funzionato con l'operazione {operation}. Per favore riprova più tardi!",
    msgAjaxProgressError: "{operation} non riuscita",
    msgDuplicateFile:
      'Il file "{name}" della stessa dimensione "{size} KB" è già stato selezionato in precedenza. Ignora la selezione duplicata.',
    msgResumableUploadRetriesExceeded:
      "Caricamento interrotto dopo <b>{max}</b> tentativi per il file <b>{file}</b>! Dettagli errore: <pre>{error}</pre>",
    msgPendingTime: "{time} rimanente",
    msgCalculatingTime: "calcolo del tempo rimanente",
    ajaxOperations: {
      deleteThumb: "eliminazione file",
      uploadThumb: "caricamento file",
      uploadBatch: "caricamento file in batch",
      uploadExtra: "caricamento dati del form",
    },
    dropZoneTitle: "Trascina i file qui &hellip;",
    dropZoneClickTitle: "<br>(o clicca per selezionare {files})",
    fileActionSettings: {
      removeTitle: "Rimuovere il file",
      uploadTitle: "Caricare un file",
      uploadRetryTitle: "Riprova il caricamento",
      downloadTitle: "Scarica file",
      rotateTitle: "Rotate 90 deg. clockwise",
      zoomTitle: "Guarda i dettagli",
      dragTitle: "Muovi / Riordina",
      indicatorNewTitle: "Non ancora caricato",
      indicatorSuccessTitle: "Caricati",
      indicatorErrorTitle: "Carica Errore",
      indicatorPausedTitle: "Caricamento in pausa",
      indicatorLoadingTitle: "Caricamento &hellip;",
    },
    previewZoomButtonTitles: {
      prev: "Vedi il file precedente",
      next: "Vedi il file seguente",
      rotate: "Rotate 90 deg. clockwise",
      toggleheader: "Attiva header",
      fullscreen: "Attiva schermo intero",
      borderless: "Abilita modalità senza bordi",
      close: "Chiudi",
    },
  };
});
