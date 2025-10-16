// Simple lightbox (no dependencies)
(function () {
  const overlay = document.getElementById("lightbox-overlay");
  const imgEl = document.getElementById("lightbox-img");
  const captionEl = document.getElementById("lightbox-caption");
  const closeBtn = document.getElementById("lightbox-close");

  function openLightbox(src, alt) {
    if (!overlay || !imgEl) return;
    imgEl.src = src;
    imgEl.alt = alt || "";
    if (captionEl) captionEl.textContent = alt || "";
    overlay.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    if (!overlay || !imgEl) return;
    overlay.hidden = true;
    imgEl.src = "";
    imgEl.alt = "";
    if (captionEl) captionEl.textContent = "";
    document.body.style.overflow = "";
  }

  // open when clicking any <a data-lightbox>
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-lightbox]");
    if (!a) return;
    e.preventDefault();
    openLightbox(a.href, a.getAttribute("data-alt") || a.title || a.querySelector("img")?.alt || "");
  });

  // close on overlay click (anywhere EXCEPT the image)
  overlay?.addEventListener("click", (e) => {
    // if the click originated on the image itself, do nothing
    if (e.target === imgEl) return;
    closeLightbox();
  });

  // close button
  closeBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    closeLightbox();
  });

  // close on ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !overlay?.hidden) closeLightbox();
  });

    // Fade-in images when they enter the viewport
  const reveal = (el) => el.classList.add("is-visible");

  const imgs = document.querySelectorAll("img.fade-in");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { reveal(e.target); io.unobserve(e.target); } });
    }, { rootMargin: "80px 0px" });
    imgs.forEach(img => io.observe(img));
  } else {
    // Fallback: reveal on load
    imgs.forEach(img => img.addEventListener("load", () => reveal(img)));
  }

})();

