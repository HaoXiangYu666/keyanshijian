const pages = [
  [
    { label: "馆藏查询", icon: "i-search" },
    { label: "借阅记录", icon: "i-record" },
    { label: "云舟专题", icon: "i-cloud" },
    { label: "图书", icon: "i-book" },
    { label: "期刊", icon: "i-journal" },
    { label: "讲座", icon: "i-lecture" },
    { label: "学术资源", icon: "i-academic" },
    { label: "照片打印1", icon: "i-print" }
  ],
  [
    { label: "新书推荐", icon: "i-spark" },
    { label: "热门榜单", icon: "i-heart" },
    { label: "浏览历史", icon: "i-history" },
    { label: "馆内导航", icon: "i-compass" },
    { label: "意见反馈", icon: "i-chat" },
    { label: "账号设置", icon: "i-gear" },
    { label: "我的收藏", icon: "i-book" },
    { label: "关于我们", icon: "i-info" }
  ]
];

const grid = document.getElementById("grid");
const dots = Array.from(document.querySelectorAll(".dot"));
const toast = document.getElementById("toast");
let currentPage = 0;
let toastTimer = null;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 1800);
}

function renderPage(index) {
  currentPage = index;
  grid.innerHTML = pages[index]
    .map(
      (item) => `
        <button class="card" type="button" data-label="${item.label}">
          <svg viewBox="0 0 24 24" aria-hidden="true"><use href="#${item.icon}"></use></svg>
          <span>${item.label}</span>
        </button>
      `
    )
    .join("");

  dots.forEach((dot) => dot.classList.toggle("active", Number(dot.dataset.page) === index));

  grid.querySelectorAll(".card").forEach((card) => {
    card.addEventListener("click", () => showToast(`已选择：${card.dataset.label}`));
  });
}

dots.forEach((dot) => {
  dot.addEventListener("click", () => renderPage(Number(dot.dataset.page)));
});

document.querySelectorAll("[data-page-jump]").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    renderPage(Number(link.dataset.pageJump));
  });
});

document.getElementById("exploreBtn").addEventListener("click", () => {
  document.querySelector(".quick-entry").scrollIntoView({ behavior: "smooth", block: "start" });
});

renderPage(0);
