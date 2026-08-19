(function() {
  'use strict';

  // --------------------------------------------------
  // CONFIGURATION (UPDATE THESE WITH YOUR SUPABASE DETAILS)
  // --------------------------------------------------
  var SUPABASE_URL = 'https://wugufkfguhardjwcmrff.supabase.co';
  var SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1Z3Vma2ZndWhhcmRqd2NtcmZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM1Mjc4MDcsImV4cCI6MjA5OTEwMzgwN30.7Yy1d1HOIxRIGj4d_3BZW1wMLht8NvkgmXy7hGbMuQY';
  // --------------------------------------------------

  // Cookie helpers
  function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  }

  function setCookie(name, value, days) {
    var expires = "";
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
  }

  // UUID generator fallback
  function generateUUID() {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  // Canvas fingerprint generation
  function getCanvasHash() {
    try {
      var canvas = document.createElement('canvas');
      var ctx = canvas.getContext('2d');
      ctx.textBaseline = "top";
      ctx.font = "14px 'Arial'";
      ctx.textBaseline = "alphabetic";
      ctx.fillStyle = "#f60";
      ctx.fillRect(125, 1, 62, 20);
      ctx.fillStyle = "#069";
      ctx.fillText("KeriPickle", 2, 15);
      ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
      ctx.fillText("KeriPickle", 4, 17);
      return canvas.toDataURL();
    } catch (e) {
      return '';
    }
  }

  async function generateFingerprint() {
    var canvasData = getCanvasHash();
    var components = [
      window.screen.width + 'x' + window.screen.height,
      Intl.DateTimeFormat().resolvedOptions().timeZone,
      navigator.language,
      navigator.platform,
      canvasData
    ].join('||');

    try {
      var msgBuffer = new TextEncoder().encode(components);
      var hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
      var hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(function(b) { return b.toString(16).padStart(2, '0'); }).join('');
    } catch(e) {
      // Basic string hash fallback if crypto.subtle is not supported
      var hash = 0;
      for (var i = 0; i < components.length; i++) {
        var char = components.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }
      return 'fp_' + Math.abs(hash);
    }
  }

  // Device type detection
  function getDeviceType() {
    var ua = navigator.userAgent;
    if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
      return "Tablet";
    }
    if (/Mobile|iP(hone|od)|Android|BlackBerry|IEMobile|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
      return "Mobile";
    }
    return "Desktop";
  }

  // Referrer detection
  function getReferrer() {
    return document.referrer || 'Direct';
  }

  // UTM parameters extraction
  function getUTMParams() {
    var urlParams = new URLSearchParams(window.location.search);
    var utm = {};
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(function(param) {
      if (urlParams.has(param)) {
        utm[param] = urlParams.get(param);
      }
    });
    return Object.keys(utm).length ? utm : null;
  }

  // Global identifier variables
  var visitorId = null;
  var sessionId = null;
  var fingerprint = null;

  // Supabase REST client helper
  // For GET requests: returns JSON data (uses return=representation)
  // For POST/PATCH/PUT: Supabase returns 204 No Content when Prefer: return=minimal
  //   — we must NOT call .json() on an empty body or it throws SyntaxError
  //   and breaks the entire callback chain (setupSession never fires).
  function supabaseRequest(path, method, body, callback) {
    if (SUPABASE_URL.indexOf('your-supabase-url') > -1) {
      // Silent return if keys not set yet
      return;
    }

    var isRead = (method === 'GET');

    var headers = {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json',
      // For reads: request full JSON back so callbacks get data
      // For writes: use minimal to avoid 413 / large payloads, handle 204
      'Prefer': isRead ? 'return=representation' : 'return=minimal'
    };

    fetch(SUPABASE_URL + '/rest/v1/' + path, {
      method: method,
      headers: headers,
      body: body ? JSON.stringify(body) : null
    })
    .then(function(res) {
      if (!res.ok) {
        return res.text().then(function(txt) {
          throw new Error('Supabase error ' + res.status + ': ' + (txt || res.statusText));
        });
      }
      // 204 No Content = successful write with empty body — do NOT parse JSON
      if (res.status === 204 || res.status === 201) {
        if (callback) callback(null);
        return;
      }
      return res.json().then(function(data) {
        if (callback) callback(data);
      });
    })
    .catch(function(err) {
      console.warn('[VisitorID Tracker] Supabase Sync Failed:', err);
    });
  }

  // Main initialization
  async function initTracker() {
    fingerprint = await generateFingerprint();

    // 1. Resolve Visitor ID (Primary: Cookie/LocalStorage, Secondary: Fingerprint DB lookup fallback)
    visitorId = getCookie('cr_visitor_id');
    if (!visitorId) {
      visitorId = localStorage.getItem('cr_visitor_id');
    }

    if (visitorId) {
      // Re-sync cookie and localStorage
      setCookie('cr_visitor_id', visitorId, 365);
      localStorage.setItem('cr_visitor_id', visitorId);
      setupSession();
    } else {
      // Look up if this fingerprint has an associated visitor_id in Supabase
      supabaseRequest('visitor_sessions?device_fingerprint=eq.' + fingerprint + '&select=visitor_id&order=session_start.desc&limit=1', 'GET', null, function(data) {
        if (data && data.length > 0) {
          visitorId = data[0].visitor_id;
          console.log('[VisitorID Tracker] Restored visitor ID from fingerprint:', visitorId);
        } else {
          visitorId = generateUUID();
          console.log('[VisitorID Tracker] Created new visitor ID:', visitorId);
        }
        setCookie('cr_visitor_id', visitorId, 365);
        localStorage.setItem('cr_visitor_id', visitorId);
        setupSession();
      });
    }
  }

  // Setup active session
  function setupSession() {
    sessionId = sessionStorage.getItem('cr_session_id');
    var isNewSession = !sessionId;

    if (isNewSession) {
      sessionId = generateUUID();
      sessionStorage.setItem('cr_session_id', sessionId);
      
      // Initialize arrays in sessionStorage
      sessionStorage.setItem('cr_pages_viewed', JSON.stringify([]));
      sessionStorage.setItem('cr_products_viewed', JSON.stringify([]));
      sessionStorage.setItem('cr_cart_events', JSON.stringify([]));

      // Create new session row in Supabase
      var body = {
        visitor_id: visitorId,
        session_id: sessionId,
        device_type: getDeviceType(),
        referrer_source: getReferrer(),
        utm_params: getUTMParams(),
        device_fingerprint: fingerprint,
        session_start: new Date().toISOString()
      };
      
      supabaseRequest('visitor_sessions', 'POST', body, function() {
        trackPageView();
      });
    } else {
      trackPageView();
    }
  }

  // Log page view
  function trackPageView() {
    var currentUrl = window.location.href;
    var timestamp = new Date().toISOString();
    var context = window.ShopifyTemplateContext || {};

    // 1. Log General Page View
    var pages = [];
    try {
      pages = JSON.parse(sessionStorage.getItem('cr_pages_viewed')) || [];
    } catch(e) {}
    
    pages.push({ url: currentUrl, timestamp: timestamp });
    sessionStorage.setItem('cr_pages_viewed', JSON.stringify(pages));

    // 2. Log PDP Product View if applicable
    var products = [];
    if (context.page_type === 'product' && context.product) {
      try {
        products = JSON.parse(sessionStorage.getItem('cr_products_viewed')) || [];
      } catch(e) {}
      
      products.push({
        product_id: context.product.id,
        title: context.product.title,
        price: context.product.price,
        url: currentUrl,
        timestamp: timestamp
      });
      sessionStorage.setItem('cr_products_viewed', JSON.stringify(products));
    }

    // 3. Sync arrays to Supabase
    var body = {
      pages_viewed: pages
    };
    if (products.length > 0) {
      body.products_viewed = products;
    }
    
    supabaseRequest('visitor_sessions?session_id=eq.' + sessionId, 'PATCH', body);
  }

  // Log cart events (Add to Cart / Remove from Cart)
  function trackCartEvent(type, productDetails) {
    if (!sessionId) return;

    var events = [];
    try {
      events = JSON.parse(sessionStorage.getItem('cr_cart_events')) || [];
    } catch(e) {}

    events.push({
      type: type, // "add_to_cart" | "remove_from_cart"
      title: productDetails.title || '',
      variant_id: productDetails.variant_id || '',
      product_id: productDetails.product_id || '',
      quantity: productDetails.quantity || 1,
      price: productDetails.price || '',
      timestamp: new Date().toISOString()
    });

    sessionStorage.setItem('cr_cart_events', JSON.stringify(events));

    // Sync to Supabase
    var body = {
      cart_events: events
    };
    supabaseRequest('visitor_sessions?session_id=eq.' + sessionId, 'PATCH', body);
  }

  // Identity Resolution: link visitor_id to customer profiles
  function resolveIdentity(phone, email, name) {
    if (!visitorId) return;

    var cleanPhone = phone ? phone.replace(/\D/g, '') : '';
    if (cleanPhone.length > 10) cleanPhone = cleanPhone.slice(-10);
    if (!cleanPhone && !email) return;

    // 1. Save to visitor_identity_map (upsert: ignore duplicates)
    var identityBody = {
      visitor_id: visitorId,
      phone_number: cleanPhone || email, // Use email as fallback if phone is blank
      first_linked_at: new Date().toISOString()
    };

    // Use a direct fetch with upsert headers to avoid 409 on repeat visits
    var upsertHeaders = {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal,resolution=ignore-duplicates'
    };
    fetch(SUPABASE_URL + '/rest/v1/visitor_identity_map', {
      method: 'POST',
      headers: upsertHeaders,
      body: JSON.stringify(identityBody)
    }).catch(function(e) { console.warn('[VisitorTracker] identity map upsert failed:', e); });

    // 2. Also enrich the active session row in visitor_sessions with contact info
    var sessionBody = {};
    if (name) sessionBody.associated_name = name;
    if (cleanPhone) sessionBody.associated_phone = cleanPhone;
    if (email) sessionBody.associated_email = email;

    if (Object.keys(sessionBody).length > 0) {
      supabaseRequest('visitor_sessions?session_id=eq.' + sessionId, 'PATCH', sessionBody);
    }
  }

  // Expose tracking helpers globally
  window.VisitorTracker = {
    getVisitorId: function() { return visitorId; },
    getSessionId: function() { return sessionId; },
    getFingerprint: function() { return fingerprint; },
    trackCartEvent: trackCartEvent,
    resolveIdentity: resolveIdentity
  };

  // Run initialization after window fully loads (ensures all scripts including jQuery are ready)
  window.addEventListener('load', function() {
    initTracker().catch(function(err) {
      console.warn('[VisitorTracker] Init failed:', err);
    });
  });

  // Intercept cart AJAX actions globally using vanilla JS custom events
  document.addEventListener('click', function(e) {
    // Intercept ATC button clicks to log cart events
    var btn = e.target ? e.target.closest('[name="add"], .js_add_to_cart_button, .js-product-button-add-to-cart, .add-to-cart, .fd-btn--atc, .smart-upsell-add-btn, .ajax_add_to_cart, .cpg-atc-btn') : null;
    if (btn) {
      // Delay slightly to allow cart response to come back
      setTimeout(function() {
        fetch('/cart.js')
          .then(function(res) { return res.json(); })
          .then(function(cart) {
            if (cart && cart.items && cart.items.length) {
              var latest = cart.items[0];
              trackCartEvent('add_to_cart', {
                title: latest.title || latest.product_title,
                variant_id: latest.variant_id,
                product_id: latest.product_id,
                quantity: latest.quantity || 1,
                price: latest.price ? (latest.price / 100).toFixed(2) : ''
              });
            }
          }).catch(function() {});
      }, 800);
    }
  }, true);

})();

