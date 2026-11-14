const menuButton = document.querySelector(".menu-toggle");
const nav = document.querySelector(".nav-links");

if (menuButton && nav) {
  menuButton.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("open");
    menuButton.setAttribute("aria-expanded", String(isOpen));
  });
  nav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
    nav.classList.remove("open");
    menuButton.setAttribute("aria-expanded", "false");
  }));
}

// Expand project cards with mouse, keyboard, Enter or Space.
document.querySelectorAll(".project-card").forEach(card => {
  const toggle = () => {
    const next = card.getAttribute("aria-expanded") !== "true";
    card.setAttribute("aria-expanded", String(next));
  };
  card.addEventListener("click", toggle);
  card.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggle();
    }
  });
});

// Reveal sections as they enter the viewport.
const revealTargets = document.querySelectorAll(
  ".section-label, .about-grid, .section-intro, .skill-card, .project-card, .education-layout, .contact-grid"
);
revealTargets.forEach(element => element.classList.add("reveal"));
if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealTargets.forEach(element => observer.observe(element));
} else {
  revealTargets.forEach(element => element.classList.add("is-visible"));
}

// Active navigation indicator.
const sections = document.querySelectorAll("main section[id]");
if ("IntersectionObserver" in window) {
  const sectionObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        document.querySelectorAll(".nav-links a").forEach(link => {
          link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`);
        });
      }
    });
  }, { rootMargin: "-35% 0px -55% 0px" });
  sections.forEach(section => sectionObserver.observe(section));
}

// Submit contact form to the Python / Flask API.
const contactForm = document.querySelector("#contactForm");
if (contactForm) {
  const status = document.querySelector("#formStatus");
  const submitButton = contactForm.querySelector("button[type='submit']");
  const submitLabel = submitButton.querySelector(".submit-label");

  contactForm.addEventListener("submit", async event => {
    event.preventDefault();
    status.textContent = "";
    status.classList.remove("error");
    contactForm.querySelectorAll(".field-error").forEach(node => node.textContent = "");

    const formData = new FormData(contactForm);
    const payload = Object.fromEntries(formData.entries());
    submitButton.disabled = true;
    submitLabel.textContent = "Sending...";

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const result = await response.json();

      if (!response.ok) {
        if (result.errors) {
          Object.entries(result.errors).forEach(([field, message]) => {
            const errorNode = contactForm.querySelector(`[data-error="${field}"]`);
            if (errorNode) errorNode.textContent = message;
          });
        }
        throw new Error(result.message || "Please check the form and try again.");
      }

      status.textContent = result.message;
      contactForm.reset();
    } catch (error) {
      status.textContent = error.message || "Something went wrong. Please try again.";
      status.classList.add("error");
    } finally {
      submitButton.disabled = false;
      submitLabel.textContent = "Send message";
    }
  });
}
