# Shopify Codfirm Installation Instructions

Because browser automation is restricted from accessing the Shopify Admin dashboard directly for security reasons, you will need to manually apply these two optimizations in your Shopify checkout settings.

Here are the step-by-step instructions:

---

### Step 1: Make it Lightning Fast (Add Script)

1. Open your browser and navigate to your [Shopify Checkout Settings](https://admin.shopify.com/store/divyaprabhafoods/settings/checkout).
2. Scroll down to the **Order status page** section.
3. In the **Additional scripts** text box, copy and paste the following code at the **very top** (before any other scripts):

```html
<!-- Codfirm Starts -->
<script>
  (function () {
    if (!window.Shopify.checkout) return;
    document.body.style.opacity = 0;
    const scr = document.createElement("script");
    const head = document.head || document.getElementsByTagName("head")[0];
    scr.src = "https://app.codfirm.in/assets/embed.js";
    scr.async = false;
    head.insertBefore(scr, head.firstChild);
  })();
</script>
<!-- Codfirm Ends -->
```

---

### Step 2: Make Contact Number Compulsory

1. On the same [Shopify Checkout Settings](https://admin.shopify.com/store/divyaprabhafoods/settings/checkout) page:
2. Locate the **Customer contact method** or **Form options** section.
3. Under **Shipping address phone number** (or **Phone number**), select the **Required** option.

---

### Step 3: Save and Confirm

1. Click **Save** at the top right of the Shopify settings page.
2. Go back to the Cashfree CODFirm & Checkout app window:
   [Cashfree CODfirm Order Verification](https://admin.shopify.com/store/divyaprabhafoods/apps/cod-order-confirmation-2/order-verification)
3. Click the green **I've done this** button for both optimizations.
