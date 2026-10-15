// Client stories page behavior (templates/portfolio/project_list.html).
//
// Two Alpine components:
//   storyHero(total)        the auto-advancing hero carousel of stories
//   screenshotViewer(urls)  one story's screenshot carousel + full-screen zoom
//
// This file must be loaded WITHOUT `defer`, at the end of <body>: Alpine's CDN
// build starts in a microtask after its own (deferred) script runs, so the
// `alpine:init` listener below has to be registered before that happens.

document.addEventListener('alpine:init', function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // Hero carousel
  // ---------------------------------------------------------------------------
  Alpine.data('storyHero', function (total) {
    return {
      current: 0,
      total: total,
      timer: null,
      paused: false,
      autoplay: false,
      interval: 7000,

      init: function () {
        var reducedMotion = window.matchMedia &&
          window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        // Nothing to advance to with one story; don't animate for people who
        // asked their OS for reduced motion.
        this.autoplay = total > 1 && !reducedMotion;
        this.start();
      },

      start: function () {
        this.stop();
        if (this.autoplay) {
          var self = this;
          this.timer = setInterval(function () { self.step(1); }, this.interval);
        }
      },
      stop: function () {
        clearInterval(this.timer);
        this.timer = null;
      },

      // Hover/focus pauses autoplay (so the reader can finish the sentence).
      pause: function () { this.paused = true; this.stop(); },
      resume: function () { this.paused = false; this.start(); },

      step: function (delta) {
        this.current = (this.current + delta + this.total) % this.total;
      },
      // Manual navigation restarts the countdown, unless the pointer/focus is
      // still on the carousel, in which case resume() will restart it later.
      go: function (n) {
        this.current = n;
        if (!this.paused) { this.start(); }
      },
      prev: function () { this.go((this.current - 1 + this.total) % this.total); },
      next: function () { this.go((this.current + 1) % this.total); },
    };
  });

  // ---------------------------------------------------------------------------
  // Screenshot carousel + zoom
  // ---------------------------------------------------------------------------
  Alpine.data('screenshotViewer', function (urls) {
    return {
      urls: urls,
      current: 0,
      zoomed: false,
      touchX: null,

      get total() { return this.urls.length; },

      prev: function () { this.current = (this.current - 1 + this.total) % this.total; },
      next: function () { this.current = (this.current + 1) % this.total; },
      go: function (n) { this.current = n; },

      open: function () {
        this.zoomed = true;
        // Stop the page scrolling behind the overlay.
        document.documentElement.style.overflow = 'hidden';
        var self = this;
        this.$nextTick(function () {
          if (self.$refs.close) { self.$refs.close.focus(); }
        });
      },
      close: function () {
        this.zoomed = false;
        document.documentElement.style.overflow = '';
        // Hand focus back to the thing that opened the zoom.
        if (this.$refs.trigger) { this.$refs.trigger.focus(); }
      },

      // Keep Tab inside the open dialog (close / prev / next).
      trapTab: function (event) {
        var focusable = Array.prototype.slice.call(
          event.currentTarget.querySelectorAll('button:not([disabled])')
        );
        if (!focusable.length) { return; }
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      },

      // Horizontal swipe changes slide (touch devices).
      touchStart: function (event) { this.touchX = event.changedTouches[0].clientX; },
      touchEnd: function (event) {
        if (this.touchX === null) { return; }
        var dx = event.changedTouches[0].clientX - this.touchX;
        this.touchX = null;
        if (Math.abs(dx) > 40) {
          if (dx < 0) { this.next(); } else { this.prev(); }
        }
      },
    };
  });
});
