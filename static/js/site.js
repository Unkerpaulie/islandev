// Site-wide client behavior.
// Kept dependency-free; small enough to read top-to-bottom.

(function () {
  'use strict';

  // Scroll-aware navbar: toggles a `is-scrolled` class once the user has
  // scrolled past 30px. Styling for that state lives in input.css.
  const nav = document.querySelector('[data-navbar]');
  if (nav) {
    const onScroll = function () {
      if (window.scrollY > 30) {
        nav.classList.add('is-scrolled');
      } else {
        nav.classList.remove('is-scrolled');
      }
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Mobile menu toggle.
  const toggle = document.querySelector('[data-mobile-toggle]');
  const panel = document.querySelector('[data-mobile-panel]');
  const iconOpen = document.querySelector('[data-icon-open]');
  const iconClose = document.querySelector('[data-icon-close]');

  if (toggle && panel) {
    const setOpen = function (open) {
      panel.classList.toggle('hidden', !open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (iconOpen && iconClose) {
        iconOpen.classList.toggle('hidden', open);
        iconClose.classList.toggle('hidden', !open);
      }
    };
    toggle.addEventListener('click', function () {
      const isOpen = !panel.classList.contains('hidden');
      setOpen(!isOpen);
    });
    // Close mobile panel when any link inside it is clicked.
    panel.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () { setOpen(false); });
    });
  }
  // Scroll-fade: elements with class `fade-in-up` start invisible and
  // translate slightly downward, then animate to full opacity + position when
  // they enter the viewport. Uses IntersectionObserver — no library needed.
  const fadeEls = document.querySelectorAll('.fade-in-up');
  if (fadeEls.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    fadeEls.forEach(function (el) { observer.observe(el); });
  } else {
    // Fallback: just show everything if IntersectionObserver isn't available.
    fadeEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

})();
