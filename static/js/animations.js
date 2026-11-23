function attachButtonRipples() {
    document.addEventListener("click", (e) => {
        const target = e.target.closest(".btn, .nav-link-btn");
        if (!target || target.disabled) return;

        const rect = target.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const ripple = document.createElement("span");
        ripple.className = "btn-ripple-circle";
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${e.clientY - rect.top - size / 2}px`;

        target.appendChild(ripple);
        setTimeout(() => ripple.remove(), 620);
    });
}

function attachSmoothNavigation() {
    window.addEventListener("pageshow", (e) => {
        if (e.persisted) {
            document.body.classList.remove("page-leaving");
        }
    });

    document.addEventListener("click", (e) => {
        const link = e.target.closest("a[href]");
        if (!link) return;

        const href = link.getAttribute("href");
        if (!href || !href.startsWith("/static/")) return;
        if (e.ctrlKey || e.metaKey || e.shiftKey || link.target === "_blank") return;
        if (window.location.pathname + window.location.search === href) return;

        e.preventDefault();
        document.body.classList.add("page-leaving");
        setTimeout(() => {
            window.location.href = href;
        }, 210);
    });
}

function attachCardSpotlights() {
    document.addEventListener("mousemove", (e) => {
        const card = e.target.closest(".stat-card");
        if (!card) return;
        const rect = card.getBoundingClientRect();
        card.style.setProperty("--mouse-x", `${e.clientX - rect.left}px`);
        card.style.setProperty("--mouse-y", `${e.clientY - rect.top}px`);
    });
}

function animateNumberElement(el) {
    const rawText = el.textContent.trim();
    if (!rawText || el.dataset.lastTarget === rawText) return;

    const match = rawText.match(/^(-?\d+(?:\.\d+)?)(.*)$/);
    if (!match) return;

    const endValue = parseFloat(match[1]);
    const suffix = match[2] || "";
    const isFloat = match[1].includes(".");

    el.dataset.lastTarget = rawText;

    if (endValue === 0) return;

    const duration = 750;
    const startTime = performance.now();

    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 4);
        const current = endValue * eased;

        el.textContent = (isFloat ? current.toFixed(1) : Math.round(current)) + suffix;

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            el.textContent = rawText;
        }
    }

    requestAnimationFrame(step);
}

function initCounterObservers() {
    const ids = [
        "totalSubjects",
        "totalTasks",
        "completionRate",
        "todoTasks",
        "inProgressTasks",
        "doneTasks",
        "totalSubjectsHero"
    ];

    ids.forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;

        animateNumberElement(el);

        const observer = new MutationObserver(() => animateNumberElement(el));
        observer.observe(el, { childList: true, characterData: true, subtree: true });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    attachButtonRipples();
    attachSmoothNavigation();
    attachCardSpotlights();
    initCounterObservers();
});