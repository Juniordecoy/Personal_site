// Simple lightbox with grouping (no dependencies)
(function () {
  const overlay = document.getElementById("lightbox-overlay");
  const imgEl = document.getElementById("lightbox-img");
  const captionEl = document.getElementById("lightbox-caption");
  const closeBtn = document.getElementById("lightbox-close");
  const prevBtn = document.getElementById("lightbox-prev");
  const nextBtn = document.getElementById("lightbox-next");

  // state for groups
  let groupItems = [];      // [{href, alt}]
  let currentIndex = 0;     // index in groupItems

  function setButtonsVisibility() {
    const multi = groupItems.length > 1;
    if (prevBtn) prevBtn.style.display = multi ? "block" : "none";
    if (nextBtn) nextBtn.style.display = multi ? "block" : "none";
  }

  function showAt(index) {
    if (!groupItems.length) return;
    currentIndex = (index + groupItems.length) % groupItems.length;
    const { href, alt } = groupItems[currentIndex];
    if (imgEl) {
      imgEl.src = href;
      imgEl.alt = alt || "";
    }
    if (captionEl) captionEl.textContent = alt || "";
  }

  function buildGroupFromAnchor(a) {
    const group = a.getAttribute("data-group");
    if (!group) {
      // single image (no group)
      groupItems = [{ href: a.href, alt: a.getAttribute("data-alt") || a.title || a.querySelector("img")?.alt || "" }];
      currentIndex = 0;
      return;
    }
    const anchors = Array.from(document.querySelectorAll(`a[data-lightbox][data-group="${group}"]`));
    groupItems = anchors.map(el => ({
      href: el.href,
      alt: el.getAttribute("data-alt") || el.title || el.querySelector("img")?.alt || ""
    }));
    // find starting index
    const startHref = a.href;
    currentIndex = Math.max(0, groupItems.findIndex(i => i.href === startHref));
  }

  function openLightboxFromAnchor(a) {
    buildGroupFromAnchor(a);
    setButtonsVisibility();
    showAt(currentIndex);
    if (overlay) {
      overlay.hidden = false;
      document.body.style.overflow = "hidden";
    }
  }

  function closeLightbox() {
    if (!overlay) return;
    overlay.hidden = true;
    if (imgEl) { imgEl.src = ""; imgEl.alt = ""; }
    if (captionEl) captionEl.textContent = "";
    document.body.style.overflow = "";
    groupItems = [];
    currentIndex = 0;
  }

  // open when clicking any <a data-lightbox>
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[data-lightbox]");
    if (!a) return;
    e.preventDefault();
    openLightboxFromAnchor(a);
  });

  // close ONLY when clicking the dark background itself
  overlay?.addEventListener("click", (e) => {
    if (e.target === overlay) closeLightbox();
  });

  // controls
  closeBtn?.addEventListener("click", (e) => { e.preventDefault(); closeLightbox(); });
  prevBtn?.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); showAt(currentIndex - 1); });
  nextBtn?.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); showAt(currentIndex + 1); });

  // keyboard: ESC to close, ←/→ to navigate
  document.addEventListener("keydown", (e) => {
    if (overlay?.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft" && groupItems.length > 1) showAt(currentIndex - 1);
    if (e.key === "ArrowRight" && groupItems.length > 1) showAt(currentIndex + 1);
  });

  // Fade-in images when they enter the viewport (unchanged)
  const reveal = (el) => el.classList.add("is-visible");
  const imgs = document.querySelectorAll("img.fade-in");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { reveal(e.target); io.unobserve(e.target); } });
    }, { rootMargin: "80px 0px" });
    imgs.forEach(img => io.observe(img));
  } else {
    imgs.forEach(img => img.addEventListener("load", () => reveal(img)));
  }
})();
