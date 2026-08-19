/* Smart Cart JS - Interactive functionality for coupons, suggestions, and note accordion */

(function($) {
  'use strict';

  function initSmartCart() {
    // Modal reparenting: Move #smart-id-modal to <body> level once so it's not
    // clipped/transformed inside the cart drawer. On subsequent re-inits (cart updates),
    // sync the fresh data-* attributes from the newly rendered drawer modal into the
    // body-level one, then remove the stale drawer copy.
    var $bodyModal = $('body > #smart-id-modal[data-appended]');
    var $drawerModal = $('#smart-id-modal').not('[data-appended]');

    if ($drawerModal.length) {
      if ($bodyModal.length) {
        // Already have a body-level modal — just sync fresh customer data attributes
        $bodyModal.attr({
          'data-has-customer': $drawerModal.attr('data-has-customer'),
          'data-cust-name': $drawerModal.attr('data-cust-name'),
          'data-cust-phone': $drawerModal.attr('data-cust-phone'),
          'data-cust-address': $drawerModal.attr('data-cust-address'),
          'data-cust-city': $drawerModal.attr('data-cust-city'),
          'data-cust-state': $drawerModal.attr('data-cust-state'),
          'data-cust-zip': $drawerModal.attr('data-cust-zip')
        });
        $drawerModal.remove(); // Remove the redundant in-drawer copy
      } else {
        // First time: move modal from drawer to body
        $drawerModal.appendTo('body').attr('data-appended', 'true');
      }
    }
    
    // Global state variables for address editing and tracking
    var editingAddressId = null;
    var currentPhoneKey = null;

    function getBackendBaseUrl() {
      if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        return 'http://localhost:3000';
      }
      return (window.SmartCheckoutConfig && window.SmartCheckoutConfig.backendUrl)
        ? window.SmartCheckoutConfig.backendUrl
        : 'https://whatsapp.arhamtechnology.com';
    }

    // Helper functions for masking and address formatting
    function maskPhone(phone) {
      if (!phone) return '';
      var clean = phone.replace(/\D/g, '');
      if (clean.length >= 10) {
        var last10 = clean.slice(-10);
        return '+91 ' + last10.substring(0, 2) + 'XXX XXX' + last10.substring(8);
      }
      return phone;
    }

    function maskEmail(email) {
      if (!email) return '';
      var parts = email.split('@');
      if (parts.length === 2) {
        var name = parts[0];
        var domain = parts[1];
        if (name.length > 3) {
          return name.substring(0, 3) + '***@' + domain;
        } else {
          return name + '***@' + domain;
        }
      }
      return email;
    }

    function formatFullAddressString(addr) {
      var fullAddress = addr.addressLine;
      if (addr.city) fullAddress += ', ' + addr.city;
      if (addr.state) fullAddress += ', ' + addr.state;
      if (addr.pincode) fullAddress += ' - ' + addr.pincode;
      return fullAddress;
    }

    function escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
    }

    function fetchCartSummaryForStep(prefix) {
      return fetch('/cart.js')
        .then(function(res) { return res.json(); })
        .then(function(cart) {
          var formattedPrice = '₹' + (cart.total_price / 100).toFixed(2);
          $('#' + prefix + '-header-total').text(formattedPrice);
          $('#' + prefix + '-summary-count').text(cart.item_count + (cart.item_count === 1 ? ' item' : ' items'));

          var itemsHtml = '';
          $.each(cart.items, function(idx, item) {
            itemsHtml += '<div class="smart-checkout-item-row">' +
              '<div class="smart-checkout-item-left">' +
                '<img src="' + item.image + '" class="smart-checkout-item-img">' +
                '<div>' +
                  '<div class="smart-checkout-item-name">' + item.product_title + '</div>' +
                  '<div class="smart-checkout-item-qty">Qty: ' + item.quantity + '</div>' +
                '</div>' +
              '</div>' +
              '<div class="smart-checkout-item-price">₹' + (item.line_price / 100).toFixed(2) + '</div>' +
            '</div>';
          });
          $('#' + prefix + '-summary-items').html(itemsHtml);
        });
    }

    function showModalAddressesState(phone, addresses) {
      currentPhoneKey = phone;
      $('#smart-addresses-logged-phone').text('+91 ' + phone);

      // Fetch dynamic cart summary
      fetchCartSummaryForStep('smart-addresses');

      // Sync stored coupon
      var storedDiscount = localStorage.getItem('storedDiscount');
      if (storedDiscount) {
        $('#smart-addresses-coupon-input').val(storedDiscount);
      }

      // Render cards
      renderAddressCards(addresses);

      // Show Nudge badge
      var count = addresses.length;
      var $badge = $('#smart-addresses-badge-nudge');
      $badge.text(count + ' saved').fadeIn(200);
      setTimeout(function() {
        $badge.fadeOut(500);
      }, 3000);

      // Hide other steps, show address selection
      $('#smart-id-modal-step-phone, #smart-id-modal-step-address, #smart-id-modal-step-checkout').hide().removeClass('active');
      $('#smart-id-modal-step-addresses').show().addClass('active');
    }

    function renderAddressCards(addresses) {
      addresses.sort(function(a, b) {
        return b.lastUsed - a.lastUsed;
      });

      var container = $('#smart-addresses-list-container');
      container.empty();

      $.each(addresses, function(idx, addr) {
        var isSelected = (idx === 0);
        var cardClass = isSelected ? 'smart-address-card selected' : 'smart-address-card unselected';
        var maskedPhone = maskPhone(addr.phone);
        var maskedEmail = addr.email ? maskEmail(addr.email) : '';
        
        var cardHtml = '<div class="' + cardClass + '" data-id="' + addr.id + '">' +
          '<div class="smart-address-card-header">' +
            '<span class="smart-address-card-title">' + escapeHtml(addr.name) + ' (' + escapeHtml(addr.label || ('Address ' + (idx + 1))) + ')</span>' +
            '<span class="smart-address-card-edit" data-id="' + addr.id + '">Edit</span>' +
          '</div>' +
          '<div class="smart-address-card-details">';
          
        if (maskedPhone) {
          cardHtml += '<div class="smart-address-card-phone"><i class="fa fa-phone"></i> ' + maskedPhone + '</div>';
        }
        if (maskedEmail) {
          cardHtml += '<div class="smart-address-card-email"><i class="fa fa-envelope"></i> ' + maskedEmail + '</div>';
        }
        
        var fullAddrLine = formatFullAddressString(addr);
        cardHtml += '<div class="smart-address-card-line"><i class="fa fa-map-marker"></i> ' + escapeHtml(fullAddrLine) + '</div>' +
          '</div>' +
        '</div>';
        
        container.append(cardHtml);
      });
    }

    // 1. Accordion Toggle for Notes
    $(document).off('click', '.smart-notes-toggle').on('click', '.smart-notes-toggle', function(e) {
      e.preventDefault();
      var $this = $(this);
      var $content = $this.siblings('.smart-notes-content');
      $this.toggleClass('open');
      $content.slideToggle(200);
    });

    // 2. Save Notes
    $(document).off('click', '.smart-note-save-btn').on('click', '.smart-note-save-btn', function(e) {
      e.preventDefault();
      var $btn = $(this);
      var note = $btn.siblings('.smart-note-input').val();
      $btn.text('Saving...');

      var updateUrl = (window.routes && window.routes.cart_update_url) ? window.routes.cart_update_url : '/cart/update.js';

      fetch(updateUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ note: note })
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        $btn.text('Saved!');
        setTimeout(function() { $btn.text('Save Note'); }, 2000);
      })
      .catch(function(err) {
        $btn.text('Error');
        setTimeout(function() { $btn.text('Save Note'); }, 2000);
      });
    });

    // 3. Upsell Selector change
    $(document).off('change', '.smart-upsell-variant-select').on('change', '.smart-upsell-variant-select', function() {
      var $select = $(this);
      var variantId = $select.val();
      var $selectedOption = $select.find('option:selected');
      var price = $selectedOption.attr('data-price');
      
      var $item = $select.closest('.smart-upsell-item');
      $item.find('.smart-upsell-add-btn').attr('data-variant-id', variantId);
      if (price) {
        $item.find('.smart-upsell-price').text(price);
      }
    });

    // 4. Add Suggestion / Upsell Item
    $(document).off('click', '.smart-upsell-add-btn').on('click', '.smart-upsell-add-btn', function(e) {
      e.preventDefault();
      var $btn = $(this);
      var variantId = $btn.attr('data-variant-id');
      if (!variantId) return;

      $btn.text('Adding...');
      $btn.prop('disabled', true);

      var addUrl = (window.routes && window.routes.cart_add_url) ? window.routes.cart_add_url : '/cart/add.js';
      if (!addUrl.endsWith('.js')) {
        addUrl += '.js';
      }

      fetch(addUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          items: [{ id: parseInt(variantId), quantity: 1 }]
        })
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        $btn.text('Added');
        // Trigger standard theme minicart reload
        $('body').trigger('update:miniCart');
      })
      .catch(function(err) {
        $btn.text('Add');
        $btn.prop('disabled', false);
      });
    });

    // 5. Coupon selection (TAP TO APPLY)
    $(document).off('click', '.smart-coupon-card.unlocked').on('click', '.smart-coupon-card.unlocked', function(e) {
      var code = $(this).attr('data-code');
      applyCoupon(code);
    });

    // 6. Manual Coupon Application
    $(document).off('click', '#smart-coupon-apply-btn').on('click', '#smart-coupon-apply-btn', function(e) {
      e.preventDefault();
      var code = $('#smart-coupon-input').val().trim();
      if (code) {
        applyCoupon(code);
      }
    });

    function applyCoupon(code) {
      var $applyBtn = $('#smart-coupon-apply-btn');
      var originalBtnText = $applyBtn.text();
      $applyBtn.text('Applying...');

      localStorage.setItem('storedDiscount', code);

      var shopifyRoot = (window.Shopify && window.Shopify.routes && window.Shopify.routes.root) ? window.Shopify.routes.root : '/';
      var discountUrl = shopifyRoot + 'discount/' + code;

      fetch(discountUrl)
      .then(function() {
        $applyBtn.text(originalBtnText);
        // Visual updates
        $('.smart-coupon-card').removeClass('applied');
        $('.smart-coupon-card[data-code="' + code + '"]').addClass('applied');
        $('#smart-coupon-input').val(code);

        // Update checkout link
        updateCheckoutLink(code);

        // Refresh cart contents
        $('body').trigger('update:miniCart');
      })
      .catch(function(err) {
        $applyBtn.text('Error');
        setTimeout(function() { $applyBtn.text(originalBtnText); }, 2000);
      });
    }

    function updateCheckoutLink(code) {
      var $checkoutBtn = $('.smart-checkout-btn');
      if ($checkoutBtn.length && code) {
        var baseHref = $checkoutBtn.attr('href').split('?')[0];
        $checkoutBtn.attr('href', baseHref + '?discount=' + code);
      }
    }

    function syncDiscountState() {
      var $progress = $('.smart-progress-section');
      if (!$progress.length) return;

      var currentTotal = parseFloat($progress.attr('data-cart-total')) || 0;
      var shopifyRoot = (window.Shopify && window.Shopify.routes && window.Shopify.routes.root) ? window.Shopify.routes.root : '/';

      // 1. Auto apply the best coupon if needed
      var bestCoupon = null;
      var maxDiscount = 0;

      $('.smart-coupon-card').each(function() {
        var code = $(this).attr('data-code');
        var min = parseFloat($(this).attr('data-min')) || 0;
        var type = $(this).attr('data-type') || 'flat';
        var value = parseFloat($(this).attr('data-value')) || 0;

        if (currentTotal >= min) {
          var discount = type === 'percentage' ? (currentTotal * value) / 100 : value;
          if (discount > maxDiscount) {
            maxDiscount = discount;
            bestCoupon = { code: code, discount: discount, type: type, value: value };
          }
        }
      });

      var storedDiscount = localStorage.getItem('storedDiscount');

      if (bestCoupon) {
        if (storedDiscount !== bestCoupon.code) {
          console.log('[smart-cart] Auto-applying best coupon:', bestCoupon.code);
          localStorage.setItem('storedDiscount', bestCoupon.code);
          fetch(shopifyRoot + 'discount/' + bestCoupon.code)
            .then(function() {
              $('body').trigger('update:miniCart');
            });
          return;
        }
      } else {
        if (storedDiscount) {
          // If the stored discount is one of our cards but now locked, clear it
          var isOurCoupon = false;
          $('.smart-coupon-card').each(function() {
            if ($(this).attr('data-code') === storedDiscount) isOurCoupon = true;
          });
          if (isOurCoupon) {
            console.log('[smart-cart] Removing locked coupon:', storedDiscount);
            localStorage.removeItem('storedDiscount');
            fetch(shopifyRoot + 'discount/CLEAR')
              .then(function() {
                $('body').trigger('update:miniCart');
              });
            return;
          }
        }
      }

      // 2. Visual representation of applied coupon
      storedDiscount = localStorage.getItem('storedDiscount');
      $('.smart-coupon-card').removeClass('applied');
      
      if (storedDiscount) {
        $('#smart-coupon-input').val(storedDiscount);
        var $appliedCard = $('.smart-coupon-card[data-code="' + storedDiscount + '"]');
        if ($appliedCard.length) {
          $appliedCard.addClass('applied');
          $appliedCard.find('.smart-coupon-status').html('Applied <i class="fa fa-check"></i>');
          
          // Calculate discount details
          var type = $appliedCard.attr('data-type') || 'flat';
          var val = parseFloat($appliedCard.attr('data-value')) || 0;
          var discountAmount = type === 'percentage' ? (currentTotal * val) / 100 : val;
          
          // Show discount line in pricing breakdown
          $('.js-applied-coupon-code').text(storedDiscount);
          $('.js-applied-coupon-amount').text('-₹' + discountAmount.toFixed(2));
          $('.smart-coupon-discount-info').css('display', 'flex');
          
          // Update subtotal display
          $('.js-original-subtotal').text('₹' + currentTotal.toFixed(2)).show();
          var finalSubtotal = currentTotal - discountAmount;
          $('.js-total-price').text('₹' + finalSubtotal.toFixed(2));
        } else {
          // A custom code entered by user
          $('.smart-coupon-discount-info').hide();
          $('.js-original-subtotal').hide();
        }
        updateCheckoutLink(storedDiscount);
      } else {
        $('#smart-coupon-input').val('');
        $('.smart-coupon-discount-info').hide();
        $('.js-original-subtotal').hide();
      }

      // 3. Delivery status display
      var m1_val = parseFloat($progress.attr('data-m1-val')) || 599;
      if (currentTotal >= m1_val) {
        $('.js-delivery-status').text('FREE').css('color', '#2e7d32');
      } else {
        $('.js-delivery-status').text('₹50.00').css('color', '#666');
      }
    }

    syncDiscountState();

    // 7. Identity Network Interactive Flow
    // (OTP verification has been removed as per requested flow)

    // 8. Open Modal when Buy Now is clicked (disabled to let Razorpay Magic Checkout handle standard checkout form submission)
    /*
    $(document).off('click', '#smart-cart-buy-now').on('click', '#smart-cart-buy-now', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      // Re-sync modal data-attributes from minicart if modal was already moved to body
      // (Since it's reparented, we need to pull fresh customer data from the drawer's original modal)
      var $bodyModal = $('body > #smart-id-modal[data-appended]');
      var $drawerModal = $('#smart-id-modal').not('[data-appended]');
      var $modal = $bodyModal;

      if ($drawerModal.length) {
        if ($bodyModal.length) {
          // Already have a body-level modal — just sync fresh customer data attributes
          $bodyModal.attr({
            'data-has-customer': $drawerModal.attr('data-has-customer'),
            'data-cust-name': $drawerModal.attr('data-cust-name'),
            'data-cust-phone': $drawerModal.attr('data-cust-phone'),
            'data-cust-address': $drawerModal.attr('data-cust-address'),
            'data-cust-city': $drawerModal.attr('data-cust-city'),
            'data-cust-state': $drawerModal.attr('data-cust-state'),
            'data-cust-zip': $drawerModal.attr('data-cust-zip')
          });
          $drawerModal.remove(); // Remove the redundant in-drawer copy
        } else {
          // First time: move modal from drawer to body
          $drawerModal.appendTo('body').attr('data-appended', 'true');
          $modal = $drawerModal;
        }
      }

      if (!$modal.length) {
        $modal = $('#smart-id-modal');
      }

      var hasCustomer = $modal.attr('data-has-customer') === 'true';

      if (hasCustomer) {
        // Native Logged-in Shopify Customer!
        var custName = $modal.attr('data-cust-name') || 'Customer';
        var custPhone = $modal.attr('data-cust-phone') || 'Logged in';
        var custEmail = $modal.attr('data-cust-email') || '';
        var custAddress = $modal.attr('data-cust-address') || '';
        var custCity = $modal.attr('data-cust-city') || '';
        var custState = $modal.attr('data-cust-state') || '';
        var custZip = $modal.attr('data-cust-zip') || '';
 
        var fullAddress = custAddress;
        if (custCity) fullAddress += ', ' + custCity;
        if (custState) fullAddress += ', ' + custState;
        if (custZip) fullAddress += ' - ' + custZip;
 
        var userData = {
          name: custName,
          phone: custPhone,
          address: fullAddress
        };
 
        localStorage.setItem('smart_cart_user', JSON.stringify(userData));
        showModalCheckoutState(userData);

        if (window.VisitorTracker && typeof window.VisitorTracker.resolveIdentity === 'function') {
          window.VisitorTracker.resolveIdentity(custPhone !== 'Logged in' ? custPhone : '', custEmail, custName);
        }
        captureVisitorToWacrm(custPhone !== 'Logged in' ? custPhone : '', custEmail, custName);
      } else {
        var storedUser = localStorage.getItem('smart_cart_user');
        if (storedUser) {
          try {
            var userData = JSON.parse(storedUser);
            showModalCheckoutState(userData);
          } catch(err) {
            localStorage.removeItem('smart_cart_user');
            showModalPhoneState();
          }
        } else {
          showModalPhoneState();
        }
      }

      // Open Modal Overlay and lock page scroll
      $('body').addClass('smart-modal-open');
      $('#smart-id-modal').fadeIn(200);
    });
    */

    // Close Modal triggers
    $(document).off('click', '#smart-id-modal-close-btn').on('click', '#smart-id-modal-close-btn', function() {
      $('body').removeClass('smart-modal-open');
      $('#smart-id-modal').fadeOut(200);
    });

    // Close Modal on background click
    $(document).off('click', '#smart-id-modal').on('click', '#smart-id-modal', function(e) {
      if ($(e.target).hasClass('smart-id-modal-overlay')) {
        $('body').removeClass('smart-modal-open');
        $('#smart-id-modal').fadeOut(200);
      }
    });

    function showModalPhoneState() {
      $('#smart-id-modal-phone-input').val('');
      
      $('#smart-id-modal-step-checkout, #smart-id-modal-step-address, #smart-id-modal-step-addresses').hide().removeClass('active');
      $('#smart-id-modal-step-phone').show().addClass('active');
    }

    function showModalCheckoutState(userData) {
      $('#smart-checkout-preview-name').text(userData.name);
      $('#smart-checkout-preview-phone').text(userData.phone);
      $('#smart-checkout-preview-address').text(userData.address);
      $('#smart-checkout-logged-phone').text(userData.phone);

      // Fetch dynamic cart summary
      fetchCartSummaryForStep('smart-checkout');

      // Restore active discount state inside checkout if present
      var storedDiscount = localStorage.getItem('storedDiscount');
      if (storedDiscount) {
        $('#smart-checkout-coupon-input').val(storedDiscount);
      }

      // Ensure a visible payment option is active by default
      var $visibleOptions = $('.smart-checkout-payment-option:visible');
      if ($visibleOptions.length && !$('.smart-checkout-payment-option.active:visible').length) {
        $('.smart-checkout-payment-option').removeClass('active').find('input[type="radio"]').prop('checked', false);
        $visibleOptions.first().addClass('active').find('input[type="radio"]').prop('checked', true);
        $('.smart-checkout-method-details').hide();
        $visibleOptions.first().find('.smart-checkout-method-details').show();
      }

      // Initialize place order button text based on default active option
      var defaultMethod = $('.smart-checkout-payment-option.active').attr('data-method') || 'upi';
      if (defaultMethod === 'cod') {
        $('#smart-checkout-place-order').text('Place Order');
      } else {
        $('#smart-checkout-place-order').text('Pay Now');
      }

      $('#smart-id-modal-step-phone, #smart-id-modal-step-address, #smart-id-modal-step-addresses').hide().removeClass('active');
      $('#smart-id-modal-step-checkout').show().addClass('active');
    }

    function showModalAddressFormState(phone) {
      currentPhoneKey = phone;
      
      if (editingAddressId) {
        var savedAddressStr = localStorage.getItem('smart_address_' + phone);
        if (savedAddressStr) {
          try {
            var addresses = JSON.parse(savedAddressStr);
            var addr = addresses.find(function(a) { return a.id === editingAddressId; });
            if (addr) {
              $('#smart-id-form-name').val(addr.name);
              $('#smart-id-form-email').val(addr.email || '');
              $('#smart-id-form-label').val(addr.label || '');
              $('#smart-id-form-address').val(addr.addressLine);
              $('#smart-id-form-pincode').val(addr.pincode);
              $('#smart-id-form-city').val(addr.city);
              $('#smart-id-form-state').val(addr.state);
            }
          } catch(e) {
            console.error(e);
          }
        }
      } else {
        // Clear fields for a new entry
        $('#smart-id-form-name').val('');
        $('#smart-id-form-email').val('');
        $('#smart-id-form-label').val('');
        $('#smart-id-form-address').val('');
        $('#smart-id-form-pincode').val('');
        $('#smart-id-form-city').val('');
        $('#smart-id-form-state').val('');
      }

      $('#smart-id-modal-step-phone, #smart-id-modal-step-checkout, #smart-id-modal-step-addresses').hide().removeClass('active');
      $('#smart-id-modal-step-address').show().addClass('active');
    }

    // Clean input character formats
    $(document).off('input', '#smart-id-modal-phone-input').on('input', '#smart-id-modal-phone-input', function() {
      var clean = $(this).val().replace(/\D/g, '');
      $(this).val(clean);
    });

    function syncAttributesToShopify(userData, callback) {
      var updateUrl = (window.routes && window.routes.cart_update_url) ? window.routes.cart_update_url : '/cart/update.js';
      fetch(updateUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          attributes: {
            'Prefilled Name': userData.name,
            'Prefilled Phone': userData.phone,
            'Prefilled Address': userData.address
          }
        })
      })
      .then(function() {
        if (callback) callback();
      });
    }

    // ------------------------------------------------------------------
    // captureVisitorToWacrm
    // Fire-and-forget: upserts a Contact in the wacrm CRM every time the
    // visitor identifies themselves (phone modal, address save, or login).
    // ------------------------------------------------------------------
    function captureVisitorToWacrm(phone, email, name) {
      var cleanPhone = phone ? String(phone).replace(/\D/g, '').slice(-10) : '';
      if (!cleanPhone && !email) return; // nothing useful to send

      var backendUrl = getBackendBaseUrl() + '/api/shopify/capture-visitor';

      fetch(backendUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ phone: cleanPhone || null, email: email || null, name: name || null })
      }).catch(function() {
        // Silently ignore — never block the checkout flow
      });
    }

    function trackCheckout(userData) {
      fetch('/cart.js')
        .then(function(res) { return res.json(); })
        .then(function(cartData) {
          if (!cartData.items || !cartData.items.length) return;

          var lineItems = cartData.items.map(function(item) {
            return {
              title: item.title,
              price: (item.price / 100).toFixed(2),
              quantity: item.quantity,
              variant_id: item.variant_id,
              product_id: item.product_id
            };
          });

          var name = userData.name || 'Customer';
          var phone = userData.phone || '';
          var email = userData.email || '';
          
          var backendUrl = getBackendBaseUrl() + '/api/shopify/track-checkout';

          fetch(backendUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            body: JSON.stringify({
              cart_token: cartData.token,
              name: name,
              phone: phone,
              email: email,
              address: userData.address || '',
              total_price: (cartData.total_price / 100).toFixed(2),
              currency: cartData.currency,
              line_items: lineItems
            })
          }).catch(function(err) {
            console.warn('[wacrm-checkout-tracker] failed to track checkout:', err);
          });
        }).catch(function(err) {
          console.warn('[wacrm-checkout-tracker] failed to get cart for tracking:', err);
        });
    }

    // Step 1: Handle Mobile Submission (Verify & Route directly)
    $(document).off('click', '#smart-id-modal-submit-phone').on('click', '#smart-id-modal-submit-phone', function(e) {
      e.preventDefault();
      var phone = $('#smart-id-modal-phone-input').val().replace(/\D/g, '');
      if (phone.length < 10) {
        alert('Please enter a valid 10-digit phone number.');
        return;
      }

      var $btn = $(this);
      var originalBtnText = $btn.text();
      $btn.text('Checking...').prop('disabled', true);

      // Simulate a fast check delay (600ms) for premium feel
      setTimeout(function() {
        $btn.text(originalBtnText).prop('disabled', false);
        currentPhoneKey = phone;

        if (window.VisitorTracker && typeof window.VisitorTracker.resolveIdentity === 'function') {
          window.VisitorTracker.resolveIdentity(phone, null, null);
        }
        captureVisitorToWacrm(phone, null, null);

        var savedAddressStr = localStorage.getItem('smart_address_' + phone);
        var addresses = [];
        if (savedAddressStr) {
          try {
            var parsed = JSON.parse(savedAddressStr);
            if (Array.isArray(parsed)) {
              addresses = parsed;
            } else if (typeof parsed === 'object' && parsed !== null) {
              // Convert legacy single-object format to array
              parsed.id = parsed.id || 'addr_legacy';
              parsed.label = parsed.label || 'Address 1';
              parsed.lastUsed = parsed.lastUsed || Date.now();
              addresses = [parsed];
              localStorage.setItem('smart_address_' + phone, JSON.stringify(addresses));
            }
          } catch(err) {
            addresses = [];
          }
        }

        if (addresses.length === 0) {
          // Route to Address Capture Form
          showModalAddressFormState(phone);
        } else if (addresses.length === 1) {
          // Exactly one address: auto-select and proceed to checkout
          var singleAddr = addresses[0];
          singleAddr.lastUsed = Date.now(); // update timestamp
          localStorage.setItem('smart_address_' + phone, JSON.stringify(addresses));

          var userData = {
            id: singleAddr.id,
            name: singleAddr.name,
            phone: phone,
            email: singleAddr.email,
            address: formatFullAddressString(singleAddr)
          };
          localStorage.setItem('smart_cart_user', JSON.stringify(userData));
          showModalCheckoutState(userData);
          syncAttributesToShopify(userData);
          trackCheckout(userData);
        } else {
          // Two or more addresses: show Address Selection screen
          showModalAddressesState(phone, addresses);
        }
      }, 600);
    });

    // Auto-fetch City/State on 6-digit Pincode input
    $(document).off('input', '#smart-id-form-pincode').on('input', '#smart-id-form-pincode', function() {
      var pincode = $(this).val().replace(/\D/g, '');
      $(this).val(pincode);

      var $status = $('#smart-pincode-status');
      var $city = $('#smart-id-form-city');
      var $state = $('#smart-id-form-state');

      if (pincode.length === 6) {
        $status.removeClass('success error').addClass('loading').text('Fetching City/State...').show();
        $city.val('');
        $state.val('');

        fetch('https://api.postalpincode.in/pincode/' + pincode)
          .then(function(res) { return res.json(); })
          .then(function(data) {
            if (data && data[0] && data[0].Status === 'Success' && data[0].PostOffice && data[0].PostOffice.length) {
              var info = data[0].PostOffice[0];
              var cityVal = info.District;
              var stateVal = info.State;

              $city.val(cityVal);
              
              // Find matching state (case-insensitive)
              $state.find('option').each(function() {
                if ($(this).val().toLowerCase() === stateVal.toLowerCase() || $(this).text().toLowerCase() === stateVal.toLowerCase()) {
                  $state.val($(this).val());
                  return false;
                }
              });

              $status.removeClass('loading error').addClass('success').text('Pincode verified successfully!').show();
            } else {
              $status.removeClass('loading success').addClass('error').text('Invalid Pincode. Please enter correct code.').show();
              $city.val('');
              $state.val('');
            }
          })
          .catch(function() {
            $status.removeClass('loading success').addClass('error').text('Connection error. Please select City/State manually.').show();
          });
      } else {
        $status.hide();
      }
    });

    // Step 4: Handle Address Form Submission
    $(document).off('click', '#smart-id-modal-save-address').on('click', '#smart-id-modal-save-address', function(e) {
      e.preventDefault();
      
      var name = $('#smart-id-form-name').val().trim();
      var emailInput = $('#smart-id-form-email').val().trim();
      var labelInput = $('#smart-id-form-label').val().trim();
      var addressLine = $('#smart-id-form-address').val().trim();
      var pincode = $('#smart-id-form-pincode').val().replace(/\D/g, '');
      var city = $('#smart-id-form-city').val().trim();
      var state = $('#smart-id-form-state').val().trim();

      if (!name || !addressLine || !pincode || !city || !state) {
        alert('Please fill out all address details.');
        return;
      }
      if (pincode.length < 6) {
        alert('Please enter a valid 6-digit Pincode.');
        return;
      }
      // Optional email validation
      if (emailInput && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput)) {
        alert('Please enter a valid email address, or leave it blank.');
        return;
      }

      var phone = currentPhoneKey || $('#smart-id-modal-phone-input').val().replace(/\D/g, '');
      if (!phone) {
        var storedUser = localStorage.getItem('smart_cart_user');
        if (storedUser) {
          phone = JSON.parse(storedUser).phone.replace(/\D/g, '');
          if (phone.length > 10) phone = phone.slice(-10);
        }
      }
      if (!phone) phone = '9876543210';

      // 1. Get existing address array
      var savedAddressStr = localStorage.getItem('smart_address_' + phone);
      var addresses = [];
      if (savedAddressStr) {
        try {
          var parsed = JSON.parse(savedAddressStr);
          if (Array.isArray(parsed)) {
            addresses = parsed;
          } else if (typeof parsed === 'object' && parsed !== null) {
            parsed.id = parsed.id || 'addr_legacy';
            parsed.label = parsed.label || 'Address 1';
            parsed.lastUsed = parsed.lastUsed || Date.now();
            addresses = [parsed];
          }
        } catch(err) {
          addresses = [];
        }
      }

      // 2. Prepare new address object
      var id = editingAddressId || 'addr_' + Date.now();
      var finalLabel = labelInput || ('Address ' + (addresses.length + 1));
      
      var newAddr = {
        id: id,
        label: finalLabel,
        name: name,
        phone: phone,
        email: emailInput || '',
        addressLine: addressLine,
        city: city,
        state: state,
        pincode: pincode,
        lastUsed: Date.now()
      };

      // 3. Check for duplicates (match name, addressLine, city, state, pincode)
      var duplicateIndex = addresses.findIndex(function(addr) {
        return addr.id !== editingAddressId && // don't match with self when editing
               addr.name.toLowerCase() === newAddr.name.toLowerCase() &&
               addr.addressLine.toLowerCase() === newAddr.addressLine.toLowerCase() &&
               addr.city.toLowerCase() === newAddr.city.toLowerCase() &&
               addr.state.toLowerCase() === newAddr.state.toLowerCase() &&
               addr.pincode === newAddr.pincode;
      });

      if (duplicateIndex > -1) {
        // Update duplicate entry's lastUsed
        addresses[duplicateIndex].lastUsed = Date.now();
        addresses[duplicateIndex].email = newAddr.email;
        if (editingAddressId) {
          // If we edited an entry and it became a duplicate of another entry, remove the edited entry to avoid duplication
          addresses = addresses.filter(function(addr) { return addr.id !== editingAddressId; });
        }
        newAddr = addresses[duplicateIndex];
      } else {
        if (editingAddressId) {
          // Update existing
          var editIdx = addresses.findIndex(function(addr) { return addr.id === editingAddressId; });
          if (editIdx > -1) {
            addresses[editIdx] = newAddr;
          } else {
            addresses.push(newAddr);
          }
        } else {
          // Add new
          addresses.push(newAddr);
        }
      }

      // Cap at 5 saved addresses, drop oldest by lastUsed
      addresses.sort(function(a, b) { return b.lastUsed - a.lastUsed; });
      if (addresses.length > 5) {
        addresses = addresses.slice(0, 5);
      }

      // Save back to localStorage
      localStorage.setItem('smart_address_' + phone, JSON.stringify(addresses));

      var formattedPhone = '+91 ' + phone.substring(0, 5) + ' ' + phone.substring(5);
      var userData = {
        id: newAddr.id,
        name: newAddr.name,
        phone: formattedPhone,
        email: newAddr.email || '',
        address: formatFullAddressString(newAddr)
      };

      // Mark as current logged-in user session
      localStorage.setItem('smart_cart_user', JSON.stringify(userData));

      if (window.VisitorTracker && typeof window.VisitorTracker.resolveIdentity === 'function') {
        window.VisitorTracker.resolveIdentity(phone, userData.email, userData.name);
      }
      captureVisitorToWacrm(phone, userData.email, userData.name);

      var $btn = $(this);
      $btn.text('Saving...').prop('disabled', true);

      // Save attributes and proceed to checkout step
      syncAttributesToShopify(userData, function() {
        $btn.text('Save & Continue').prop('disabled', false);
        editingAddressId = null; // reset edit state
        showModalCheckoutState(userData);
        trackCheckout(userData);
      });
    });

    // Step 3 Checkout Toggles & Controllers
    
    // Collapsible Order Summary Table
    $(document).off('click', '#smart-checkout-summary-toggle').on('click', '#smart-checkout-summary-toggle', function(e) {
      e.preventDefault();
      var $items = $('#smart-checkout-summary-items');
      var $icon = $(this).find('i');
      
      $items.slideToggle(200);
      if ($icon.hasClass('fa-chevron-down')) {
        $icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
      } else {
        $icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
      }
    });

    // Edit Address Trigger
    $(document).off('click', '#smart-checkout-edit-address').on('click', '#smart-checkout-edit-address', function(e) {
      e.preventDefault();
      var phone = currentPhoneKey || $('#smart-id-modal-phone-input').val().replace(/\D/g, '');
      if (!phone) {
        var storedUser = localStorage.getItem('smart_cart_user');
        if (storedUser) {
          try {
            phone = JSON.parse(storedUser).phone.replace(/\D/g, '');
            if (phone.length > 10) phone = phone.slice(-10);
          } catch(err) {}
        }
      }
      if (phone) {
        var savedAddressStr = localStorage.getItem('smart_address_' + phone);
        if (savedAddressStr) {
          try {
            var addresses = JSON.parse(savedAddressStr);
            if (Array.isArray(addresses) && addresses.length >= 1) {
              showModalAddressesState(phone, addresses);
              return;
            }
          } catch(err) {}
        }
      }
      showModalAddressFormState(phone);
    });

    // Back to Addresses Selection or Phone Number entry
    $(document).off('click', '#smart-checkout-back-btn').on('click', '#smart-checkout-back-btn', function(e) {
      e.preventDefault();
      var phone = currentPhoneKey || $('#smart-id-modal-phone-input').val().replace(/\D/g, '');
      if (!phone) {
        var storedUser = localStorage.getItem('smart_cart_user');
        if (storedUser) {
          try {
            phone = JSON.parse(storedUser).phone.replace(/\D/g, '');
            if (phone.length > 10) phone = phone.slice(-10);
          } catch(err) {}
        }
      }
      if (phone) {
        var savedAddressStr = localStorage.getItem('smart_address_' + phone);
        if (savedAddressStr) {
          try {
            var addresses = JSON.parse(savedAddressStr);
            if (Array.isArray(addresses) && addresses.length >= 1) {
              showModalAddressesState(phone, addresses);
              return;
            }
          } catch(err) {}
        }
      }
      showModalPhoneState();
    });

    // Back to Phone Number from Addresses Selection
    $(document).off('click', '#smart-addresses-back-btn').on('click', '#smart-addresses-back-btn', function(e) {
      e.preventDefault();
      showModalPhoneState();
    });

    // Collapsible Order Summary Table inside Addresses Selection
    $(document).off('click', '#smart-addresses-summary-toggle').on('click', '#smart-addresses-summary-toggle', function(e) {
      e.preventDefault();
      var $items = $('#smart-addresses-summary-items');
      var $icon = $(this).find('i');
      
      $items.slideToggle(200);
      if ($icon.hasClass('fa-chevron-down')) {
        $icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
      } else {
        $icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
      }
    });

    // Apply Coupon Code inside Addresses Selection
    $(document).off('click', '#smart-addresses-coupon-apply').on('click', '#smart-addresses-coupon-apply', function(e) {
      e.preventDefault();
      var code = $('#smart-addresses-coupon-input').val().trim();
      if (!code) {
        alert('Please enter a coupon code.');
        return;
      }
      
      var $btn = $(this);
      $btn.text('Applying...').prop('disabled', true);

      setTimeout(function() {
        $btn.text('Apply').prop('disabled', false);
        localStorage.setItem('storedDiscount', code);
        
        // Populate coupon field in other steps
        $('#smart-coupon-input').val(code);
        $('#smart-checkout-coupon-input').val(code);
        $('.smart-coupon-card').removeClass('applied');
        $('.smart-coupon-card[data-code="' + code + '"]').addClass('applied');

        alert('Coupon ' + code + ' applied successfully!');
      }, 500);
    });

    // Add Address Button from selection screen
    $(document).off('click', '#smart-addresses-add-btn').on('click', '#smart-addresses-add-btn', function(e) {
      e.preventDefault();
      editingAddressId = null;
      showModalAddressFormState(currentPhoneKey);
    });

    // Edit Address Link from cards
    $(document).off('click', '.smart-address-card-edit').on('click', '.smart-address-card-edit', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var addrId = $(this).attr('data-id');
      editingAddressId = addrId;
      showModalAddressFormState(currentPhoneKey);
    });

    // Card Selection click trigger
    $(document).off('click', '.smart-address-card').on('click', '.smart-address-card', function(e) {
      if ($(e.target).hasClass('smart-address-card-edit')) return;
      $('.smart-address-card').removeClass('selected').addClass('unselected');
      $(this).removeClass('unselected').addClass('selected');
    });

    // Proceed Button click trigger from selection screen
    $(document).off('click', '#smart-addresses-proceed-btn').on('click', '#smart-addresses-proceed-btn', function(e) {
      e.preventDefault();
      var $selectedCard = $('.smart-address-card.selected');
      if (!$selectedCard.length) {
        alert('Please select or add an address to proceed.');
        return;
      }
      
      var addrId = $selectedCard.attr('data-id');
      var savedAddressStr = localStorage.getItem('smart_address_' + currentPhoneKey);
      if (savedAddressStr) {
        try {
          var addresses = JSON.parse(savedAddressStr);
          var selectedAddr = addresses.find(function(a) { return a.id === addrId; });
          if (selectedAddr) {
            selectedAddr.lastUsed = Date.now();
            localStorage.setItem('smart_address_' + currentPhoneKey, JSON.stringify(addresses));
            
            var userData = {
              id: selectedAddr.id,
              name: selectedAddr.name,
              phone: currentPhoneKey,
              email: selectedAddr.email,
              address: formatFullAddressString(selectedAddr)
            };
            
            localStorage.setItem('smart_cart_user', JSON.stringify(userData));
            syncAttributesToShopify(userData);
            trackCheckout(userData);
            showModalCheckoutState(userData);
          }
        } catch(err) {
          console.error(err);
        }
      }
    });

    // Apply Coupon Code inside Custom Checkout
    $(document).off('click', '#smart-checkout-coupon-apply').on('click', '#smart-checkout-coupon-apply', function(e) {
      e.preventDefault();
      var code = $('#smart-checkout-coupon-input').val().trim();
      if (!code) {
        alert('Please enter a coupon code.');
        return;
      }
      
      var $btn = $(this);
      $btn.text('Applying...').prop('disabled', true);

      setTimeout(function() {
        $btn.text('Apply').prop('disabled', false);
        localStorage.setItem('storedDiscount', code);
        
        // Populate coupon field in the drawer too
        $('#smart-coupon-input').val(code);
        $('.smart-coupon-card').removeClass('applied');
        $('.smart-coupon-card[data-code="' + code + '"]').addClass('applied');

        alert('Coupon ' + code + ' applied successfully!');
      }, 500);
    });

    // Payment Option Accordion Selection
    $(document).off('click', '.smart-checkout-payment-option').on('click', '.smart-checkout-payment-option', function(e) {
      // Avoid loops if clicking fields inside the active detail container
      if ($(e.target).closest('.smart-checkout-method-details').length) return;

      var $option = $(this);
      var method = $option.attr('data-method');
      
      $('.smart-checkout-payment-option').removeClass('active').find('input[type="radio"]').prop('checked', false);
      $option.addClass('active').find('input[type="radio"]').prop('checked', true);

      $('.smart-checkout-method-details').slideUp(200);
      $option.find('.smart-checkout-method-details').slideDown(200);

      // Update button text dynamically
      var $btn = $('#smart-checkout-place-order');
      if (method === 'cod') {
        $btn.text('Place Order');
      } else {
        $btn.text('Pay Now');
      }
    });

    // UPI Quick Tag suffixes
    $(document).off('click', '.quick-tag').on('click', '.quick-tag', function(e) {
      e.preventDefault();
      var suffix = $(this).attr('data-suffix');
      var $upiInput = $('#smart-checkout-upi-id');
      var val = $upiInput.val().split('@')[0];
      if (val) {
        $upiInput.val(val + suffix);
      } else {
        $upiInput.val(suffix);
      }
      $upiInput.focus();
    });

    // Format Card Expiry MM/YY
    $(document).off('input', '#smart-card-exp').on('input', '#smart-card-exp', function() {
      var val = $(this).val().replace(/\D/g, '');
      if (val.length >= 2) {
        $(this).val(val.substring(0, 2) + '/' + val.substring(2, 4));
      } else {
        $(this).val(val);
      }
    });

    // Format Card Number with space masking
    $(document).off('input', '#smart-card-num').on('input', '#smart-card-num', function() {
      var val = $(this).val().replace(/\D/g, '');
      var formatted = val.match(/.{1,4}/g);
      if (formatted) {
        $(this).val(formatted.join(' '));
      } else {
        $(this).val(val);
      }
    });

    // Logout
    $(document).off('click', '#smart-checkout-logout, #smart-addresses-logout').on('click', '#smart-checkout-logout, #smart-addresses-logout', function(e) {
      e.preventDefault();
      localStorage.removeItem('smart_cart_user');
      currentPhoneKey = null;
      editingAddressId = null;
      showModalPhoneState();
    });

    function verifyCashfreePayment(orderId) {
      var checkUrl = getBackendBaseUrl() + '/api/cashfree/order-status/' + orderId;

      var pollCount = 0;
      var maxPolls = 8;

      function poll() {
        fetch(checkUrl)
          .then(function(res) { return res.json(); })
          .then(function(data) {
            if (data.order_status === 'PAID') {
              // Success! Clear storefront cart and redirect to thank-you page
              fetch('/cart/clear.js', { method: 'POST' })
                .then(function() {
                  var returnUrl = getBackendBaseUrl() + '/checkout/return?order_id=' + orderId;
                  window.location.href = returnUrl;
                });
            } else if (data.order_status === 'FAILED') {
              alert('Payment failed or was cancelled. Please try again.');
              $('#smart-checkout-place-order').text('Pay Now').prop('disabled', false);
            } else {
              if (pollCount < maxPolls) {
                pollCount++;
                setTimeout(poll, 2000);
              } else {
                // Timeout, redirect to return page as fallback
                var returnUrl = getBackendBaseUrl() + '/checkout/return?order_id=' + orderId;
                window.location.href = returnUrl;
              }
            }
          })
          .catch(function(err) {
            console.warn('[cashfree-verify] status poll error:', err);
            if (pollCount < maxPolls) {
              pollCount++;
              setTimeout(poll, 2000);
            } else {
              var returnUrl = getBackendBaseUrl() + '/checkout/return?order_id=' + orderId;
              window.location.href = returnUrl;
            }
          });
      }

      poll();
    }

    // Place Order Submission
    $(document).off('click', '#smart-checkout-place-order').on('click', '#smart-checkout-place-order', function(e) {
      e.preventDefault();

      var $activeOption = $('.smart-checkout-payment-option.active');
      var method = $activeOption.attr('data-method');
      var $btn = $(this);

      // Read current user
      var storedUser = localStorage.getItem('smart_cart_user');
      var userData = storedUser ? JSON.parse(storedUser) : { name: 'Customer', phone: '', address: '' };

      // Parse shipping address parameters
      var name = userData.name || 'Customer';
      var phone = userData.phone || '';
      var addressLine = '';
      var city = '';
      var state = '';
      var pincode = '';

      if (userData.address) {
        var parts = userData.address.split(' - ');
        pincode = parts[1] || '';
        if (parts[0]) {
          var addrParts = parts[0].split(', ');
          state = addrParts.pop() || '';
          city = addrParts.pop() || '';
          addressLine = addrParts.join(', ') || '';
        }
      }

      if (method === 'cod') {
        $btn.text('Placing Order...').prop('disabled', true);
        var cartUpdateUrl = (window.routes && window.routes.cart_update_url) ? window.routes.cart_update_url : '/cart/update.js';
        
        // Sync payment attributes in Shopify
        fetch(cartUpdateUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            attributes: {
              'Prefilled Name': userData.name,
              'Prefilled Phone': userData.phone,
              'Prefilled Address': userData.address,
              'Payment Method': 'cod'
            }
          })
        })
        .then(function() {
          // Fetch current cart items to send to secure API
          return fetch('/cart.js')
            .then(function(res) { return res.json(); })
            .then(function(cartData) {
              if (!cartData.items || !cartData.items.length) {
                throw new Error('Your cart is empty.');
              }
              
              var lineItems = cartData.items.map(function(item) {
                return {
                  variant_id: item.variant_id,
                  quantity: item.quantity
                };
              });

              var backendUrl = getBackendBaseUrl() + '/api/shopify/create-order';

              // Post to Next.js API route to create draft order & complete it securely
              return fetch(backendUrl, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
                },
                body: JSON.stringify({
                  name: name,
                  phone: phone,
                  email: userData.email || '',
                  address: addressLine,
                  city: city,
                  state: state,
                  zip: pincode,
                  payment_method: 'cod',
                  discount_code: localStorage.getItem('storedDiscount') || '',
                  line_items: lineItems
                })
              });
            })
            .then(function(apiRes) {
              if (!apiRes.ok) {
                return apiRes.json().then(function(errData) {
                  throw new Error(errData.error || 'Server error creating order');
                }).catch(function() {
                  throw new Error('Failed to create order on server');
                });
              }
              return apiRes.json();
            })
            .then(function(resData) {
              if (resData.success && resData.order) {
                // Clear Shopify Cart
                return fetch('/cart/clear.js', { method: 'POST' })
                  .then(function() {
                    // Show custom success screen inside modal
                    $('#smart-success-order-name').text(resData.order.name || ('#' + resData.order.order_number));
                    $('#smart-success-name').text(name);
                    $('#smart-success-phone').text(phone);
                    $('#smart-success-address').text(userData.address);

                    $('.smart-id-modal-step').hide();
                    $('#smart-id-modal-step-success').show();

                    // Reset modal total/count UI
                    $('#smart-checkout-header-total').text('₹0.00');
                    $('#smart-checkout-summary-count').text('0 items');
                    $('#smart-checkout-summary-items').html('<p style="padding:16px;text-align:center;color:#71717a;">Cart is empty</p>');

                    // Clear local discount
                    localStorage.removeItem('storedDiscount');
                    
                    // Trigger cart updates to sync UI
                    $(document).trigger('contentUpdated');
                  });
              } else {
                throw new Error(resData.error || 'Failed to place order.');
              }
            });
        })
        .catch(function(err) {
          console.error('Checkout error:', err);
          alert('Could not place order: ' + (err.message || 'Please check your connection and details.'));
        })
        .finally(function() {
          $btn.text('Place Order').prop('disabled', false);
        });

      } else {
        // Prepaid payments (Cashfree PG Integration)
        $btn.text('Initiating payment...').prop('disabled', true);

        // Fetch current cart items to send to secure API
        fetch('/cart.js')
          .then(function(res) { return res.json(); })
          .then(function(cartData) {
            if (!cartData.items || !cartData.items.length) {
              throw new Error('Your cart is empty.');
            }
            
            var lineItems = cartData.items.map(function(item) {
              return {
                variant_id: item.variant_id,
                quantity: item.quantity
              };
            });

            var cashfreeCreateUrl = getBackendBaseUrl() + '/api/cashfree/create-order';

            // Post to Next.js API route to create draft order & initiate Cashfree session
            return fetch(cashfreeCreateUrl, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              },
              body: JSON.stringify({
                cart_items: lineItems,
                customer: {
                  name: name,
                  email: userData.email || '',
                  phone: phone
                },
                shipping_address: {
                  address: addressLine,
                  city: city,
                  state: state,
                  zip: pincode
                },
                discount_code: localStorage.getItem('storedDiscount') || ''
              })
            });
          })
          .then(function(apiRes) {
            if (!apiRes.ok) {
              return apiRes.json().then(function(errData) {
                throw new Error(errData.error || 'Server error creating Cashfree order');
              }).catch(function() {
                throw new Error('Failed to create Cashfree order on server');
              });
            }
            return apiRes.json();
          })
          .then(function(resData) {
            if (resData.success && resData.payment_session_id) {
              var mode = 'sandbox';
              if (resData.environment) {
                mode = resData.environment.toLowerCase();
              } else {
                var isProd = (window.location.hostname.indexOf('divyaprabhafoods.com') > -1);
                mode = isProd ? 'production' : 'sandbox';
              }
              var cashfreeInstance = Cashfree({
                mode: mode
              });

              return cashfreeInstance.checkout({
                paymentSessionId: resData.payment_session_id,
                redirectTarget: '_modal'
              }).then(function() {
                $btn.text('Verifying...').prop('disabled', true);
                verifyCashfreePayment(resData.order_id);
              });
            } else {
              throw new Error(resData.error || 'Failed to retrieve payment session ID.');
            }
          })
          .catch(function(err) {
            console.error('Payment checkout error:', err);
            alert('Could not start payment: ' + (err.message || 'Please check your connection and try again.'));
            $btn.text('Pay Now').prop('disabled', false);
          });
      }
    });

    // Continue Shopping button click handler
    $(document).off('click', '#smart-success-continue-btn').on('click', '#smart-success-continue-btn', function(e) {
      e.preventDefault();
      $('body').removeClass('smart-modal-open');
      $('#smart-id-modal').fadeOut(200);
      window.location.href = '/';
    });

    function verifyCashfreePaymentFromUrl(orderId) {
      var checkUrl = getBackendBaseUrl() + '/api/cashfree/order-status/' + orderId;
      var pollCount = 0;
      var maxPolls = 10;

      function poll() {
        fetch(checkUrl)
          .then(function(res) { return res.json(); })
          .then(function(data) {
            if (data.order_status === 'PAID') {
              fetch('/cart/clear.js', { method: 'POST' })
                .finally(function() {
                  $('.smart-success-checkmark-circle').text('✓').css('background-color', '#22c55e');
                  $('#smart-success-order-name').text('#' + (data.shopify_order_number || orderId));
                  
                  if (data.customer) {
                    $('#smart-success-name').text(data.customer.name || 'Customer');
                    $('#smart-success-phone').text(data.customer.phone || '');
                  }
                  
                  if (data.shipping_address) {
                    var addr = data.shipping_address;
                    var addrStr = addr.address;
                    if (addr.city) addrStr += ', ' + addr.city;
                    if (addr.state) addrStr += ', ' + addr.state;
                    if (addr.zip) addrStr += ' - ' + addr.zip;
                    $('#smart-success-address').text(addrStr);
                  }
                  
                  $('#smart-id-modal-step-success .smart-id-modal-title').text('Order Confirmed!');
                  $('#smart-id-modal-step-success .smart-id-modal-subtitle').text('Thank you, your order has been placed successfully.');
                  
                  $('.smart-id-modal-step').hide().removeClass('active');
                  $('#smart-id-modal-step-success').show().addClass('active');

                  localStorage.removeItem('storedDiscount');
                  $(document).trigger('contentUpdated');

                  // Redirect to native Shopify thank you / order status page
                  setTimeout(function() {
                    if (data.order_status_url) {
                      window.location.href = data.order_status_url;
                    } else {
                      window.location.href = '/checkout/thank_you';
                    }
                  }, 2000);
                });
            } else if (data.order_status === 'FAILED') {
              $('.smart-success-checkmark-circle').text('✕').css('background-color', '#ef4444');
              $('#smart-id-modal-step-success .smart-id-modal-title').text('Payment Failed');
              $('#smart-id-modal-step-success .smart-id-modal-subtitle').text('The transaction failed or was cancelled.');
              $('#smart-success-order-name').text('Transaction Failed');
              $('#smart-success-name').text('Please close this modal and try checking out again.');
              $('#smart-success-phone').text('');
              $('#smart-success-address').text('');

              $('.smart-id-modal-step').hide().removeClass('active');
              $('#smart-id-modal-step-success').show().addClass('active');
            } else if (data.order_status === 'PROCESSING' || data.order_status === 'PENDING' || data.order_status === 'PAID_NOT_CONVERTED') {
              if (pollCount < maxPolls) {
                pollCount++;
                setTimeout(poll, 2500);
              } else {
                $('.smart-success-checkmark-circle').text('⌛').css('background-color', '#f59e0b');
                $('#smart-id-modal-step-success .smart-id-modal-title').text('Reconciling Payment');
                $('#smart-id-modal-step-success .smart-id-modal-subtitle').text('We are waiting for bank confirmation. Your order will be placed as soon as it clears.');
                $('#smart-success-order-name').text('Pending Confirmation');
                $('#smart-success-name').text('You can safely close this page. If payment succeeds, you will receive details via WhatsApp/SMS.');
                $('#smart-success-phone').text('');
                $('#smart-success-address').text('');

                $('.smart-id-modal-step').hide().removeClass('active');
                $('#smart-id-modal-step-success').show().addClass('active');
              }
            } else {
              if (pollCount < maxPolls) {
                pollCount++;
                setTimeout(poll, 2500);
              }
            }
          })
          .catch(function(err) {
            console.warn('[cashfree-url-verify] error:', err);
            if (pollCount < maxPolls) {
              pollCount++;
              setTimeout(poll, 2500);
            }
          });
      }

      poll();
    }

    var urlParams = new URLSearchParams(window.location.search);
    var cashfreeOrderId = urlParams.get('cashfree_order_id');
    if (cashfreeOrderId) {
      urlParams.delete('cashfree_order_id');
      var newUrl = window.location.pathname;
      if (urlParams.toString()) {
        newUrl += '?' + urlParams.toString();
      }
      window.history.replaceState({}, document.title, newUrl);

      $('body').addClass('smart-modal-open');
      $('#smart-id-modal').fadeIn(200);

      $('.smart-id-modal-step').hide().removeClass('active');
      $('#smart-id-modal-step-success').show().addClass('active');
      
      $('.smart-success-checkmark-circle').text('⌛').css('background-color', '#3b82f6');
      $('#smart-id-modal-step-success .smart-id-modal-title').text('Verifying Payment');
      $('#smart-id-modal-step-success .smart-id-modal-subtitle').text('Please wait while we verify your payment status with the bank...');
      $('#smart-success-order-name').text('Verifying Order...');
      $('#smart-success-name').text('Checking order details...');
      $('#smart-success-phone').text('');
      $('#smart-success-address').text('');

      verifyCashfreePaymentFromUrl(cashfreeOrderId);
    }

    checkMilestoneUnlock();
  }

  function checkMilestoneUnlock() {
    var $progress = $('.smart-progress-section');
    if (!$progress.length) {
      console.log('[smart-cart] progress section not found - cart is empty. Resetting milestones.');
      localStorage.setItem('smart_completed_milestones', JSON.stringify([]));
      return;
    }

    var currentTotal = parseFloat($progress.attr('data-cart-total')) || 0;
    var milestones = [
      { val: parseFloat($progress.attr('data-m1-val')) || 0, lbl: $progress.attr('data-m1-lbl') || 'Free Delivery' },
      { val: parseFloat($progress.attr('data-m2-val')) || 0, lbl: $progress.attr('data-m2-lbl') || 'Reward 1' },
      { val: parseFloat($progress.attr('data-m3-val')) || 0, lbl: $progress.attr('data-m3-lbl') || 'Reward 2' },
      { val: parseFloat($progress.attr('data-m4-val')) || 0, lbl: $progress.attr('data-m4-lbl') || 'Reward 3' }
    ];

    var currentCompleted = [];
    $.each(milestones, function(idx, m) {
      if (m.val > 0 && currentTotal >= m.val) {
        currentCompleted.push(m.lbl);
      }
    });

    console.log('[smart-cart] currentTotal:', currentTotal, 'currentCompleted:', currentCompleted);

    var storedStr = localStorage.getItem('smart_completed_milestones');
    var previousCompleted = [];
    if (storedStr) {
      try {
        previousCompleted = JSON.parse(storedStr);
      } catch(e) {
        previousCompleted = [];
      }
    }
    console.log('[smart-cart] previousCompleted:', previousCompleted);

    var justAdded = sessionStorage.getItem('just_added_to_cart') === 'true';
    console.log('[smart-cart] justAdded:', justAdded);

    if (justAdded) {
      if (currentCompleted.length > 0) {
        // Clear flag immediately to prevent double triggers
        sessionStorage.removeItem('just_added_to_cart');
        
        var targetMilestone = currentCompleted[currentCompleted.length - 1];
        console.log('[smart-cart] Triggering celebration for completed milestone:', targetMilestone);
        triggerMangoCelebration(targetMilestone);
      }
    }

    localStorage.setItem('smart_completed_milestones', JSON.stringify(currentCompleted));
  }

  function triggerMangoCelebration(milestoneName) {
    $('#smart-celebration-overlay').remove();

    var overlayHtml = '<div id="smart-celebration-overlay"></div>';
    $('body').append(overlayHtml);

    var $container = $('#smart-celebration-overlay');
    $container.show();

    var mangoCount = 12;
    for (var i = 0; i < mangoCount; i++) {
      spawnFallingMango($container);
    }

    setTimeout(function() {
      $container.fadeOut(500, function() {
        $(this).remove();
      });
    }, 4500);
  }

  function spawnFallingMango($container) {
    var left = Math.random() * 100;
    var size = 30 + Math.random() * 30;
    var delay = Math.random() * 2;
    var duration = 2 + Math.random() * 2.5;
    var rotation = Math.random() * 360;
    var rotateSpeed = -180 + Math.random() * 360;

    var mangoSvg = 
      '<svg class="falling-mango" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" ' +
           'style="left:' + left + '%; width:' + size + 'px; height:' + size + 'px; ' +
           'animation-delay:' + delay + 's; animation-duration:' + duration + 's; ' +
           '--start-rot:' + rotation + 'deg; --end-rot:' + (rotation + rotateSpeed) + 'deg;">' +
        '<path d="M50,12 C28,15 18,36 18,58 C18,78 32,88 48,87 C56,86 64,80 67,73 C71,64 74,48 71,32 C68,18 60,12 50,12 Z" fill="url(#mango-grad-fall)" />' +
        '<path d="M50,12 C48,6 42,4 40,1 C43,4 47,6 48,12 Z" fill="#2E431F" />' +
        '<path d="M48,12 C52,8 58,6 65,4 C58,8 52,10 48,12 Z" fill="#1A2B12" />' +
        '<defs>' +
          '<radialGradient id="mango-grad-fall" cx="40%" cy="40%" r="60%">' +
            '<stop offset="0%" stop-color="#C4D964" />' +
            '<stop offset="60%" stop-color="#79993C" />' +
            '<stop offset="100%" stop-color="#455A25" />' +
          '</radialGradient>' +
        '</defs>' +
      '</svg>';

    $container.append(mangoSvg);
  }

  $(document).ready(function() {
    initSmartCart();

    // Watch #js_cart_popup for dynamic HTML injections (e.g. homepage grid ATC)
    // Only run checkMilestoneUnlock — NOT initSmartCart — to avoid layout disruption
    var cosmeticsCart = document.getElementById('js_cart_popup');
    if (cosmeticsCart) {
      var milestoneCheckTimer = null;
      var observer = new MutationObserver(function() {
        // Debounce: wait until DOM mutations settle before checking
        clearTimeout(milestoneCheckTimer);
        milestoneCheckTimer = setTimeout(function() {
          checkMilestoneUnlock();
        }, 600);
      });
      observer.observe(cosmeticsCart, { childList: true, subtree: true });
    }
  });

  // Capture-phase click listener to set just_added_to_cart flag, bypassing stopPropagation()
  document.addEventListener('click', function(e) {
    var target = e.target;
    var atcButton = target.closest('form[action="/cart/add"] button, [name="add"], .js_add_to_cart_button, .js-product-button-add-to-cart, .add-to-cart, .fd-btn--atc, .smart-upsell-add-btn, .ajax_add_to_cart, .js_plus, .plus, .cpg-atc-btn');
    if (atcButton) {
      sessionStorage.setItem('just_added_to_cart', 'true');
      
      // Safety reset after 2 seconds in case no milestone is unlocked
      setTimeout(function() {
        sessionStorage.removeItem('just_added_to_cart');
      }, 2000);
    }
  }, true);

  // Re-run init after theme updates the minicart contents dynamically
  $(document).on('contentUpdated drawer:Minicart update:miniCart ajax:deleteCart ajax:addToCart cart:updated cartUpdated', function() {
    initSmartCart();
  });

  $(window).on('contentUpdated update:miniCart cart:updated cartUpdated', function() {
    initSmartCart();
  });

  // Native event listeners to handle CustomEvents from theme's native JS dispatchers
  document.addEventListener('contentUpdated', function() {
    initSmartCart();
  });
  document.addEventListener('drawer:Minicart', function() {
    initSmartCart();
  });

})(jQuery);
