(function () {
  const qrModal = document.getElementById("qrModal");
  const sellModal = document.getElementById("sellModal");

  function lockScroll(lock) {
    document.body.style.overflow = lock ? "hidden" : "";
  }

  if (qrModal) {
    const titleEl = document.getElementById("qrModalTitle");
    const codeEl = document.getElementById("qrModalCode");
    const imgEl = document.getElementById("qrModalImg");
    const loaderEl = document.getElementById("qrModalLoader");
    const urlEl = document.getElementById("qrModalUrl");
    const downloadEl = document.getElementById("qrModalDownload");
    const pngEl = document.getElementById("qrModalPng");

    function showLoader(show) {
      if (loaderEl) loaderEl.hidden = !show;
      if (imgEl) imgEl.hidden = show;
    }

    function openQrModal(btn) {
      titleEl.textContent = btn.dataset.name || "Plaquinha";
      codeEl.textContent = btn.dataset.code || "";
      urlEl.textContent = btn.dataset.public || "";
      downloadEl.href = btn.dataset.download || "#";
      if (pngEl) pngEl.href = btn.dataset.png || "#";
      showLoader(true);
      imgEl.onload = () => showLoader(false);
      imgEl.onerror = () => {
        if (loaderEl) loaderEl.textContent = "Falha ao carregar preview. Tente Baixar PDF/PNG.";
      };
      imgEl.alt = "Plaquinha " + (btn.dataset.code || "");
      imgEl.src = btn.dataset.img || "";
      qrModal.hidden = false;
      lockScroll(true);
    }

    function closeQrModal() {
      qrModal.hidden = true;
      imgEl.src = "";
      imgEl.onload = null;
      imgEl.onerror = null;
      showLoader(true);
      if (loaderEl) loaderEl.textContent = "Gerando preview...";
      if (!sellModal || sellModal.hidden) lockScroll(false);
    }

    document.querySelectorAll("[data-open-qr]").forEach((btn) => {
      btn.addEventListener("click", () => openQrModal(btn));
    });
    qrModal.querySelectorAll("[data-close-qr]").forEach((el) => {
      el.addEventListener("click", closeQrModal);
    });
  }

  if (sellModal) {
    const form = document.getElementById("sellForm");
    const titleEl = document.getElementById("sellModalTitle");
    const codeEl = document.getElementById("sellModalCode");
    const priceInput = document.getElementById("sellPriceInput");

    function openSellModal(btn) {
      titleEl.textContent = btn.dataset.name || "Marcar como vendida";
      codeEl.textContent = btn.dataset.code || "";
      form.action = btn.dataset.action || "";
      priceInput.value = "";
      sellModal.hidden = false;
      lockScroll(true);
      setTimeout(() => priceInput.focus(), 50);
    }

    function closeSellModal() {
      sellModal.hidden = true;
      if (!qrModal || qrModal.hidden) lockScroll(false);
    }

    document.querySelectorAll("[data-open-sell]").forEach((btn) => {
      btn.addEventListener("click", () => openSellModal(btn));
    });
    sellModal.querySelectorAll("[data-close-sell]").forEach((el) => {
      el.addEventListener("click", closeSellModal);
    });

    form.addEventListener("submit", (event) => {
      if (!priceInput.value.trim()) {
        event.preventDefault();
        priceInput.focus();
        return;
      }
      const ok = window.confirm(
        `Confirmar venda de ${codeEl.textContent} por R$ ${priceInput.value}?`
      );
      if (!ok) event.preventDefault();
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (sellModal && !sellModal.hidden) {
      sellModal.hidden = true;
      lockScroll(false);
    } else if (qrModal && !qrModal.hidden) {
      qrModal.hidden = true;
      lockScroll(false);
    }
  });
})();
