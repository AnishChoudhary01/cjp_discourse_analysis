/* CJP Discourse — Landing Page Interactions */

document.querySelectorAll("[data-scroll]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const track = document.getElementById(btn.dataset.scroll);
    if (!track) return;
    const dir = Number(btn.dataset.dir || 1);
    track.scrollBy({ left: dir * 320, behavior: "smooth" });
  });
});

// Hide broken image icons gracefully if local photos are absent
document.querySelectorAll("img").forEach((img) => {
  img.addEventListener("error", () => {
    img.style.display = "none";
  });
});

// Mobile menu toggle
const menuBtn = document.querySelector(".menu");
const navLinks = document.getElementById("nav-links");
if (menuBtn && navLinks) {
  menuBtn.addEventListener("click", () => {
    const open = navLinks.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", String(open));
  });
}

// Search dialog
const dialog = document.getElementById("search");
const openSearch = document.getElementById("open-search");
const searchInput = document.getElementById("search-input");
const searchHits = document.getElementById("search-hits");
const sections = [...document.querySelectorAll("[data-search]")];

if (openSearch && dialog) {
  openSearch.addEventListener("click", () => {
    dialog.showModal();
    searchInput.focus();
  });

  dialog.addEventListener("click", (e) => {
    if (e.target === dialog) dialog.close();
  });

  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim().toLowerCase();
    searchHits.innerHTML = "";
    if (!q) return;
    sections
      .filter((s) => s.textContent.toLowerCase().includes(q))
      .forEach((s) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = `#${s.id}`;
        a.textContent = s.dataset.search;
        a.addEventListener("click", () => dialog.close());
        li.appendChild(a);
        searchHits.appendChild(li);
      });
  });
}
