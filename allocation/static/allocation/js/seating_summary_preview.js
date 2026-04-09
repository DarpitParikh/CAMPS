(function () {
  function triggerPrint() {
    window.focus();
    setTimeout(function () {
      window.print();
    }, 20);
  }

  function bindPrintButton() {
    var printButton = document.getElementById('printSummaryBtn');
    if (!printButton) {
      return;
    }

    printButton.addEventListener('click', function (event) {
      event.preventDefault();
      triggerPrint();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindPrintButton);
  } else {
    bindPrintButton();
  }
})();
