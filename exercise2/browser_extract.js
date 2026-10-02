
(async () => {
  // Paste the product URLs from page1_urls.json between the brackets.
  const urls = [
    // "https://www.cellarbrations.com.au/.../product/...-id-555940",
  ];

  const results = [];
  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

  function extractProduct() {
    const descriptionElement = document.querySelector(
      '[data-testid="pdpDangerouslySetDecription-span-testId"]'
    );

    const parts = descriptionElement
      ? descriptionElement.innerHTML
          .split(/<br\s*\/?>/i)
          .map(html => {
            const temp = document.createElement("div");
            temp.innerHTML = html;
            return temp.innerText.trim();
          })
          .filter(Boolean)
      : [];

    const attributeIndex = parts.findIndex(text =>
      /^(Alcohol Volume|Pack Format|Standard Drinks|Pack Type|Country of Origin):/i.test(text)
    );

    const attributes = Object.fromEntries(
      parts.slice(attributeIndex < 0 ? parts.length : attributeIndex)
        .map(text => {
          const index = text.indexOf(":");
          return index < 0
            ? null
            : [text.slice(0, index).trim(), text.slice(index + 1).trim()];
        })
        .filter(Boolean)
    );

    return {
      product_id: location.pathname.match(/id-(\d+)/)?.[1] ?? null,
      product_url: location.href,
      description: parts.slice(
        0, attributeIndex < 0 ? parts.length : attributeIndex
      ).join(" "),
      attributes
    };
  }

  if (!urls.length) {
    console.error("Add product URLs to the urls array first.");
    return;
  }

  console.log("Ready to extract", urls.length, "products.");
  console.log("This script needs a navigation/resume mechanism before batch use.");
})();